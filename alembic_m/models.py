from sqlalchemy import UniqueConstraint, Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import declarative_base, relationship
from .db import Base
from datetime import date


# alembic revision --autogenerate -m "Create tables"
# alembic upgrade heads

class LocationModel(Base):
    __tablename__ = "location"
    __table_args__ = (
        UniqueConstraint("city", "country"),
    )
    location_id = Column(Integer, primary_key=True)
    city = Column(String(80), nullable=False)
    country = Column(String(80), nullable=False)
    people = relationship('PersonModel', backref='location')
    jobs = relationship('JobModel', backref='location')


class PersonModel(Base):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("location.location_id"))
    username = Column(String(45), nullable=False, unique=True)
    password = Column(String(512), nullable=False)
    email = Column(String(45), nullable=False, unique=True)
    firstName = Column(String(64), nullable=False)
    secondName = Column(String(64), nullable=False)
    age = Column(Integer, nullable=False)
    role = Column(String(45), nullable=False, default="applicant")
    experiences = relationship("ExperienceModel", backref='person')
    applications = relationship("ApplicationModel", backref='person')


class ExperienceModel(Base):
    __tablename__ = "experience"

    experience_id = Column(Integer, primary_key=True)
    beggining = Column(Date, nullable=False)
    end = Column(Date, nullable=True)
    job = Column(String(80), nullable=False)
    person_id = Column(Integer, ForeignKey("person.person_id"))


class JobModel(Base):
    __tablename__ = "job"

    job_id = Column(Integer(), primary_key=True)
    position = Column(String(80), nullable=False)
    salary = Column(Integer)
    company = Column(String(80), nullable=False)
    online = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.location_id"))
    applications = relationship("ApplicationModel", backref='job')


class ApplicationModel(Base):
    __tablename__ = "application"

    application_id = Column(Integer(), primary_key=True)
    person_id = Column(Integer, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("job.job_id", ondelete="CASCADE"), nullable=False)
    dateOfApp = Column(Date, default=str(date.today()))
