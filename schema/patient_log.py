from marshmallow import EXCLUDE

from schema.base_schema import ma
from database.patient_log import PatientLog


class PatientLogSchema(ma.ModelSchema):
    class Meta:
        model = PatientLog
        unknown = EXCLUDE
