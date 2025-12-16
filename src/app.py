"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta

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

# --- Audit Log Configuration ---
# Privacy-aware settings: configure retention period (in days)
AUDIT_LOG_RETENTION_DAYS = int(os.environ.get("AUDIT_LOG_RETENTION_DAYS", "90"))  # Default 90 days


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)

    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)

    activity = relationship("Activity", back_populates="participants")

    __table_args__ = (
        UniqueConstraint("email", "activity_id", name="uq_participant_email_activity"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String, nullable=False)  # signup, unregister, upload, check-in
    user_email = Column(String, nullable=False)
    activity_name = Column(String, nullable=True)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)


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
                ("Manga Maniacs", "Explore the fantastic stories of the most peculiar characters from Japanese Manga (graphic novels).", "Tuesdays, 7:00 PM - 8:00 PM", 15,
                 []),
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


# --- Audit Logging Helper Functions ---
def log_audit_event(db, action: str, user_email: str, activity_name: str = None, details: str = None, ip_address: str = None):
    """Create an audit log entry"""
    audit_log = AuditLog(
        timestamp=datetime.utcnow(),
        action=action,
        user_email=user_email,
        activity_name=activity_name,
        details=details,
        ip_address=ip_address
    )
    db.add(audit_log)
    db.commit()


def cleanup_old_audit_logs():
    """Remove audit logs older than the retention period"""
    if AUDIT_LOG_RETENTION_DAYS <= 0:
        return  # Retention disabled
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=AUDIT_LOG_RETENTION_DAYS)
        deleted = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
        db.commit()
        return deleted
    finally:
        db.close()


# --- Minimal Auth & Roles ---
security = HTTPBearer(auto_error=False)

# For simplicity, use static tokens mapped to roles. In a future change, replace with proper user DB.
TOKENS = {
    # student token(s)
    "student-token-123": "student",
    # organizer token(s)
    "organizer-token-abc": "organizer",
    # admin token(s)
    "admin-token-xyz": "admin",
}


def get_current_role(creds: HTTPAuthorizationCredentials = Depends(security)):
    if not creds:
        return None
    token = creds.credentials
    return TOKENS.get(token)


@app.post("/login")
def login(username: str, role: str):
    """Return a static token for demo purposes based on requested role."""
    if role not in {"student", "organizer", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    # In a real system, verify username/password and issue JWT.
    for t, r in TOKENS.items():
        if r == role:
            return {"token": t, "role": r}
    raise HTTPException(status_code=500, detail="No token configured for role")


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
def signup_for_activity(activity_name: str, email: str, role: str | None = Depends(get_current_role)):
    """Sign up a student for an activity"""
    # If auth provided, ensure role is student
    if role and role != "student":
        raise HTTPException(status_code=403, detail="Only students can sign up")
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
        
        # Log the audit event
        log_audit_event(db, "signup", email, activity_name, f"Student signed up for {activity_name}")
        
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, role: str | None = Depends(get_current_role)):
    """Unregister a student from an activity"""
    # If auth provided, ensure role is organizer (management action)
    if role and role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can manage registrations")
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
        
        # Log the audit event
        log_audit_event(db, "unregister", email, activity_name, f"Student unregistered from {activity_name}")
        
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        db.close()


# --- Admin Endpoints ---
@app.get("/admin/audit-logs")
def get_audit_logs(role: str | None = Depends(get_current_role), limit: int = 100, offset: int = 0):
    """Get audit logs - admin only"""
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = SessionLocal()
    try:
        # Clean up old logs first
        cleanup_old_audit_logs()
        
        # Get logs with pagination
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()
        total = db.query(AuditLog).count()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "user_email": log.user_email,
                    "activity_name": log.activity_name,
                    "details": log.details,
                    "ip_address": log.ip_address
                }
                for log in logs
            ]
        }
    finally:
        db.close()


@app.get("/admin/audit-logs/export")
def export_audit_logs(role: str | None = Depends(get_current_role)):
    """Export audit logs as CSV - admin only"""
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["ID", "Timestamp", "Action", "User Email", "Activity Name", "Details", "IP Address"])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat(),
                log.action,
                log.user_email,
                log.activity_name or "",
                log.details or "",
                log.ip_address or ""
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )
    finally:
        db.close()


@app.get("/admin/audit-logs/stats")
def get_audit_stats(role: str | None = Depends(get_current_role)):
    """Get audit log statistics - admin only"""
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = SessionLocal()
    try:
        total_logs = db.query(AuditLog).count()
        
        # Count by action type
        from sqlalchemy import func
        action_counts = db.query(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action).all()
        
        # Get date range
        oldest_log = db.query(AuditLog).order_by(AuditLog.timestamp.asc()).first()
        newest_log = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        
        return {
            "total_logs": total_logs,
            "action_counts": {action: count for action, count in action_counts},
            "retention_days": AUDIT_LOG_RETENTION_DAYS,
            "oldest_log": oldest_log.timestamp.isoformat() if oldest_log else None,
            "newest_log": newest_log.timestamp.isoformat() if newest_log else None
        }
    finally:
        db.close()
