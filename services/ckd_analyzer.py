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
        if patient.probability > 0.6:
            patient.meal = "Evitar alimentos fritos, en especial papas y alimentos procesados como galletas. Adicionalmente, procure consumir alimentos integrales."
            patient.sugars = "Evitar el consumo de postres, gaseosas y jugos."
            patient.fats = "Evitar el consumo de fritos (alitas, chicharrón, costillas) y embutidos. En su lugar consumir alimentos cocidos o al horno y grasas saludables como el aguacate."
            patient.protein = "Evitar el consumo de atún, embutidos y congelados, adicionalmente cuidar el tamaño de las porciones consumidas. Procurar consumir huevo, carnes como pescado o pechuga de pollo y proteinas vegetales como el tofu y leguminosas."
            patient.alcohol = "Evitar el consumo de cualquier tipo de bebidas alcohólicas."
        elif patient.probability > 0.4:
            patient.meal = "Evitar alimentos fritos, en especial papas y alimentos procesados como galletas."
            patient.sugars = "Evitar el consumo de postres y gaseosas."
            patient.fats = "Evitar el consumo de fritos y embutidos."
            patient.protein = "Evitar el consumo de atún, embutidos y congelados, consumir una porción adecuada a sus necesidades físicas. Procurar consumir huevo, carnes como pescado o pechuga de pollo y proteinas vegetales como el tofu y leguminosas."
            patient.alcohol = "Evitar el consumo de cualquier tipo de bebidas alcohólicas."
        else:
            patient.meal = "Evitar excesos en alimentos procesados como galletas."
            patient.sugars = "Evitar excesos en el consumo de postres, dulces y gaseosas"
            patient.fats = "Evitar el consumo de fritos y embutidos."
            patient.protein = "Procurar consumir huevo, carnes no procesadas y proteinas vegetales como el tofu y leguminosas."
            patient.alcohol = "Evitar un consumo de bebidas alcohólicas."

