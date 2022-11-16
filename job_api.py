from flask import request
from flask_restful import Resource
from alembic_m.db import db_session
from alembic_m.models import JobModel, ApplicationModel, LocationModel
from schemas import JobModelSchema, ApplicationModelSchema
from marshmallow.exceptions import ValidationError
from resp_error import errs, json_error

job_schema = JobModelSchema()
application_schema = ApplicationModelSchema()


class JobIdAPI(Resource):
    def get(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        return job_schema.dump(job), 200

    def delete(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        db_session.delete(job)
        db_session.commit()
        return '', 204

class JobAPI(Resource):
    def get(self):
        jobs_list = JobModel.query.all()
        return job_schema.dump(jobs_list, many=True), 200

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
        db_session.add(data)
        db_session.commit()
        return json_data, 201

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

        db_session.add(data)
        db_session.commit()
        return json_data, 200

class JobIdApplicationAPI(Resource):

    def get(self, job_id):
        job = JobModel.query.get(job_id)
        if not job:
            return errs.not_found
        applications = job.applications
        return application_schema.dump(applications, many=True), 200
