from flask import request
from flask_restful import Resource
from alembic_m.db import db_session
from alembic_m.models import PersonModel, ExperienceModel, LocationModel
from schemas import PersonModelSchema, ExperienceModelSchema, ApplicationModelSchema
from marshmallow.exceptions import ValidationError
from resp_error import errs, json_error

person_schema = PersonModelSchema()
experience_schema = ExperienceModelSchema()
application_schema = ApplicationModelSchema()


class PeopleAPI(Resource):
    def get(self):
        people_list = PersonModel.query.all()
        return person_schema.dump(people_list, many=True), 200

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        person = PersonModel.query.get(json_data.get("person_id", None))
        if person:
            return errs.exists
        location = LocationModel.query.get(json_data.get("location_id", None))
        if not location:
            return json_error('Non-existent location', 400)
        try:
            data = person_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        if PersonModel.query.filter_by(username=data.username).first():
            return json_error('Not unique username', 400)
        if PersonModel.query.filter_by(email=data.email).first():
            return json_error('Not unique email', 400)

        db_session.add(data)
        db_session.commit()

        return json_data, 201

    def put(self):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        person = PersonModel.query.get(json_data.get("person_id", None))
        if not person:
            return errs.not_found
        location = LocationModel.query.get(json_data.get("location_id", None))
        if not location:
            return json_error('Non-existent location', 400)
        try:
            data = person_schema.load(json_data, session=db_session,  partial=True)
        except ValidationError as err:
            return json_error(err.messages, 400)
        username = PersonModel.query.filter_by(username=data.username).first()
        email = PersonModel.query.filter_by(email=data.email).first()
        if username and username.person_id != data.person_id:
            return json_error('Not unique username', 400)
        if email and email.person_id != data.person_id:
            return json_error('Not unique email', 400)

        db_session.add(data)
        db_session.commit()
        return json_data, 200


class PersonIdAPI(Resource):
    def get(self, person_id):
        person = PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        return person_schema.dump(person), 200

    def delete(self, person_id):
        person = PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        db_session.delete(person)
        db_session.commit()
        return '', 204


class PersonUsernameAPI(Resource):
    def get(self, username):
        person = PersonModel.query.filter_by(username=username).first()
        if not person:
            return errs.not_found
        return person_schema.dump(person), 200

    def delete(self, username):
        person = PersonModel.query.filter_by(username=username).first()
        if not person:
            return errs.not_found
        db_session.delete(person)
        db_session.commit()
        return '', 204

class PersonExperienceApi(Resource):
    def get(self, person_id):
        person=PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        experiences = person.experiences
        return experience_schema.dump(experiences, many=True), 200

    def post(self, person_id):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        experience = ExperienceModel.query.get(json_data.get("experience_id", None))
        if experience:
            return errs.exists
        json_data['person_id']=person_id
        try:
            data = experience_schema.load(json_data, session=db_session)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return json_data, 201

    def put(self, person_id):
        json_data = request.get_json()
        if not json_data:
            return errs.bad_request
        experience = ExperienceModel.query.get(json_data.get("experience_id", None))
        if not experience:
            return errs.exists
        try:
            data = experience_schema.load(json_data, session=db_session,  partial=True)
        except ValidationError as err:
            return json_error(err.messages, 400)

        db_session.add(data)
        db_session.commit()

        return json_data, 201

class PersonExperienceIdAPI(Resource):
    def get(self, person_id, experience_id):
        person = PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        experiences = person.experiences
        experience_ids = [e.experience_id for e in experiences]
        if experience_id not in experience_ids:
            return json_error('Invalid request. Bad id value.', 400)
        experience = ExperienceModel.query.get(experience_id)
        return experience_schema.dump(experience), 200

    def delete(self, person_id, experience_id):
        person = PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        experiences = person.experiences
        experience_ids = [e.experience_id for e in experiences]
        if experience_id not in experience_ids:
            return json_error('Invalid request. Bad id value.', 400)
        experience = ExperienceModel.query.get(experience_id)
        db_session.delete(experience)
        db_session.commit()
        return '', 204


class PersonApplicationsApi(Resource):
    def get(self, person_id):
        person = PersonModel.query.get(person_id)
        if not person:
            return errs.not_found
        applications = person.applications
        return application_schema.dump(applications, many=True), 200