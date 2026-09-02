import re


# --------------------------------------------------
# Severity Detection
# --------------------------------------------------

def detect_severity(text):
    """
    Detect disruption severity from news text.

    Returns:
        HIGH, MEDIUM, or LOW
    """

    text = str(text).lower()

    # HIGH severity keywords
    high_keywords = [
        "severe",
        "critical",
        "major",
        "massive",
        "extreme",
        "shutdown",
        "closed",
        "closure",
        "strike",
        "fire",
        "explosion",
        "destroyed",
        "halted",
        "completely disrupted",
        "complete disruption",
        "serious disruption"
    ]

    # LOW severity keywords
    low_keywords = [
        "minor",
        "slight",
        "small",
        "limited",
        "brief",
        "minor delay",
        "normal delay"
    ]

    # MEDIUM severity keywords
    medium_keywords = [
        "moderate",
        "significant",
        "delayed",
        "delay",
        "disruption",
        "restricted",
        "reduced",
        "slowdown",
        "congestion",
        "shortage",
        "temporary closure"
    ]

    # ----------------------------------------------
    # Check HIGH first
    # ----------------------------------------------

    for keyword in high_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            return "HIGH"

    # ----------------------------------------------
    # Check LOW before MEDIUM
    # ----------------------------------------------

    for keyword in low_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            return "LOW"

    # ----------------------------------------------
    # Check MEDIUM
    # ----------------------------------------------

    for keyword in medium_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            return "MEDIUM"

    # ----------------------------------------------
    # Default
    # ----------------------------------------------

    return "LOW"


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    test_news = [
        "Hamburg Port has been closed due to a severe operational disruption.",
        "Rotterdam Port is experiencing significant delays.",
        "The supplier reported a minor delay in shipment.",
        "Operations are running normally."
    ]

    print("===== AtmoGraph Severity Detection =====")

    for news in test_news:

        severity = detect_severity(news)

        print("\nNews:")
        print(news)

        print("Severity:", severity)

    print("\n===== Severity Detection Complete =====")