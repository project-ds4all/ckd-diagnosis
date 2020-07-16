import numpy as np
from typing import NewType
from sklearn.neural_network import MLPClassifier

from entities.patient_request import PatientRequest
from utils.profile_utils import profile

ModelType = NewType("Model", MLPClassifier)


def _build_data(data):
    return np.array([data.age, data.diabetes, data.pain_in_joint,
                     data.urinary_infection, data.hypertension]).reshape(1, -1)


class CKDClassifier:
    def __init__(self,
                 model: ModelType):
        self.__model = model

    @profile
    def predict(self, patient: PatientRequest) -> float:

        obs = _build_data(data=patient)
        prediction = self.__model.predict_proba(obs)[0, 1]
        return prediction
