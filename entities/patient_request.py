class PatientRequest:
    def __init__(self, **kwargs):
        self.address = kwargs['address']
        self.age = kwargs['age']
        self.diabetes = kwargs['diabetes']
        self.pain_in_joint = kwargs['pain_in_joint']
        self.urinary_infection = kwargs['urinary_infection']
        self.hypertension = kwargs['hypertension']
        self.probability = None
        self.lat = None
        self.lng = None
        self.park_id = None
        self.park_type = None
        self.park_name = None
        self.diet = None
