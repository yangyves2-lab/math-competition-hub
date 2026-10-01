
from datetime import datetime
from . import db

class Competition(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(300),nullable=False)
    country=db.Column(db.String(120))
    organizer=db.Column(db.String(300))
    category=db.Column(db.String(80),default="competition")
    target=db.Column(db.Text)
    official_url=db.Column(db.Text)
    description=db.Column(db.Text)
    first_seen=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    last_checked=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    editions=db.relationship("Edition",backref="competition",cascade="all, delete-orphan")
    sources=db.relationship("Source",backref="competition",cascade="all, delete-orphan")

class Edition(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    competition_id=db.Column(db.Integer,db.ForeignKey("competition.id"),nullable=False)
    year=db.Column(db.Integer,nullable=False)
    registration_start=db.Column(db.Date)
    registration_end=db.Column(db.Date)
    event_date=db.Column(db.String(120))
    fee=db.Column(db.String(200))
    target=db.Column(db.Text)
    difficulty=db.Column(db.Integer,default=3)
    difficulty_note=db.Column(db.Text)
    status=db.Column(db.String(30),default="unknown")
    notes=db.Column(db.Text)
    papers=db.relationship("Paper",backref="edition",cascade="all, delete-orphan")
    __table_args__=(db.UniqueConstraint("competition_id","year",name="uq_comp_year"),)

class Paper(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    edition_id=db.Column(db.Integer,db.ForeignKey("edition.id"),nullable=False)
    title=db.Column(db.String(300))
    year=db.Column(db.Integer)
    paper_url=db.Column(db.Text)
    solution_url=db.Column(db.Text)
    source_type=db.Column(db.String(30),default="official")
    first_seen=db.Column(db.DateTime,default=datetime.utcnow)
    last_checked=db.Column(db.DateTime,default=datetime.utcnow)
    __table_args__=(db.UniqueConstraint("edition_id","title","paper_url",name="uq_paper"),)

class Source(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    competition_id=db.Column(db.Integer,db.ForeignKey("competition.id"),nullable=False)
    url=db.Column(db.Text,nullable=False)
    source_type=db.Column(db.String(30),default="official")
    title=db.Column(db.String(500))
    checked_at=db.Column(db.DateTime,default=datetime.utcnow)

class ChangeLog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    competition_id=db.Column(db.Integer,db.ForeignKey("competition.id"))
    edition_id=db.Column(db.Integer,db.ForeignKey("edition.id"))
    checked_at=db.Column(db.DateTime,default=datetime.utcnow)
    field_name=db.Column(db.String(120))
    old_value=db.Column(db.Text)
    new_value=db.Column(db.Text)
    source_url=db.Column(db.Text)

class SearchRun(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    started_at=db.Column(db.DateTime,default=datetime.utcnow)
    finished_at=db.Column(db.DateTime)
    new_count=db.Column(db.Integer,default=0)
    updated_count=db.Column(db.Integer,default=0)
    paper_count=db.Column(db.Integer,default=0)
    error_count=db.Column(db.Integer,default=0)
    notes=db.Column(db.Text)
