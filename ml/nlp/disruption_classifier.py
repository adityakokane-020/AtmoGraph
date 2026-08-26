import re


# --------------------------------------------------
# Disruption keywords
# --------------------------------------------------

DISRUPTION_PATTERNS = {
    "Port Strike": [
        "strike",
        "workers strike",
        "port strike",
        "labor strike",
        "labour strike",
        "dock strike"
    ],

    "Port Closure": [
        "port closure",
        "port closed",
        "closed port",
        "port shutdown",
        "port shut down"
    ],

    "Port Congestion": [
        "port congestion",
        "congestion at port",
        "port delays",
        "port delay",
        "shipping congestion"
    ],

    "Natural Disaster": [
        "earthquake",
        "hurricane",
        "flood",
        "tsunami",
        "storm"
    ],

    "Fire": [
        "fire",
        "warehouse fire",
        "factory fire",
        "port fire"
    ]
}


# --------------------------------------------------
# Severity keywords
# --------------------------------------------------

HIGH_SEVERITY = [
    "major",
    "severe",
    "critical",
    "massive",
    "shutdown",
    "closed",
    "complete disruption"
]

MEDIUM_SEVERITY = [
    "significant",
    "moderate",
    "long delay",
    "disruption"
]

LOW_SEVERITY = [
    "minor",
    "small",
    "limited"
]


# --------------------------------------------------
# Detect disruption type
# --------------------------------------------------

def detect_disruption_type(text):

    text_lower = text.lower()

    for disruption_type, keywords in DISRUPTION_PATTERNS.items():

        for keyword in keywords:

            if keyword in text_lower:
                return disruption_type

    return "Unknown"


# --------------------------------------------------
# Detect severity
# --------------------------------------------------

def detect_severity(text):

    text_lower = text.lower()

    for keyword in HIGH_SEVERITY:

        if keyword in text_lower:
            return "High"

    for keyword in MEDIUM_SEVERITY:

        if keyword in text_lower:
            return "Medium"

    for keyword in LOW_SEVERITY:

        if keyword in text_lower:
            return "Low"

    # Default severity when disruption exists
    return "Medium"


# --------------------------------------------------
# Complete disruption analysis
# --------------------------------------------------

def analyze_disruption(text):

    disruption_type = detect_disruption_type(text)

    if disruption_type == "Unknown":

        return {
            "disruption_type": "Unknown",
            "severity": "None"
        }

    severity = detect_severity(text)

    return {
        "disruption_type": disruption_type,
        "severity": severity
    }


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    news = (
        "Workers announced a major strike at Rotterdam Port. "
        "The disruption may affect electronics shipments "
        "from Germany to North America."
    )

    result = analyze_disruption(news)

    print("===== AtmoGraph Disruption Detection =====")

    print("\nNews:")
    print(news)

    print("\nAnalysis:")

    print(
        "Disruption Type:",
        result["disruption_type"]
    )

    print(
        "Severity:",
        result["severity"]
    )

    print("\n===== Detection Complete =====")