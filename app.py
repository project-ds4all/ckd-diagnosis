import boto3
import botocore
import requests
import logging
import json
from flask import Flask, request, Response
import datetime as dt
from signalfx_tracing import auto_instrument, create_tracer, trace

import routes
import settings
from database.db import db, connection_uri
from schema.base_schema import ma
from schema.patient_log import PatientLogSchema
from schema.patient_request import PatientRequestSchema
from services.parks_data_storage import ParksDataStorage
from services.google_geocoder import Geocoder
from services.s3_service import S3Service
from services.ckd_analyzer import CKDAnalyzer
from services.json_formatter import JsonFormatter
from utils.api_utils import request_logger, failure

# APP init config
app = Flask(__name__)
app.config["DEBUG"] = settings.DEBUG
app.config["SQLALCHEMY_DATABASE_URI"] = connection_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = settings.PROPAGATE_EXCEPTIONS
app.config['SQLALCHEMY_POOL_RECYCLE'] = 120
db.init_app(app)
ma.init_app(app)

# Logs
logging_mode = logging.INFO
logging.basicConfig(format=settings.LOG_PATTERN, level=logging_mode)

# Global services
if settings.LOCAL:
    logging.info(f'val-self-onboarding logger loading s3 client on local environment')
    client = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          config=botocore.config.Config(connect_timeout=5, retries={'max_attempts': 1}))
else:
    logging.info(f'val-self-onboarding logger loading s3 client on {settings.ENV} environment')
    client = boto3.client('s3',
                          config=botocore.config.Config(connect_timeout=5, retries={'max_attempts': 1}))

s3_service = S3Service(bucket=settings.S3_BUCKET_NAME, client=client)

parks_path, last_update = s3_service.download_earliest_file(
    prefix=settings.PREFIX_DATA,
    pattern=settings.PREFIX_DATA + settings.PATTERN_PARKS,
    local_path='urban_parks.geojson'
)
parks_data_storage = ParksDataStorage(file_path=parks_path, last_update=dt.datetime.utcnow())

models_path, last_update = s3_service.download_earliest_file(
    prefix=settings.PREFIX_MODEL,
    pattern=settings.PREFIX_MODEL + settings.PATTERN_MODEL,
    local_path='ckd_model.pkl'
)

ckd_analyzer = CKDAnalyzer(path=models_path)
google_geocoder = Geocoder(settings.GOOGLE_KEY)


# Before first request executions
@app.before_first_request
def init_app():
    db.create_all()


# Error handler
@trace
@app.errorhandler(Exception)
def handle_error(err):
    return failure(exception=err)


# Status endpoint
@trace
@app.route(routes.STATUS, methods=['GET'])
def health_check():
    request_logger(requests=request)
    response = Response(response=json.dumps({
        'msg': 'Up and running',
        'version': settings.APP_VERSION,
        'deployed at': settings.DEPLOYED_AT,
        'requested at utc': dt.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
    }), headers={"Content-Type": "application/json"},
        status=200)
    return response


# Cancellation anomaly classification endpoint
@trace
@app.route(routes.SELF_ONBOARDING, methods=['POST'])
def classify_patient():
    request_logger(requests=request)
    patient_schema = PatientRequestSchema()
    patient_request = patient_schema.load(request.get_json())
    google_geocoder.lat_long_assign(patient_request)
    parks_data_storage.assign_closest_park(patient=patient_request)
    ckd_analyzer.predict(patient=patient_request)
    ckd_analyzer.diet_assigner(patient=patient_request)

    json_formatter = JsonFormatter()
    patient_log_schema = PatientLogSchema()
    patient_log = json_formatter.db_conversion(patient_request)
    patient_record = patient_log_schema.loads(patient_log)
    patient_record.save_to_db()

    response = json_formatter.response_conversion(patient_request)

    return response


if __name__ == '__main__':
    logging.info('Server started.')
    app.run(host='0.0.0.0', port=8000)
