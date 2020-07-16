import json
from entities.patient_request import PatientRequest


class JsonFormatter:
    def __init__(self):
        pass

    @staticmethod
    def db_conversion(patient_request: PatientRequest):
        patient_log = json.dumps({
            "address": patient_request.address,
            "age": patient_request.age,
            "diabetes": patient_request.diabetes,
            "pain_in_joint": patient_request.pain_in_joint,
            "urinary_infection": patient_request.urinary_infection,
            "hypertension": patient_request.hypertension,
            "lat": patient_request.lat,
            "lng": patient_request.lng,
            "park_id": patient_request.park_id,
            "park_type": patient_request.park_type,
            "park_name": patient_request.park_name,
            "probability": patient_request.probability
        })
        return patient_log

    @staticmethod
    def response_conversion(patient_request: PatientRequest):
        response = json.dumps({
            "address": patient_request.address,
            "age": patient_request.age,
            "diabetes": patient_request.diabetes,
            "pain_in_joint": patient_request.pain_in_joint,
            "urinary_infection": patient_request.urinary_infection,
            "hypertension": patient_request.hypertension,
            "lat": patient_request.lat,
            "lng": patient_request.lng,
            "park_id": patient_request.park_id,
            "park_type": patient_request.park_type,
            "park_name": patient_request.park_name,
            "probability": patient_request.probability
        })
        return response
