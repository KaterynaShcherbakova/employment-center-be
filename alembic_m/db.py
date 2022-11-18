from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DBURL = 'postgresql+psycopg2://postgres:2580@localhost:5432/employment_center'
engine=create_engine(DBURL)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from .models import LocationModel, PersonModel, ExperienceModel, JobModel, ApplicationModel
    Base.metadata.create_all(bind=engine)