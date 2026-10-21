from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "cgpa",
    "attendance_percentage",
    "project_count",
    "certification_count",
    "internship_count",
    "activity_count",
]


def load_student_data(path=None):
    """Load the fictional student dataset used for ML profiling."""

    if path is None:
        path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "raw"
            / "students.csv"
        )

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Student dataset not found: {path}"
        )

    return pd.read_csv(path)


def prepare_features(df):
    """Prepare numeric features for ML analysis."""

    missing = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required ML features: {missing}"
        )

    return df[FEATURE_COLUMNS].astype(float)


def build_readiness_model(df):
    """
    Train the KMeans readiness profiling model.

    The model uses standardized student-development features.
    """

    features = prepare_features(df)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    model = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=20
    )

    clusters = model.fit_predict(scaled_features)

    return scaler, model, clusters, scaled_features


def calculate_readiness_profiles(df):
    """
    Group students into three data-driven readiness profiles.

    This is unsupervised profiling, not predictive career forecasting.
    """

    result = df.copy()

    scaler, model, clusters, scaled_features = build_readiness_model(df)

    result["ml_cluster"] = clusters

    # Calculate cluster scores using standardized features
    # so that CGPA, attendance, projects, etc. contribute
    # on comparable scales.
    scaled_df = pd.DataFrame(
        scaled_features,
        columns=FEATURE_COLUMNS,
        index=result.index
    )

    scaled_df["ml_cluster"] = clusters

    cluster_scores = (
        scaled_df
        .groupby("ml_cluster")[FEATURE_COLUMNS]
        .mean()
        .mean(axis=1)
    )

    ordered_clusters = cluster_scores.sort_values().index.tolist()

    profile_mapping = {
        ordered_clusters[0]: "Developing",
        ordered_clusters[1]: "Emerging",
        ordered_clusters[2]: "Ready",
    }

    result["ml_readiness_profile"] = result["ml_cluster"].map(
        profile_mapping
    )

    return result


def analyze_student(student_id, df=None):
    """
    Return the ML readiness profile for a student
    already present in the prototype dataset.
    """

    if df is None:
        df = load_student_data()

    result = calculate_readiness_profiles(df)

    student = result[
        result["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:
        raise ValueError(
            f"Student not found: {student_id}"
        )

    row = student.iloc[0]

    return {
        "student_id": str(row["student_id"]),
        "ml_cluster": int(row["ml_cluster"]),
        "ml_readiness_profile": str(
            row["ml_readiness_profile"]
        ),
    }


def analyze_student_features(
    student_id,
    student_data,
    df=None
):
    """
    Calculate the ML readiness profile for a provided student.

    The submitted student does not need to exist in the
    prototype dataset. The prototype dataset is used as the
    reference population for the KMeans model.
    """

    if df is None:
        df = load_student_data()

    # Train the readiness model using the reference dataset.
    scaler, model, clusters, scaled_features = build_readiness_model(df)

    # Determine readiness labels from the reference population.
    scaled_df = pd.DataFrame(
        scaled_features,
        columns=FEATURE_COLUMNS
    )

    scaled_df["ml_cluster"] = clusters

    cluster_scores = (
        scaled_df
        .groupby("ml_cluster")[FEATURE_COLUMNS]
        .mean()
        .mean(axis=1)
    )

    ordered_clusters = cluster_scores.sort_values().index.tolist()

    profile_mapping = {
        ordered_clusters[0]: "Developing",
        ordered_clusters[1]: "Emerging",
        ordered_clusters[2]: "Ready",
    }

    # Convert submitted student information into the same
    # feature structure used to train the model.
    student_frame = pd.DataFrame(
        [
            {
                column: float(student_data[column])
                for column in FEATURE_COLUMNS
            }
        ]
    )

    student_features = prepare_features(student_frame)

    # Scale the submitted student's features using the scaler
    # fitted on the reference dataset.
    scaled_student = scaler.transform(student_features)

    # Predict the nearest KMeans cluster.
    predicted_cluster = int(
        model.predict(scaled_student)[0]
    )

    return {
        "student_id": str(student_id),
        "ml_cluster": predicted_cluster,
        "ml_readiness_profile": profile_mapping[
            predicted_cluster
        ],
    }


if __name__ == "__main__":
    df = load_student_data()

    result = calculate_readiness_profiles(df)

    output_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "processed"
        / "ml_readiness_profiles.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        output_path,
        index=False
    )

    print(
        f"ML readiness profiles written to: {output_path}"
    )