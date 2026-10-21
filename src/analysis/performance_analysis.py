from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "cgpa",
    "attendance_percentage",
    "project_count",
    "certification_count",
    "internship_count",
    "activity_count",
]


def validate_columns(df):
    """Validate that the required analysis columns exist."""

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def baseline_evidence(row):
    """
    Generate explainable readiness evidence.

    Academic evidence:
    CGPA >= 7.5 and attendance >= 75%

    Experience evidence:
    At least one project or internship

    Development evidence:
    At least one certification or activity
    """

    academic = (
        row["cgpa"] >= 7.5
        and row["attendance_percentage"] >= 75
    )

    experience = (
        row["project_count"] >= 1
        or row["internship_count"] >= 1
    )

    development = (
        row["certification_count"] >= 1
        or row["activity_count"] >= 1
    )

    count = sum(
        [
            academic,
            experience,
            development,
        ]
    )

    if count == 3:
        level = "strong"
    elif count == 2:
        level = "developing"
    else:
        level = "limited"

    return pd.Series(
        {
            "evidence_count": count,
            "evidence_level": level,
            "academic_evidence": academic,
            "experience_evidence": experience,
            "development_evidence": development,
        }
    )


def analyze(df):
    """Add explainable evidence to every student."""

    validate_columns(df)

    out = df.copy()

    evidence = out.apply(
        baseline_evidence,
        axis=1,
    )

    return pd.concat(
        [
            out,
            evidence,
        ],
        axis=1,
    )


def summarize(df):
    """Return an overall performance summary."""

    validate_columns(df)

    result = analyze(df)

    return {
        "student_count": int(
            len(result)
        ),
        "mean_cgpa": round(
            float(
                result["cgpa"].mean()
            ),
            2,
        ),
        "mean_attendance": round(
            float(
                result[
                    "attendance_percentage"
                ].mean()
            ),
            2,
        ),
        "evidence_levels": (
            result[
                "evidence_level"
            ]
            .value_counts()
            .to_dict()
        ),
    }


if __name__ == "__main__":

    root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    input_path = (
        root
        / "data"
        / "processed"
        / "students_features.csv"
    )

    df = pd.read_csv(
        input_path
    )

    result = analyze(df)

    output_path = (
        root
        / "data"
        / "processed"
        / "student_analysis.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output_path,
        index=False,
    )

    import json

    summary_path = (
        root
        / "data"
        / "processed"
        / "performance_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summarize(df),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        summarize(df)
    )