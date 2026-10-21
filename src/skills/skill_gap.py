import json
from pathlib import Path


RECOMMENDATIONS = {
    "Python": "Complete Python practice and build a small data or automation project.",
    "SQL": "Practice SQL queries and database exercises using progressively harder datasets.",
    "Pandas": "Work through Pandas exercises and build a small data-cleaning project.",
    "Power BI": "Create a dashboard project using a public or fictional dataset.",
    "Git": "Practice branching, commits, pull requests and conflict resolution.",
    "Java": "Build a small Java application covering core OOP concepts.",
    "Spring": "Build a small Spring REST service and document its endpoints.",
    "HTML": "Build a responsive multi-page HTML interface.",
    "CSS": "Practice responsive layouts and component styling.",
    "JavaScript": "Build an interactive browser project using JavaScript.",
    "React": "Create a small React application with reusable components.",
    "Node.js": "Build a small Node.js API and connect it to a database.",
    "NumPy": "Complete numerical computing exercises with NumPy.",
    "scikit-learn": "Build a small supervised-learning experiment and document evaluation.",
    "C": "Practice C programming with small systems-oriented exercises.",
    "C++": "Build a small C++ project using classes and standard library features.",
    "Embedded C": "Practice embedded C concepts with a simulated or supervised lab project.",
    "Arduino": "Build a simple Arduino prototype with documented code and testing.",
}


LEVEL_NAMES = {
    0: "Missing",
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
}


def load_taxonomy(path=None):
    """Load career-role skill requirements."""

    path = (
        Path(path)
        if path
        else Path(__file__).resolve().parents[2]
        / "data"
        / "skill_taxonomy.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Skill taxonomy not found: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def skill_gap(student_skills, target_role, taxonomy=None):
    """
    Compare student skills against the required skills
    for a selected career role.
    """

    taxonomy = taxonomy or load_taxonomy()

    if target_role not in taxonomy:
        raise ValueError(
            f"Unsupported target role: {target_role}"
        )

    role_data = taxonomy[target_role]

    # New taxonomy format:
    # {
    #     "Python": 2,
    #     "SQL": 2
    # }
    #
    # Backward compatibility:
    # ["Python", "SQL"]
    if isinstance(role_data, dict):
        required_levels = role_data
    else:
        required_levels = {
            skill: 1
            for skill in role_data
        }

    # Student skills can be supplied as:
    #
    # Old format:
    # ["Python", "SQL"]
    #
    # New format:
    # {
    #     "Python": 2,
    #     "SQL": 1
    # }
    if isinstance(student_skills, dict):
        current_levels = {}

        for skill, level in student_skills.items():
            skill_name = str(skill).strip()

            if not skill_name:
                continue

            try:
                numeric_level = int(level)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid skill level for {skill_name}"
                )

            if numeric_level < 0 or numeric_level > 3:
                raise ValueError(
                    f"Skill level for {skill_name} must be between 0 and 3"
                )

            current_levels[
                skill_name.lower()
            ] = numeric_level

        level_information_available = True

    else:
        current_levels = {
            str(skill).strip().lower(): None
            for skill in student_skills
            if skill and str(skill).strip()
        }

        level_information_available = False

    matched_skills = []
    needs_improvement = []
    missing_skills = []
    skill_comparison = []
    recommendations = []

    for skill, required_level in required_levels.items():

        if required_level not in LEVEL_NAMES:
            raise ValueError(
                f"Invalid required level for {skill}: "
                f"{required_level}"
            )

        current_level = current_levels.get(
            skill.lower(),
            0
        )

        # If the student has the skill but no level
        # was supplied, we cannot calculate a level gap.
        if current_level is None:
            gap = 0
        else:
            gap = max(
                int(required_level) - int(current_level),
                0
            )

        comparison = {
            "skill": skill,
            "current_level": current_level,
            "current_level_name": (
                "Level not provided"
                if current_level is None
                else LEVEL_NAMES[current_level]
            ),
            "required_level": int(required_level),
            "required_level_name": LEVEL_NAMES[
                required_level
            ],
            "gap": gap,
        }

        skill_comparison.append(comparison)

        # Skill is completely missing.
        if skill.lower() not in current_levels:

            missing_skills.append(skill)

            recommendations.append(
                RECOMMENDATIONS.get(
                    skill,
                    (
                        f"Improve your {skill} skills "
                        "through structured practice "
                        "and a practical project."
                    ),
                )
            )

        # Skill exists but is below the required level.
        elif (
            level_information_available
            and current_level < required_level
        ):

            needs_improvement.append(skill)

            recommendations.append(
                RECOMMENDATIONS.get(
                    skill,
                    (
                        f"Improve your {skill} skills "
                        "through structured practice "
                        "and a practical project."
                    ),
                )
            )

        # Skill meets or exceeds requirement.
        else:

            matched_skills.append(skill)

    total_gaps = (
        len(missing_skills)
        + len(needs_improvement)
    )

    if total_gaps == 0:
        priority = "low"
    elif len(missing_skills) > 2:
        priority = "high"
    else:
        priority = "medium"

    return {
        "target_role": target_role,
        "required_skills": list(
            required_levels.keys()
        ),
        "matched_skills": matched_skills,
        "needs_improvement": needs_improvement,
        "missing_skills": missing_skills,
        "skill_comparison": skill_comparison,
        "priority": priority,
        "recommendations": recommendations,
    }