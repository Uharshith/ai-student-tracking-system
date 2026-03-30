def generate_recommendation(prediction):

    if prediction == 0:
        return {
            "performance_level": "Low",
            "risk_level": "High",

            "student_recommendations": [
                "Your current academic indicators suggest a high risk of underperformance.",
                "It is strongly advised to improve attendance consistency above 75%.",
                "Prioritize clearing pending backlogs to avoid cumulative academic impact.",
                "Seek additional academic support sessions or faculty mentoring."
            ],

            "faculty_recommendations": [
                "Student shows high academic risk based on predictive indicators.",
                "Recommend one-on-one academic counseling.",
                "Monitor attendance trends weekly.",
                "Provide structured remedial guidance."
            ]
        }

    elif prediction == 1:
        return {
            "performance_level": "Medium",
            "risk_level": "Moderate",

            "student_recommendations": [
                "Academic performance is stable but requires improvement for higher outcomes.",
                "Focus on strengthening internal assessment consistency.",
                "Increase active participation in coursework and assignments.",
                "Aim to maintain attendance above 80%."
            ],

            "faculty_recommendations": [
                "Student demonstrates moderate performance stability.",
                "Encourage performance optimization strategies.",
                "Provide periodic feedback to boost academic consistency."
            ]
        }

    elif prediction == 2:
        return {
            "performance_level": "High",
            "risk_level": "Low",

            "student_recommendations": [
                "Excellent academic trajectory detected.",
                "Maintain consistency across attendance and assessments.",
                "Consider preparing for competitive academic opportunities.",
                "Engage in advanced academic enrichment programs."
            ],

            "faculty_recommendations": [
                "Student exhibits strong academic indicators.",
                "Encourage participation in advanced or research activities.",
                "Consider recommending for academic excellence programs."
            ]
        }

    else:
        return {
            "performance_level": "Unknown",
            "risk_level": "Unknown",
            "student_recommendations": [],
            "faculty_recommendations": []
        }
  