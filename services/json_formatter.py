import json
from entities.patient_request import PatientRequest


class JsonFormatter:
    def __init__(self):
        pass

    @staticmethod
    def db_conversion(patient_request: PatientRequest):
        patient_log = json.dumps({
            "address": patient_request.address,
            "birth_date": str(patient_request.birth_date),
            "gender": patient_request.gender,
            "age": patient_request.age,
            "diabetes": patient_request.diabetes,
            "pain_in_joint": patient_request.pain_in_joint,
            "urinary_infection": patient_request.urinary_infection,
            "hypertension": patient_request.hypertension,
            "lat": patient_request.lat,
            "lng": patient_request.lng,
            "strata": patient_request.strata,
            "park_id": patient_request.park_id,
            "park_type": patient_request.park_type,
            "park_name": patient_request.park_name,
            "probability": patient_request.probability
        }, ensure_ascii=False)
        return patient_log

    @staticmethod
    def response_conversion(patient_request: PatientRequest):
        response = json.dumps({
            "lat": patient_request.lat,
            "lng": patient_request.lng,
            "park_id": patient_request.park_id,
            "park_type": patient_request.park_type,
            "park_name": patient_request.park_name,
            "probability": round(patient_request.probability*100, 1),
            "protein": patient_request.protein,
            "meals": patient_request.meal,
            "alcohol": patient_request.alcohol,
            "dairy": patient_request.dairy,
            "fats": patient_request.fats,
            "sugars": patient_request.sugars,
            "vegetables": patient_request.vegetables,
            "fruits": patient_request.fruits
        }, ensure_ascii=False)
        return response
