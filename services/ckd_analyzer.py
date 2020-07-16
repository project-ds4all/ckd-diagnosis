import os
import pickle
import logging

from entities.patient_request import PatientRequest
from services.ckd_predictor import CKDClassifier, ModelType
from services.model_loader import ModelLoader


def _load_models(path) -> ModelType:
    model_loader = ModelLoader(path=path)
    model_ckd = model_loader.load()
    return model_ckd


class CKDAnalyzer:
    def __init__(self, path):
        self.__model = _load_models(path)

    def predict(self, patient: PatientRequest):
        try:
            model = CKDClassifier(self.__model)
            logging.info(f"ckd-diagnosis calculating probability of CKD")
            patient.probability = model.predict(patient=patient)

        except KeyError:
            logging.info(f"ckd-diagnosis did not receive all the information of the patient")

    @staticmethod
    def diet_assigner(patient: PatientRequest):
        logging.info(f"ckd-diagnosis-logger: assigning diet based on probability")
        if patient.probability > 0.8:
            patient.diet = "papa con arroz"
        elif patient.probability > 0.5:
            patient.diet = "papa con arroz"
        else:
            patient.diet = "papa con arroz"

