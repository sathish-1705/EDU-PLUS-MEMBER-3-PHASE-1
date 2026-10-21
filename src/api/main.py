from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.ai_data_builder import build_complete_ai_analysis
from src.analysis.performance_analysis import baseline_evidence
from src.ml.readiness_model import analyze_student
from src.skills.skill_gap import skill_gap


app = FastAPI(
    title="EDU PLUS Member 3 AI/ML API",
    version="1.0.0",
    description="Explainable student readiness and skill-gap analysis API.",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Supported career roles
# ---------------------------------------------------------

SUPPORTED_ROLES = {
    "Data Analyst",
    "Backend Developer",
    "Full Stack Developer",
    "Machine Learning Engineer",
    "Embedded Systems Engineer",
}


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class StudentReadinessRequest(BaseModel):
    student_id: str
    cgpa: float = Field(ge=0, le=10)
    attendance_percentage: float = Field(ge=0, le=100)
    skills: List[str]
    project_count: int = Field(ge=0)
    certification_count: int = Field(ge=0)
    internship_count: int = Field(ge=0)
    activity_count: int = Field(ge=0)
    career_goal: str


# ---------------------------------------------------------
# Response model
# ---------------------------------------------------------

class StudentReadinessResponse(BaseModel):
    student_id: str
    target_role: str
    evidence_count: int
    evidence_level: str
    ml_cluster: int
    ml_readiness_profile: str
    required_skills: List[str]
    matched_skills: List[str]
    needs_improvement: List[str]
    missing_skills: List[str]
    skill_comparison: List[dict]
    priority: str
    recommendations: List[str]


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "EDU PLUS Member 3 AI/ML API",
        "status": "running",
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# ML profile endpoint
# ---------------------------------------------------------

@app.get("/v1/student-readiness/ml-profile/{student_id}")
def get_ml_profile(student_id: str):

    try:
        return analyze_student(student_id)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


# ---------------------------------------------------------
# LIVE Supabase + AI/ML analysis
# ---------------------------------------------------------

@app.get("/v1/student-readiness/live/{student_code}")
def get_live_student_analysis(student_code: str):

    try:
        result = build_complete_ai_analysis(
            student_code
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ---------------------------------------------------------
# Manual analysis endpoint
# ---------------------------------------------------------

@app.post(
    "/v1/student-readiness/analyze",
    response_model=StudentReadinessResponse,
)
def analyze_student_readiness(
    request: StudentReadinessRequest
):

    if request.career_goal not in SUPPORTED_ROLES:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported career goal: "
                f"{request.career_goal}. "
                f"Supported roles: "
                f"{sorted(SUPPORTED_ROLES)}"
            ),
        )

    student_data = {
        "cgpa": request.cgpa,
        "attendance_percentage": request.attendance_percentage,
        "project_count": request.project_count,
        "certification_count": request.certification_count,
        "internship_count": request.internship_count,
        "activity_count": request.activity_count,
    }

    try:

        evidence = baseline_evidence(
            student_data
        )

        gap = skill_gap(
            request.skills,
            request.career_goal,
        )

        ml_profile = analyze_student(
            request.student_id
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return StudentReadinessResponse(
        student_id=request.student_id,

        target_role=request.career_goal,

        evidence_count=int(
            evidence["evidence_count"]
        ),

        evidence_level=str(
            evidence["evidence_level"]
        ),

        ml_cluster=int(
            ml_profile["ml_cluster"]
        ),

        ml_readiness_profile=str(
            ml_profile["ml_readiness_profile"]
        ),

        required_skills=gap[
            "required_skills"
        ],

        matched_skills=gap[
            "matched_skills"
        ],

        needs_improvement=gap[
            "needs_improvement"
        ],

        missing_skills=gap[
            "missing_skills"
        ],

        skill_comparison=gap[
            "skill_comparison"
        ],

        priority=gap[
            "priority"
        ],

        recommendations=gap[
            "recommendations"
        ],
    )