from flask import request
from flask_restful import Resource
from alembic_m.db import db_session
from alembic_m.models import JobModel, ApplicationModel, PersonModel
from schemas import ApplicationModelSchema
from marshmallow.exceptions import ValidationError
from resp_error import errs, json_error
from all_api import *

application_schema = ApplicationModelSchema()

class ApplicationAPI(Resource):
    @auth.login_required(role=["admin", "aplicant", "employer"])
    def get(self):
        applications_list = ApplicationModel.query.all()
        return application_schema.dump(applications_list, many=True), 200

    @auth.login_required(role="aplicant")
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        application = ApplicationModel.query.get(json_data.get("application_id", None))
        if application:
            return errs.exists
        person = PersonModel.query.get(json_data.get("person_id", None))
        if not person:
            return json_error('Non-existent person', 400)
        job = JobModel.query.get(json_data.get("job_id", None))
        if not job:
            return json_error('Non-existent job', 400)
        try:
            data = application_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()
        return json_data, 201

    @auth.login_required(role=["aplicant","admin"])
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        application = ApplicationModel.query.get(json_data.get("application_id", None))
        if not application:
            return errs.not_found
        person = PersonModel.query.get(json_data.get("person_id", None))
        if not person:
            return json_error('Non-existent person', 400)
        job = JobModel.query.get(json_data.get("job_id", None))
        if not job:
            return json_error('Non-existent job', 400)
        try:
            data = application_schema.load(json_data, session=db_session,  partial=True)
        except ValidationError as err:
            return json_error(err.messages, 400)

        if data.person_id != get_current_user().person_id and get_current_user().role != "admin":
            return errs.no_access

        db_session.add(data)
        db_session.commit()
        return json_data, 200

class ApplicationIdAPI(Resource):
    @auth.login_required(role="admin")
    def get(self, application_id):
        application = ApplicationModel.query.get(application_id)
        if not application:
            return errs.not_found
        return application_schema.dump(application), 200

    @auth.login_required(role=["aplicant", "admin"])
    def delete(self, application_id):
        application = ApplicationModel.query.get(application_id)
        if not application:
            return errs.not_found
        if application.person_id != get_current_user().person_id and get_current_user().role != "admin":
            return errs.no_access

        db_session.delete(application)
        db_session.commit()
        return '', 204

