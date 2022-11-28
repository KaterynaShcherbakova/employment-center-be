from flask import Flask
from flask_restful import Api
# from requests.auth import HTTPBasicAuth

from alembic_m.db import db_session, init_db

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


from location_api import LocationAPI, LocationIdAPI
from person_api import PersonApplicationsApi, PeopleAPI, PersonIdAPI, PersonUsernameAPI, PersonExperienceIdAPI, \
    PersonExperienceApi  # , PersonLogin
from application_api import ApplicationAPI, ApplicationIdAPI
from job_api import JobIdAPI, JobAPI, JobIdApplicationAPI

api.add_resource(LocationAPI, '/locations')
api.add_resource(LocationIdAPI, '/locations/<int:location_id>')

api.add_resource(PersonApplicationsApi, '/people/<int:person_id>/applications')
api.add_resource(PersonExperienceIdAPI, '/people/<int:person_id>/experience/<int:experience_id>')
api.add_resource(PersonUsernameAPI, '/people/<username>')
api.add_resource(PersonIdAPI, '/people/<int:person_id>')
api.add_resource(PeopleAPI, '/people')
api.add_resource(PersonExperienceApi, '/people/<int:person_id>/experiences')

api.add_resource(ApplicationAPI, '/applications')
api.add_resource(ApplicationIdAPI, '/applications/<int:application_id>')

api.add_resource(JobAPI, '/jobs')
api.add_resource(JobIdAPI, '/jobs/<int:job_id>')
api.add_resource(JobIdApplicationAPI, '/jobs/<int:job_id>/applications')
