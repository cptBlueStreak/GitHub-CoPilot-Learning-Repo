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

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Train for inter-school soccer matches and improve team skills",
        "schedule": "Tuesdays, Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 18,
        "participants": ["nina@mergington.edu", "leon@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice drills, scrimmages, and basketball conditioning",
        "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
        "max_participants": 16,
        "participants": ["isabel@mergington.edu", "ryan@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "luke@mergington.edu"]
    },
    "Drama Club": {
        "description": "Rehearse scenes, work on performance skills, and produce school plays",
        "schedule": "Thursdays, 3:45 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["sophia@mergington.edu", "matt@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments, discuss scientific topics, and prepare for science fairs",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["julia@mergington.edu", "omar@mergington.edu"]
    },
    "Debate Team": {
        "description": "Practice arguments, research issues, and compete in debate tournaments",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["harper@mergington.edu", "noah@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate the student email is not already registered against the activity and that the activity is not full
    if email in activity["participants"]:   
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full") 
    
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def remove_participant(activity_name: str, email: str):
    """Remove/unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    normalized = email.strip().lower()
    # Find matching participant case-insensitively
    participants_lower = [p.lower() for p in activity.get("participants", [])]
    if normalized not in participants_lower:
        raise HTTPException(status_code=404, detail="Participant not found")

    idx = participants_lower.index(normalized)
    removed = activity["participants"].pop(idx)

    return {"message": f"Removed {removed} from {activity_name}"}
