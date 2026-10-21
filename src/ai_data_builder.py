from src.supabase_data import get_student_data
from src.ml.readiness_model import analyze_student_features
from src.skills.skill_gap import skill_gap
from src.analysis.performance_analysis import baseline_evidence


def build_ai_student_data(student_code: str):
    """
    Fetch student data from Supabase and convert it
    into a format suitable for AI/ML analysis.
    """

    data = get_student_data(student_code)

    academics = data["academics"]
    attendance = data["attendance"]
    skills = data["skills"]
    projects = data["projects"]
    certifications = data["certifications"]
    internships = data["internships"]
    achievements = data["achievements"]
    career_profile = data["career_profile"]

    cgpa_values = [
        float(row["cgpa"])
        for row in academics
        if row.get("cgpa") is not None
    ]

    cgpa = (
        sum(cgpa_values) / len(cgpa_values)
        if cgpa_values
        else 0.0
    )

    attendance_values = [
        float(row["attendance_percentage"])
        for row in attendance
        if row.get("attendance_percentage") is not None
    ]

    attendance_percentage = (
        sum(attendance_values) / len(attendance_values)
        if attendance_values
        else 0.0
    )

    student_skills = {}

    for row in skills:
        skill_name = row.get("skill_name")

        if not skill_name:
            continue

        skill_level = row.get("skill_level", 0)

        student_skills[str(skill_name).strip()] = int(
            skill_level
        )

    target_role = None

    if career_profile:
        career = career_profile[0]

        target_role = career.get("target_role")

        if not target_role:
            target_role = career.get("career_goal")

    return {
        "student_id": student_code,
        "cgpa": cgpa,
        "attendance_percentage": attendance_percentage,
        "project_count": len(projects),
        "certification_count": len(certifications),
        "internship_count": len(internships),
        "activity_count": len(achievements),
        "skills": student_skills,
        "career_goal": target_role,
    }


def analyze_student_from_supabase(student_code: str):
    """
    Run the existing ML readiness model using
    live student data from Supabase.
    """

    student_data = build_ai_student_data(student_code)

    ml_input = {
        "cgpa": student_data["cgpa"],
        "attendance_percentage": student_data[
            "attendance_percentage"
        ],
        "project_count": student_data["project_count"],
        "certification_count": student_data[
            "certification_count"
        ],
        "internship_count": student_data[
            "internship_count"
        ],
        "activity_count": student_data["activity_count"],
    }

    ml_result = analyze_student_features(
        student_id=student_code,
        student_data=ml_input,
    )

    return {
        **student_data,
        **ml_result,
    }


def build_complete_ai_analysis(student_code: str):
    """
    Generate the complete AI analysis for a student.

    Combines:
    1. Supabase student data
    2. Performance evidence
    3. ML readiness profiling
    4. Career-role skill-gap analysis
    5. Recommendations
    """

    student_data = build_ai_student_data(student_code)

    ml_input = {
        "cgpa": student_data["cgpa"],
        "attendance_percentage": student_data[
            "attendance_percentage"
        ],
        "project_count": student_data[
            "project_count"
        ],
        "certification_count": student_data[
            "certification_count"
        ],
        "internship_count": student_data[
            "internship_count"
        ],
        "activity_count": student_data[
            "activity_count"
        ],
    }

    # -----------------------------------------------------
    # Performance evidence
    # -----------------------------------------------------

    evidence = baseline_evidence(
        ml_input
    )

    # -----------------------------------------------------
    # ML readiness
    # -----------------------------------------------------

    ml_result = analyze_student_features(
        student_id=student_code,
        student_data=ml_input,
    )

    # -----------------------------------------------------
    # Career skill-gap analysis
    # -----------------------------------------------------

    if not student_data["career_goal"]:
        raise ValueError(
            f"No target career role found for student: "
            f"{student_code}"
        )

    gap_result = skill_gap(
        student_data["skills"],
        student_data["career_goal"],
    )

    # -----------------------------------------------------
    # Complete result
    # -----------------------------------------------------

    return {
        "student_id": student_code,

        "target_role": student_data[
            "career_goal"
        ],

        "evidence_count": int(
            evidence["evidence_count"]
        ),

        "evidence_level": str(
            evidence["evidence_level"]
        ),

        "evidence": {
            "cgpa": student_data["cgpa"],

            "attendance_percentage": student_data[
                "attendance_percentage"
            ],

            "project_count": student_data[
                "project_count"
            ],

            "certification_count": student_data[
                "certification_count"
            ],

            "internship_count": student_data[
                "internship_count"
            ],

            "activity_count": student_data[
                "activity_count"
            ],
        },

        "ml_cluster": int(
            ml_result["ml_cluster"]
        ),

        "ml_readiness_profile": str(
            ml_result["ml_readiness_profile"]
        ),

        "required_skills": gap_result[
            "required_skills"
        ],

        "matched_skills": gap_result[
            "matched_skills"
        ],

        "needs_improvement": gap_result[
            "needs_improvement"
        ],

        "missing_skills": gap_result[
            "missing_skills"
        ],

        "skill_comparison": gap_result[
            "skill_comparison"
        ],

        "priority": gap_result[
            "priority"
        ],

        "recommendations": gap_result[
            "recommendations"
        ],
    }