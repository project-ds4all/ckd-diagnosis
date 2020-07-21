from marshmallow import Schema, fields, post_load, EXCLUDE
from entities.patient_request import PatientRequest


class PatientRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    address = fields.Str(required=True)
    birth_date = fields.Date(required=True)
    diabetes = fields.Int(required=True)
    pain_in_joint = fields.Int(required=True)
    urinary_infection = fields.Int(required=True)
    hypertension = fields.Int(required=True)
    gender = fields.Str(required=True)

    @post_load()
    def make_alarm(self, data: dict, **kwargs) -> PatientRequest:
        return PatientRequest(**data)
