from flask import request
from flask_restful import Resource
from alembic_m.db import db_session
from alembic_m.models import JobModel, ApplicationModel, LocationModel
from schemas import JobModelSchema, ApplicationModelSchema
from marshmallow.exceptions import ValidationError
from resp_error import errs, json_error
from all_api import *

job_schema = JobModelSchema()
application_schema = ApplicationModelSchema()


class JobIdAPI(Resource):
    def get(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        return job_schema.dump(job), 200

    @auth.login_required(role=["employer", "admin"])
    def delete(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        if get_current_user().person_id != job.creator_id and get_current_user().role!="admin":
            return errs.no_access
        db_session.delete(job)
        db_session.commit()
        return '', 204

class JobAPI(Resource):
    def get(self):
        jobs_list = JobModel.query.all()
        return job_schema.dump(jobs_list, many=True), 200

    @auth.login_required(role=["employer", "admin"])
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        job = JobModel.query.get(json_data.get("job_id", None))
        if job:
            return errs.exists
        location = LocationModel.query.get(json_data.get("location_id", None))
        if not location:
            return json_error('Non-existent location', 400)
        try:
            data = job_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        data.creator_id = get_current_user().person_id
        db_session.add(data)
        db_session.commit()
        return json_data, 201

    @auth.login_required(role=["employer", "admin"])
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        job = JobModel.query.get(json_data.get("job_id", None))
        if not job:
            return errs.not_found

        location = LocationModel.query.get(json_data.get("location_id", None))
        if not location:
            return json_error('Non-existent location', 400)
        try:
            data = job_schema.load(json_data, session=db_session,  partial=True)
        except ValidationError as err:
            return json_error(err.messages, 400)

        if get_current_user().person_id != job.creator_id and get_current_user().role != "admin":
            return errs.no_access

        db_session.add(data)
        db_session.commit()
        return json_data, 200

class JobIdApplicationAPI(Resource):
    @auth.login_required(role=["employer", "admin"])
    def get(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        applications = job.applications
        if not applications:
            return errs.not_found
        if get_current_user().person_id != job.creator_id and get_current_user().role != "admin":
            return errs.no_access

        return application_schema.dump(applications, many=True), 200
