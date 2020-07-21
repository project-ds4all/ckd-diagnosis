from marshmallow import Schema, fields, post_load, EXCLUDE
from entities.dashboard_request import DashboardRequest


class DashboardRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    genders = fields.Str(required=True)
    years = fields.Str(required=True)
    values = fields.Str(required=True)
    indexes = fields.Str(required=True)
    group = fields.Str(required=True)

    @post_load()
    def make_alarm(self, data: dict, **kwargs) -> DashboardRequest:
        return DashboardRequest(**data)
