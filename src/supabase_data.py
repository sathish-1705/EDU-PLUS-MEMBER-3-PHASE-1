from src.supabase_client import supabase


def get_student_profile(student_code: str):
    response = (
        supabase
        .table("student_profiles")
        .select("*")
        .eq("student_code", student_code)
        .single()
        .execute()
    )

    return response.data


def get_student_data(student_code: str):
    profile = get_student_profile(student_code)

    if not profile:
        raise ValueError(f"Student not found: {student_code}")

    student_id = profile["id"]

    return {
        "profile": profile,

        "academics": (
            supabase
            .table("academics")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "attendance": (
            supabase
            .table("attendance")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "skills": (
            supabase
            .table("skills")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "projects": (
            supabase
            .table("projects")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "certifications": (
            supabase
            .table("certifications")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "internships": (
            supabase
            .table("internships")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "achievements": (
            supabase
            .table("achievements")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),

        "career_profile": (
            supabase
            .table("career_profiles")
            .select("*")
            .eq("student_id", student_id)
            .execute()
            .data
        ),
    }