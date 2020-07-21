import logging
from sqlalchemy import Integer, BigInteger, Float, Sequence, DateTime, String
import datetime
from database.db import db


class PatientLog(db.Model):
    __tablename__ = "ckd_patients_records"

    id = db.Column(BigInteger, Sequence('id_seq', metadata=db.metadata), primary_key=True)
    address = db.Column(String(length=200), nullable=True)
    birth_date = db.Column(String(length=20))
    gender = db.Column(String(length=10))
    age = db.Column(Integer(), nullable=True)
    diabetes = db.Column(Integer(), nullable=True)
    pain_in_joint = db.Column(Integer(), nullable=True)
    urinary_infection = db.Column(Integer(), nullable=True)
    hypertension = db.Column(Integer(), nullable=True)
    lat = db.Column(Float())
    lng = db.Column(Float())
    strata = db.Column(Integer())
    park_id = db.Column(Integer(), nullable=True)
    park_type = db.Column(String(length=200), nullable=True)
    park_name = db.Column(String(length=200), nullable=True)
    probability = db.Column(Float())
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def save_to_db(self) -> None:
        logging.info(f"ckd-diagnosis-logger: writing patient record")
        db.session.add(self)
        db.session.commit()
