"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import List

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# --- Persistence (SQLite via SQLAlchemy) ---
DB_PATH = os.path.join(current_dir, "activities.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)

    participants: List["Participant"] = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)

    activity: Activity = relationship("Activity", back_populates="participants")

    __table_args__ = (
        UniqueConstraint("email", "activity_id", name="uq_participant_email_activity"),
    )


def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed initial activities if empty
    db = SessionLocal()
    try:
        if db.query(Activity).count() == 0:
            seed_data = [
                ("Chess Club", "Learn strategies and compete in chess tournaments", "Fridays, 3:30 PM - 5:00 PM", 12,
                 ["michael@mergington.edu", "daniel@mergington.edu"]),
                ("Programming Class", "Learn programming fundamentals and build software projects", "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", 20,
                 ["emma@mergington.edu", "sophia@mergington.edu"]),
                ("Gym Class", "Physical education and sports activities", "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", 30,
                 ["john@mergington.edu", "olivia@mergington.edu"]),
                ("Soccer Team", "Join the school soccer team and compete in matches", "Tuesdays and Thursdays, 4:00 PM - 5:30 PM", 22,
                 ["liam@mergington.edu", "noah@mergington.edu"]),
                ("Basketball Team", "Practice and play basketball with the school team", "Wednesdays and Fridays, 3:30 PM - 5:00 PM", 15,
                 ["ava@mergington.edu", "mia@mergington.edu"]),
                ("Art Club", "Explore your creativity through painting and drawing", "Thursdays, 3:30 PM - 5:00 PM", 15,
                 ["amelia@mergington.edu", "harper@mergington.edu"]),
                ("Drama Club", "Act, direct, and produce plays and performances", "Mondays and Wednesdays, 4:00 PM - 5:30 PM", 20,
                 ["ella@mergington.edu", "scarlett@mergington.edu"]),
                ("Math Club", "Solve challenging problems and participate in math competitions", "Tuesdays, 3:30 PM - 4:30 PM", 10,
                 ["james@mergington.edu", "benjamin@mergington.edu"]),
                ("Debate Team", "Develop public speaking and argumentation skills", "Fridays, 4:00 PM - 5:30 PM", 12,
                 ["charlotte@mergington.edu", "henry@mergington.edu"]),
            ]
            for name, description, schedule, maxp, emails in seed_data:
                act = Activity(name=name, description=description, schedule=schedule, max_participants=maxp)
                db.add(act)
                db.flush()
                for email in emails:
                    db.add(Participant(email=email, activity_id=act.id))
            db.commit()
    finally:
        db.close()


init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    db = SessionLocal()
    try:
        result = {}
        acts = db.query(Activity).all()
        for a in acts:
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": [p.email for p in a.participants]
            }
        return result
    finally:
        db.close()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Check already signed up
        exists = db.query(Participant).filter(Participant.activity_id == act.id, Participant.email == email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Enforce capacity
        current_count = db.query(Participant).filter(Participant.activity_id == act.id).count()
        if current_count >= act.max_participants:
            raise HTTPException(status_code=400, detail="Activity is at full capacity")

        db.add(Participant(email=email, activity_id=act.id))
        db.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")

        part = db.query(Participant).filter(Participant.activity_id == act.id, Participant.email == email).first()
        if not part:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        db.delete(part)
        db.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        db.close()
