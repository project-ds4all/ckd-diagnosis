from dateutil.relativedelta import relativedelta
from datetime import datetime


class PatientRequest:
    def __init__(self, **kwargs):
        self.address = kwargs['address']
        self.birth_date = kwargs['birth_date']
        self.diabetes = kwargs['diabetes']
        self.pain_in_joint = kwargs['pain_in_joint']
        self.urinary_infection = kwargs['urinary_infection']
        self.hypertension = kwargs['hypertension']
        self.gender = kwargs['gender']
        self.probability = None
        self.lat = None
        self.lng = None
        self.park_id = None
        self.park_type = None
        self.park_name = None
        self.sugars = None
        self.fruits = None
        self.vegetables = None
        self.protein = None
        self.fats = None
        self.meal = None
        self.dairy = None
        self.alcohol = None
        self.strata = None
        self.__assign_age()

    def __assign_age(self):
        self.age = relativedelta(datetime.today(), self.birth_date).years
