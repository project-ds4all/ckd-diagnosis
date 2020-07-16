import os
import datetime as dt

# APP
APP_NAME = 'ckd-diagnosis'
APP_VERSION = '1.0.0'
APP_ID = os.getenv('x_application_id', APP_NAME)
BASE_PATH = f'/api/{APP_NAME}'
DEBUG = os.getenv('DEBUG', True)
PROPAGATE_EXCEPTIONS = os.getenv('PROPAGATE_EXCEPTIONS', True)
DEPLOYED_AT = dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
LOG_PATTERN = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:(%(threadName)-10s):%(levelname)s:%(process)d:%(message)s'

# ENVIRONMENT
ENV = 'dev' if os.getenv("ENVIRONMENT").lower() == 'dev' else 'prod'
LOCAL = os.getenv('LOCAL', False)

# MICROSERVICES
DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', 10))
API_KEY = str(os.getenv('API_KEY_VALUE'))

# POSTGRES SQL
PG_USER = os.getenv('POSTGRES_USER')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD')
PG_HOST = os.getenv('POSTGRES_HOST')
PG_PORT = os.getenv('POSTGRES_PORT')
PG_DATABASE = os.getenv('POSTGRES_DATABASE')

# S3 CREDENTIALS
S3_CONNECTION_STR = os.getenv('S3_BUCKET')
S3_BUCKET_NAME = S3_CONNECTION_STR.split('.')[0]

# S3 PREFIX AND PATH
PREFIX_DATA = f'data'
PATTERN_PARKS = '/urban_parks.geojson'

PREFIX_MODEL = f'models'
PATTERN_MODEL = '/\\w+.pkl'


# AWS CREDENTIALS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# GOOGLE CREDENTIALS
GOOGLE_KEY = os.getenv('GOOGLE_ACCESS_KEY_ID')

# SIGNALFX ENV VARS
SIGNALFX_ACCESS_TOKEN = os.getenv('SIGNALFX_ACCESS_TOKEN', '')
SIGNALFX_ENDPOINT_URL = os.getenv('SIGNALFX_ENDPOINT_URL', '')
SIGNALFX_TRACING_ENABLED = os.getenv('SIGNALFX_TRACING_ENABLED', False)
SIGNALFX_SERVICE_NAME = f'{APP_NAME}'

