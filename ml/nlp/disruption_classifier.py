# --------------------------------------------------
# Disruption Detection
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
        "port shut down",
        "has been closed",
        "was closed"
    ],

    "Port Congestion": [
        "congestion",
        "port congestion",
        "congestion at port",
        "shipping congestion",
        "severe congestion",
        "heavy congestion"
    ],

    "Shipping Delay": [
        "shipping delay",
        "shipping delays",
        "shipment delay",
        "shipment delays",
        "shipping disruption",
        "shipping disruption",
        "operational delay",
        "long delay"
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
# Severity
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
    "disruption",
    "delay",
    "delays",
    "congestion"
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

    return "None"


# --------------------------------------------------
# Complete analysis
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

    test_cases = [

        "Workers announced a major strike at Rotterdam Port.",

        "Hamburg Port has been closed due to a severe operational disruption.",

        "Heavy congestion at Singapore Port is causing shipping delays.",

        "Mumbai Port is facing significant shipping delays.",

        "Global electronics companies reported strong quarterly sales."
    ]

    print("===== AtmoGraph Disruption Detection =====")

    for i, news in enumerate(test_cases, start=1):

        result = analyze_disruption(news)

        print(f"\nTest {i}:")
        print("News:", news)
        print("Disruption:", result["disruption_type"])
        print("Severity:", result["severity"])

    print("\n===== Detection Complete =====")