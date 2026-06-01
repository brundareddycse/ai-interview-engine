# Interview Routes - Core interview management endpoints
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()

class InterviewCreate(BaseModel):
    job_title: str
    job_description: str
    candidate_name: str
    candidate_resume: Optional[str] = None
    candidate_email: Optional[str] = None

class AnswerSubmit(BaseModel):
    question_id: str
    answer_text: str
    time_taken: int  # seconds

class InterviewResponse(BaseModel):
    interview_id: str
    status: str
    created_at: datetime
    current_question_number: int
    total_questions: int

class AnswerResponse(BaseModel):
    status: str
    score: float
    feedback: str
    dimension_scores: dict

# In-memory storage for demo (replace with database)
interviews_db = {}

@router.post("/create", response_model=InterviewResponse)
async def create_interview(data: InterviewCreate):
    """Create a new interview session"""
    interview_id = f"INT_{uuid.uuid4().hex[:8].upper()}"
    
    interview = {
        "interview_id": interview_id,
        "status": "started",
        "created_at": datetime.utcnow(),
        "candidate_name": data.candidate_name,
        "job_title": data.job_title,
        "job_description": data.job_description,
        "resume": data.candidate_resume,
        "current_question_number": 0,
        "total_questions": 0,
        "answers": [],
        "scores": []
    }
    
    interviews_db[interview_id] = interview
    
    return InterviewResponse(
        interview_id=interview_id,
        status="started",
        created_at=interview["created_at"],
        current_question_number=0,
        total_questions=0
    )

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: str):
    """Get interview session details"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = interviews_db[interview_id]
    return InterviewResponse(
        interview_id=interview_id,
        status=interview["status"],
        created_at=interview["created_at"],
        current_question_number=interview["current_question_number"],
        total_questions=interview["total_questions"]
    )

@router.post("/{interview_id}/submit-answer", response_model=AnswerResponse)
async def submit_answer(interview_id: str, data: AnswerSubmit):
    """Submit answer to current question"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = interviews_db[interview_id]
    
    # Store answer
    interview["answers"].append({
        "question_id": data.question_id,
        "answer_text": data.answer_text,
        "time_taken": data.time_taken,
        "submitted_at": datetime.utcnow()
    })
    
    # Simulate scoring
    base_score = 0.75
    time_penalty = 0.05 if data.time_taken > 300 else 0
    score = max(0.0, min(1.0, base_score - time_penalty))
    
    interview["scores"].append(score)
    interview["current_question_number"] += 1
    
    return AnswerResponse(
        status="answer_recorded",
        score=score,
        feedback="Good response. Consider providing more specific examples.",
        dimension_scores={
            "accuracy": 0.8,
            "clarity": 0.7,
            "depth": 0.75,
            "relevance": 0.8,
            "time_efficiency": 0.7
        }
    )

@router.get("/{interview_id}/status")
async def get_interview_status(interview_id: str):
    """Get current interview status"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = interviews_db[interview_id]
    avg_score = sum(interview["scores"]) / len(interview["scores"]) if interview["scores"] else 0
    
    return {
        "interview_id": interview_id,
        "status": interview["status"],
        "current_question": interview["current_question_number"],
        "total_answers": len(interview["answers"]),
        "average_score": avg_score,
        "candidate": interview["candidate_name"]
    }

@router.get("/{interview_id}/report")
async def get_interview_report(interview_id: str):
    """Get final interview report and readiness score"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = interviews_db[interview_id]
    
    # Calculate overall score
    scores = interview["scores"]
    overall_score = sum(scores) / len(scores) if scores else 0
    
    # Determine hiring recommendation
    if overall_score >= 0.8:
        recommendation = "STRONG_YES"
    elif overall_score >= 0.65:
        recommendation = "YES"
    elif overall_score >= 0.5:
        recommendation = "MAYBE"
    else:
        recommendation = "NO"
    
    return {
        "interview_id": interview_id,
        "candidate_name": interview["candidate_name"],
        "job_title": interview["job_title"],
        "overall_score": round(overall_score, 2),
        "hiring_recommendation": recommendation,
        "dimensions": {
            "technical": 0.75,
            "communication": 0.7,
            "problem_solving": 0.78,
            "cultural_fit": 0.72
        },
        "strengths": ["Good technical foundation", "Clear communication"],
        "weaknesses": ["Limited system design experience"],
        "feedback": "Strong candidate with good fundamentals",
        "total_questions": interview["current_question_number"],
        "completed_at": datetime.utcnow()
    }

@router.get("/")
async def list_interviews(limit: int = Query(10, ge=1, le=100)):
    """List recent interviews"""
    return {
        "total": len(interviews_db),
        "interviews": list(interviews_db.keys())[:limit]
    }
