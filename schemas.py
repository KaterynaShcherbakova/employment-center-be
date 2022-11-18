from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from alembic_m.models import LocationModel, PersonModel, ExperienceModel, JobModel, ApplicationModel
from marshmallow import Schema, validate, fields
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
class LocationModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LocationModel
        load_instance = True
        include_fk = True

class PersonModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonModel
        load_instance = True
        include_fk = True
    #     exclude = ("password",)
    # password = auto_field(load_only=True)


class ExperienceModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ExperienceModel
        load_instance = True
        include_fk = True

class JobModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = JobModel
        load_instance = True
        include_fk = True

class ApplicationModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ApplicationModel
        load_instance = True
        include_fk = True