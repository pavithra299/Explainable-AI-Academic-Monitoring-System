import joblib
import pandas as pd
model = joblib.load(
    "models/exam_score_model.pkl"
)

explainer = joblib.load(
    "models/shap_explainer.pkl"
)


FEATURE_ORDER = [
    "Hours_Studied",
    "Attendance",
    "Parental_Involvement",
    "Access_to_Resources",
    "Extracurricular_Activities",
    "Sleep_Hours",
    "Previous_Scores",
    "Motivation_Level",
    "Internet_Access",
    "Tutoring_Sessions",
    "Family_Income",
    "Teacher_Quality",
    "Peer_Influence",
    "Physical_Activity",
    "Learning_Disabilities",
    "Parental_Education_Level",
    "Distance_from_Home",
    "School_Type_Public",
    "Gender_Male"
]
ORDINAL_MAPPINGS = {
    "Parental_Involvement": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    },

    "Access_to_Resources": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    },

    "Motivation_Level": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    },

    "Family_Income": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    },

    "Teacher_Quality": {
        "Low": 0,
        "Medium": 1,
        "High": 2
    },

    "Peer_Influence": {
        "Negative": 0,
        "Neutral": 1,
        "Positive": 2
    },

    "Parental_Education_Level": {
        "High School": 1,
        "College": 2,
        "Postgraduate": 3
    },

    "Distance_from_Home": {
        "Near": 0,
        "Moderate": 1,
        "Far": 2
    }
}
BINARY_MAPPINGS = {
    "Extracurricular_Activities": {
        "No": 0,
        "Yes": 1
    },

    "Internet_Access": {
        "No": 0,
        "Yes": 1
    },

    "Learning_Disabilities": {
        "No": 0,
        "Yes": 1
    }
}
def encode_student_data(data):

    data = data.copy()

    # Ordinal Encoding
    for feature, mapping in ORDINAL_MAPPINGS.items():

        data[feature] = mapping[
            data[feature]
        ]

    # Binary Encoding
    for feature, mapping in BINARY_MAPPINGS.items():

        data[feature] = mapping[
            data[feature]
        ]

    # One-Hot Encoding
    data["School_Type_Public"] = (
        data.pop("School_Type") == "Public"
    )

    data["Gender_Male"] = (
        data.pop("Gender") == "Male"
    )

    return data
def predict_exam_score(student_data):

    encoded_data = encode_student_data(student_data)

    ordered_data = {
        feature: encoded_data[feature]
        for feature in FEATURE_ORDER
    }

    student_df = pd.DataFrame(
        [ordered_data]
    )

    prediction = model.predict(student_df)

    return round(prediction[0], 2)
def generate_shap_explanation(student_data):

    encoded_data = encode_student_data(student_data)

    ordered_data = {
        feature: encoded_data[feature]
        for feature in FEATURE_ORDER
    }

    student_df = pd.DataFrame(
        [ordered_data]
    )

    shap_values = explainer.shap_values(
        student_df
    )

    contributions = list(
        zip(
            FEATURE_ORDER,
            shap_values[0]
        )
    )

    positive = [
        (feature, value)
        for feature, value in contributions
        if value > 0
    ]

    negative = [
        (feature, value)
        for feature, value in contributions
        if value < 0
    ]

    positive.sort(
        key=lambda x: x[1],
        reverse=True
    )

    negative.sort(
        key=lambda x: x[1]
    )

    explanations = []

    explanations.append(
        "🟢 Positive Contributors"
    )

    if positive:

        for feature, value in positive[:2]:

            explanations.append(
                f"✓ {feature.replace('_', ' ')} improved the prediction."
            )

    else:

        explanations.append(
            "No major positive contributors identified."
        )


    explanations.append(
        "🔴 Negative Contributors"
    )

    if negative:

        for feature, value in negative[:2]:

            explanations.append(
                f"✗ {feature.replace('_', ' ')} reduced the prediction."
            )

    else:

        explanations.append(
            "No major negative contributors identified."
        )

    return explanations