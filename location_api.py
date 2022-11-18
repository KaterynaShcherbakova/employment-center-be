from flask import request
from flask_restful import Resource
from alembic_m.db import db_session
from alembic_m.models import LocationModel
from schemas import LocationModelSchema
from marshmallow.exceptions import ValidationError
from resp_error import errs, json_error

from all_api import *

location_schema = LocationModelSchema()

class LocationAPI(Resource):
    @auth.login_required
    def get(self):
        locations_list = LocationModel.query.all()
        return location_schema.dump(locations_list, many=True), 200

    @auth.login_required(role="admin")
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        location = LocationModel.query.get(json_data.get("location_id", None))
        if location:
            return errs.exists
        try:
            data = location_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)
        db_session.add(data)
        db_session.commit()
        return json_data, 201

    @auth.login_required(role="admin")
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        location = LocationModel.query.get(json_data.get("location_id", None))
        if not location:
            return errs.not_found
        try:
            data = location_schema.load(json_data, session=db_session, partial=True)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()
        return json_data, 200

class LocationIdAPI(Resource):
    @auth.login_required
    def get(self, location_id):
        location = LocationModel.query.get(location_id)
        if not location:
            return errs.not_found
        return location_schema.dump(location), 200

    @auth.login_required(role="admin")
    def delete(self, location_id):
        location = LocationModel.query.get(location_id)
        if not location:
            return errs.not_found
        db_session.delete(location)
        db_session.commit()
        return '', 204
