import unittest
import json
from main import app
from schemas import location_schema, application_schema, job_schema, person_schema, experience_schema
from alembic_m.models import PersonModel, ExperienceModel, JobModel, ApplicationModel, LocationModel
from alembic_m.db import db_session

pr = 'api/v1'
from flask_testing import TestCase
from base64 import b64encode
from bcrypt import hashpw, gensalt

a_headers = {
    'Authorization': 'Basic %s' % b64encode(b"adm:adm").decode("ascii")
}

e_headers = {
    'Authorization': 'Basic %s' % b64encode(b"emp:emp").decode("ascii")
}

app_headers = {
    'Authorization': 'Basic %s' % b64encode(b"app:app").decode("ascii")
}


def get_data(response):
    return json.loads(response.data.decode('utf-8'))


class ApplicationTest(TestCase):

    def create_app(self):
        return app

    @classmethod
    def setUpClass(cls):
        city = LocationModel(location_id=100, city='New-York', country='The United States')
        employer = PersonModel(person_id=100, location_id=100, firstName="Name", secondName="Surname",
                               username="emp100", password=hashpw(bytes('emp100', 'utf-8'), gensalt(14)).decode(),
                               role="employer", age=47, email="emp100@gmail.com")
        job = JobModel(job_id=100, location_id=100, position="Waiter", company="Pizza Celentano", creator_id=100)
        applicant = PersonModel(person_id=101, location_id=100, firstName="Name", secondName="Surname",
                                username="app101", password=hashpw(bytes('app101', 'utf-8'), gensalt(14)).decode(),
                                role="applicant", age=20, email="app101@gmail.com")
        application = ApplicationModel(application_id=100, job_id=100, person_id=101)
        if not LocationModel.query.get(100):
            db_session.add(city)
        if not PersonModel.query.get(100):
            db_session.add(employer)
        if not PersonModel.query.get(101):
            db_session.add(applicant)
        db_session.commit()
        if not JobModel.query.get(100):
            db_session.add(job)
        if not ApplicationModel.query.get(100):
            db_session.add(application)
        db_session.commit()

    @classmethod
    def tearDownClass(cls):
        id = 100
        app_id = 101
        to_del = [JobModel.query.get(id), PersonModel.query.get(id), PersonModel.query.get(app_id),
                  LocationModel.query.get(id), ApplicationModel.query.get(id)]
        for obj in to_del:
            if obj:
                db_session.delete(obj)
        new_application = ApplicationModel.query.get(200)
        if new_application:
            db_session.delete(new_application)
        db_session.commit()

    def test_get_all_applications(self):
        response = self.client.get(f'{pr}/applications', headers=e_headers)
        self.assertEqual(response.status_code, 200)
        application_ids = [i['application_id'] for i in get_data(response)]
        self.assertIn(100, application_ids)

    def test_post_put_get_delete(self):
        data = {
            "application_id": 200,
            "person_id": 101,
            "job_id": 100
        }

        to_del = ApplicationModel.query.get(200)
        if to_del:
            db_session.delete(to_del)
            db_session.commit()

        # POST

        # BAD REQUEST
        response = self.client.post(f'{pr}/applications', json={}, headers=app_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.post(f'{pr}/applications', json=data)
        self.assertEqual(response.status_code, 401)
        # Non-existent person
        foo_data = data.copy()
        foo_data['person_id'] = 404
        foo_data['application_id'] = 404
        response = self.client.post(f'{pr}/applications', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Non-existent job
        foo_data = data.copy()
        foo_data['job_id'] = 404
        foo_data['application_id'] = 404
        response = self.client.post(f'{pr}/applications', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD DATA
        foo_data = data.copy()
        foo_data['job_id'] = "BAD JOB ID"
        foo_data['application_id'] = 404
        response = self.client.post(f'{pr}/applications', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # CREATED
        response = self.client.post(f'{pr}/applications', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 201)
        # CHECK CREATED
        response_data = get_data(response)
        self.assertEqual(response_data['application_id'], data['application_id'])
        # ALREADY EXISTS
        response = self.client.post(f'{pr}/applications', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 403)


        # PUT
        data['person_id'] = 100

        # Non-existent job
        foo_data = data.copy()
        foo_data['job_id'] = 404
        response = self.client.put(f'{pr}/applications', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD REQUEST
        response = self.client.put(f'{pr}/applications', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.put(f'{pr}/applications', json=data)
        self.assertEqual(response.status_code, 401)

        # UPDATED
        response = self.client.put(f'{pr}/applications', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 200)
        # CHECK UPDATED
        response_data = get_data(response)
        self.assertEqual(response_data['person_id'], data['person_id'])
        # DOESN'T EXIST
        foo_data = data.copy()
        foo_data['person_id'] = 404
        response = self.client.put(f'{pr}/applications', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # GET BY ID

        # NOT FOUND
        response = self.client.get(f'{pr}/applications/421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # SUCCESS
        response = self.client.get(f'{pr}/applications/200', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        # NOT FOUND
        response = self.client.delete(f'{pr}/applications/421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # NO ACCESS
        response = self.client.delete(f'{pr}/applications/200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # SUCCESS
        response = self.client.delete(f'{pr}/applications/{data["application_id"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)


class JobTest(TestCase):

    def create_app(self):
        return app

    @classmethod
    def setUpClass(cls):
        city = LocationModel(location_id=100, city='New-York', country='The United States')
        employer = PersonModel(person_id=100, location_id=100, firstName="Name", secondName="Surname",
                               username="emp100", password=hashpw(bytes('emp100', 'utf-8'), gensalt(14)).decode(),
                               role="employer", age=47, email="emp100@gmail.com")
        job = JobModel(job_id=100, location_id=100, position="Waiter", company="Pizza Celentano", creator_id=100)
        application = ApplicationModel(application_id=100, job_id=100, person_id=100)
        if not LocationModel.query.get(100):
            db_session.add(city)
        if not PersonModel.query.get(100):
            db_session.add(employer)
        db_session.commit()
        if not JobModel.query.get(100):
            db_session.add(job)
        db_session.commit()
        if not ApplicationModel.query.get(100):
            db_session.add(application)
        db_session.commit()

    @classmethod
    def tearDownClass(cls):
        id = 100
        to_del = [JobModel.query.get(id), PersonModel.query.get(id),
                  LocationModel.query.get(id), ApplicationModel.query.get(id)]
        for obj in to_del:
            if obj:
                db_session.delete(obj)
        db_session.commit()

    def test_get_all_jobs(self):
        response = self.client.get(f'{pr}/jobs', headers=e_headers)
        self.assertEqual(response.status_code, 200)
        jobs_ids = [i['job_id'] for i in get_data(response)]
        self.assertIn(100, jobs_ids)

    def test_post_put_get_delete_jobs(self):
        data = {'job_id': 200, 'location_id': 100, 'position': "Manager", 'company': "Pizza Celentano",
                'creator_id': 100}

        to_del = JobModel.query.get(200)
        to_del1 = JobModel.query.get(404)
        if to_del:
            db_session.delete(to_del)
        if to_del1:
            db_session.delete(to_del1)
        db_session.commit()

        # POST
        # NO ACCESS
        response = self.client.post(f'{pr}/jobs', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # BAD REQUEST
        response = self.client.post(f'{pr}/jobs', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.post(f'{pr}/jobs', json=data)
        self.assertEqual(response.status_code, 401)
        # Non-existent person
        foo_data = data.copy()
        foo_data['job_id'] = 404
        foo_data['creator_id'] = 404
        response = self.client.post(f'{pr}/jobs', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Non-existent job
        foo_data = data.copy()
        foo_data['job_id'] = 404
        foo_data['location_id'] = 404
        response = self.client.post(f'{pr}/jobs', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD DATA
        foo_data = data.copy()
        foo_data['job_id'] = "404"
        foo_data['location_id'] = "BAD DATA"
        response = self.client.post(f'{pr}/jobs', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # CREATED
        response = self.client.post(f'{pr}/jobs', json=data, headers=a_headers)

        self.assertEqual(response.status_code, 201)
        # CHECK CREATED
        response_data = get_data(response)
        self.assertEqual(response_data['job_id'], data['job_id'])
        # ALREADY EXISTS
        response = self.client.post(f'{pr}/jobs', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 403)

        # PUT
        data['position'] = 'HR-Manager'

        # NO ACCESS
        response = self.client.put(f'{pr}/jobs', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # BAD REQUEST
        response = self.client.put(f'{pr}/jobs', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.put(f'{pr}/jobs', json=data)
        self.assertEqual(response.status_code, 401)
        # UPDATED
        response = self.client.put(f'{pr}/jobs', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 200)
        # CHECK UPDATED
        response_data = get_data(response)
        self.assertEqual(response_data['position'], data['position'])
        # DOESN'T EXIST
        foo_data = data.copy()
        foo_data['location_id'] = 404
        response = self.client.put(f'{pr}/jobs', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # GET BY ID

        # NOT FOUND
        response = self.client.get(f'{pr}/jobs/421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # SUCCESS
        response = self.client.get(f'{pr}/jobs/200', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        # NO ACCESS
        response = self.client.delete(f'{pr}/jobs/200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # SUCCESS
        response = self.client.delete(f'{pr}/jobs/{data["job_id"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)

    def test_get_jobs_app(self):
        # SUCCESS
        response = self.client.get(f'{pr}/jobs/100/applications', headers=a_headers)
        self.assertEqual(response.status_code, 200)
        jobs_ids = [i['application_id'] for i in get_data(response)]
        self.assertIn(100, jobs_ids)


class PersonTest(TestCase):

    def create_app(self):
        return app

    @classmethod
    def setUpClass(cls):
        city = LocationModel(location_id=100, city='New-York', country='The United States')
        employer = PersonModel(person_id=100, location_id=100, firstName="Name", secondName="Surname",
                               username="emp100", password=hashpw(bytes('emp100', 'utf-8'), gensalt(14)).decode(),
                               role="employer", age=47, email="emp100@gmail.com")
        job = JobModel(job_id=100, location_id=100, position="Waiter", company="Pizza Celentano", creator_id=100)
        applicant = PersonModel(person_id=101, location_id=100, firstName="Name", secondName="Surname",
                                username="app101", password=hashpw(bytes('app101', 'utf-8'), gensalt(14)).decode(),
                                role="applicant", age=20, email="app101@gmail.com")
        application = ApplicationModel(application_id=100, job_id=100, person_id=101)
        experience = ExperienceModel(person_id=100, experience_id=100, beggining='2019-12-19', end='2022-12-19',
                                     job="Stripper")
        if not LocationModel.query.get(100):
            db_session.add(city)
        if not PersonModel.query.get(100):
            db_session.add(employer)
        if not PersonModel.query.get(101):
            db_session.add(applicant)
        db_session.commit()
        if not ExperienceModel.query.get(100):
            db_session.add(experience)
        if not JobModel.query.get(100):
            db_session.add(job)
        if not ApplicationModel.query.get(100):
            db_session.add(application)
        db_session.commit()

    @classmethod
    def tearDownClass(cls):

        id = 100
        app_id = 101
        to_del = [JobModel.query.get(id), PersonModel.query.get(id), PersonModel.query.get(app_id),
                  LocationModel.query.get(id), ApplicationModel.query.get(id), ExperienceModel.query.get(id)]
        for obj in to_del:
            if obj:
                db_session.delete(obj)
        new_application = ApplicationModel.query.get(200)
        if new_application:
            db_session.delete(new_application)
        db_session.commit()

    def test_get_all_people(self):
        response = self.client.get(f'{pr}/people', headers=a_headers)
        self.assertEqual(response.status_code, 200)
        people_ids = [i['person_id'] for i in get_data(response)]
        self.assertIn(100, people_ids)

    def test_get_all_person_experience(self):
        response = self.client.get(f'{pr}/people/100/experiences', headers=a_headers)
        self.assertEqual(response.status_code, 200)
        people_ids = [i['experience_id'] for i in get_data(response)]
        self.assertIn(100, people_ids)

    def test_post_put_get_delete_people(self):
        data = {'person_id': 200, 'location_id': 100, 'firstName': "Name", 'secondName': "Surname",
                'username': "app200", 'password': hashpw(bytes('app200', 'utf-8'), gensalt(14)).decode(),
                'role': "applicant", 'age': 20, 'email': "app200@gmail.com"}

        to_del = PersonModel.query.get(200)
        to_del1 = PersonModel.query.get(404)
        if to_del:
            db_session.delete(to_del)
        if to_del1:
            db_session.delete(to_del1)
        db_session.commit()

        # POST

        # BAD REQUEST
        response = self.client.post(f'{pr}/people', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Not unique username
        foo_data = data.copy()
        foo_data['username'] = 'adm'
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Not unique email
        foo_data = data.copy()
        foo_data['email'] = 'app101@gmail.com'
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Non-existent location
        foo_data = data.copy()
        foo_data['location_id'] = 404
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD DATA
        foo_data = data.copy()
        foo_data['person_id'] = "404"
        foo_data['location_id'] = "BAD DATA"
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # CREATED
        response = self.client.post(f'{pr}/people', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 201)
        # CHECK CREATED
        response_data = get_data(response)
        self.assertEqual(response_data['person_id'], data['person_id'])
        # ALREADY EXISTS
        response = self.client.post(f'{pr}/people', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 403)

        # PUT
        data['age'] = 19
        # NO ACCESS
        response = self.client.put(f'{pr}/people', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # BAD DATA
        foo_data = data.copy()
        foo_data['person_id'] = "404"
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD REQUEST
        response = self.client.put(f'{pr}/people', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.put(f'{pr}/people', json=data)
        self.assertEqual(response.status_code, 401)
        # UPDATED
        response = self.client.put(f'{pr}/people', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 200)
        # CHECK UPDATED
        response_data = get_data(response)
        self.assertEqual(response_data['age'], data['age'])
        # DOESN'T EXIST
        foo_data = data.copy()
        foo_data['location_id'] = 404
        response = self.client.put(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Not unique username
        foo_data = data.copy()
        foo_data['username'] = 'adm'
        response = self.client.put(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Not unique email
        foo_data = data.copy()
        foo_data['email'] = 'app101@gmail.com'
        response = self.client.put(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # Non-existent location
        foo_data = data.copy()
        foo_data['location_id'] = 404
        response = self.client.put(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD DATA
        foo_data = data.copy()
        foo_data['person_id'] = "404"
        foo_data['location_id'] = "BAD DATA"
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # GET BY ID
        # NO ACCESS
        response = self.client.get(f'{pr}/people/200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # NOT FOUND
        response = self.client.get(f'{pr}/people/421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # SUCCESS
        response = self.client.get(f'{pr}/people/200', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        # NO ACCESS
        response = self.client.delete(f'{pr}/people/200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # SUCCESS
        response = self.client.delete(f'{pr}/people/{data["person_id"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)

        # GET BY USERNAME
        data = {'person_id': 200, 'location_id': 100, 'firstName': "Name", 'secondName': "Surname",
                'username': "app200", 'password': hashpw(bytes('app200', 'utf-8'), gensalt(14)).decode(),
                'role': "applicant", 'age': 20, 'email': "app200@gmail.com"}
        # CREATED
        response = self.client.post(f'{pr}/people', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 201)
        # NO ACCESS
        response = self.client.get(f'{pr}/people/app200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # NOT FOUND
        response = self.client.get(f'{pr}/people/app421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # SUCCESS
        response = self.client.get(f'{pr}/people/app200', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        # NO ACCESS
        response = self.client.delete(f'{pr}/people/app200', headers=app_headers)
        self.assertEqual(response.status_code, 403)
        response = self.client.delete(f'{pr}/people/{data["username"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)

    def test_get_people_app(self):
        response = self.client.get(f'{pr}/people/101/applications', headers=a_headers)
        self.assertEqual(response.status_code, 200)
        people_ids = [i['application_id'] for i in get_data(response)]
        self.assertIn(100, people_ids)

    def test_post_put_get_delete_exp(self):
        data = {'person_id': 100, "job": "Manager", "beggining": "2019-09-19", "experience_id": 200}

        to_del = ExperienceModel.query.get(200)
        to_del1 = ExperienceModel.query.get(404)
        if to_del:
            db_session.delete(to_del)
        if to_del1:
            db_session.delete(to_del1)
        db_session.commit()

        # POST

        # BAD REQUEST
        response = self.client.post(f'{pr}/people/100/experiences', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.post(f'{pr}/people/100/experiences', json=data)
        self.assertEqual(response.status_code, 401)
        # NO ACCESS
        response = self.client.post(f'{pr}/people/100/experiences', json=data, headers=app_headers)
        self.assertEqual(response.status_code, 403)
        # Non-existent person
        foo_data = data.copy()
        foo_data['person_id'] = 404
        response = self.client.post(f'{pr}/people/100/experiences', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD DATA
        foo_data = data.copy()
        foo_data['person_id'] = "404"
        response = self.client.post(f'{pr}/people/100/experiences', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # CREATED
        response = self.client.post(f'{pr}/people/100/experiences', json=data, headers=a_headers)

        self.assertEqual(response.status_code, 201)
        # CHECK CREATED
        response_data = get_data(response)
        self.assertEqual(response_data['experience_id'], data['experience_id'])
        # ALREADY EXISTS
        response = self.client.post(f'{pr}/people/100/experiences', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 403)

        # PUT
        data['job'] = "Policeman"
        # BAD DATA
        foo_data = data.copy()
        foo_data['person_id'] = "404"
        response = self.client.post(f'{pr}/people', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD REQUEST
        response = self.client.put(f'{pr}/people/100/experiences', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.put(f'{pr}/people/100/experiences', json=data)
        self.assertEqual(response.status_code, 401)
        # UPDATED
        response = self.client.put(f'{pr}/people/100/experiences', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 200)
        # CHECK UPDATED
        response_data = get_data(response)
        self.assertEqual(response_data['job'], data['job'])
        # DOESN'T EXIST
        foo_data = data.copy()
        foo_data['person_id'] = 404
        response = self.client.put(f'{pr}/people/100/experiences', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 400)

        # GET BY ID

        # NOT FOUND
        response = self.client.get(f'{pr}/people/100/experience/421', headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # SUCCESS
        response = self.client.get(f'{pr}/people/100/experience/200', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        # NOT FOUND
        response = self.client.delete(f'{pr}/people/100/experience/400', headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # SUCCESS
        response = self.client.delete(f'{pr}/people/100/experience/{data["experience_id"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)


class LocationTest(TestCase):

    def create_app(self):
        return app

    @classmethod
    def setUpClass(cls):
        city = LocationModel(location_id=100, city='New-York', country='The United States')

        if not LocationModel.query.get(100):
            db_session.add(city)
        db_session.commit()

    @classmethod
    def tearDownClass(cls):
        id = 100
        app_id = 101
        to_del = [LocationModel.query.get(id)]
        for obj in to_del:
            if obj:
                db_session.delete(obj)
        new_location = LocationModel.query.get(200)
        if new_location:
            db_session.delete(new_location)
        db_session.commit()

    def test_get_all_locations(self):
        response = self.client.get(f'{pr}/locations', headers=e_headers)
        self.assertEqual(response.status_code, 200)
        location_ids = [i['location_id'] for i in get_data(response)]
        self.assertIn(100, location_ids)

    def test_post_put_get_delete(self):
        data = {
            "location_id": 200,
            "city": "Washington",
            "country": "The United States"
        }

        to_del = LocationModel.query.get(200)
        if to_del:
            db_session.delete(to_del)
            db_session.commit()

        # POST

        # BAD REQUEST
        response = self.client.post(f'{pr}/locations', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.post(f'{pr}/locations', json=data)
        self.assertEqual(response.status_code, 401)

        # CREATED
        response = self.client.post(f'{pr}/locations', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 201)
        # CHECK CREATED
        response_data = get_data(response)
        self.assertEqual(response_data['location_id'], data['location_id'])
        # ALREADY EXISTS
        response = self.client.post(f'{pr}/locations', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 403)

        # PUT
        data['location_id'] = 200

        # BAD REQUEST
        response = self.client.put(f'{pr}/locations', json={}, headers=a_headers)
        self.assertEqual(response.status_code, 400)
        # BAD AUTH
        response = self.client.put(f'{pr}/locations', json=data)
        self.assertEqual(response.status_code, 401)
        # UPDATED
        response = self.client.put(f'{pr}/locations', json=data, headers=a_headers)
        self.assertEqual(response.status_code, 200)
        # CHECK UPDATED
        response_data = get_data(response)
        self.assertEqual(response_data['location_id'], data['location_id'])
        # DOESN'T EXIST
        foo_data = data.copy()
        foo_data['location_id'] = 404
        response = self.client.put(f'{pr}/locations', json=foo_data, headers=a_headers)
        self.assertEqual(response.status_code, 404)

        # GET BY ID

        # NOT FOUND
        response = self.client.get(f'{pr}/locations/421', headers=a_headers)
        self.assertEqual(response.status_code, 404)
        # SUCCESS
        response = self.client.get(f'{pr}/locations/100', headers=a_headers)
        self.assertEqual(response.status_code, 200)

        # DELETE
        response = self.client.delete(f'{pr}/locations/{data["location_id"]}', headers=a_headers)
        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()

# python -m coverage run -m unittest
# coverage report -m
