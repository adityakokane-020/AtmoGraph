
import re


def detect_disruption_type(text):
    """
    Detect supply-chain disruption type from news text.

    Types:
    - Port Closure
    - Port Strike
    - Port Congestion
    """

    text = text.lower()

    # -----------------------------
    # 1. PORT CLOSURE
    # -----------------------------
    closure_keywords = [
        "port closed",
        "port closure",
        "port has been closed",
        "port was closed",
        "port shutdown",
        "port shut down",
        "port halted",
        "port has halted",
        "port operations halted",
        "closed the port",
        "closure of the port"
        "operations have been halted",
        "operations halted",
        "port operations have been halted",
        "port operations halted",
    ]

    for keyword in closure_keywords:
        if keyword in text:
            return "Port Closure"

    # -----------------------------
    # 2. PORT STRIKE
    # -----------------------------
    strike_keywords = [
        "port strike",
        "port workers strike",
        "workers strike",
        "labor strike",
        "labour strike",
        "dockworkers strike",
        "dockworker strike",
        "strike at the port",
        "strike at port",
        "workers went on strike",
        "workers announced a strike"
    ]

    for keyword in strike_keywords:
        if keyword in text:
            return "Port Strike"

    # -----------------------------
    # 3. PORT CONGESTION
    # -----------------------------
    congestion_keywords = [
        "port congestion",
        "port is congested",
        "port congestion increased",
        "shipping congestion",
        "container congestion",
        "cargo congestion",
        "port backlog",
        "container backlog",
        "shipping backlog",
        "port slowdown",
        "shipping slowdown",
        "severe congestion",
        "heavy congestion"
    ]

    for keyword in congestion_keywords:
        if keyword in text:
            return "Port Congestion"

    # -----------------------------
    # 4. UNKNOWN
    # -----------------------------
    return "Unknown"


# -----------------------------------
# TEST
# -----------------------------------

if __name__ == "__main__":

    test_news = [
        "Rotterdam Port has been closed due to a severe operational disruption.",
        "Workers announced a strike at Rotterdam Port.",
        "Rotterdam Port is facing severe congestion and container backlog.",
        "Rotterdam Port operations have been halted.",
        "Shipping delays are increasing."
    ]

    print("\n===== Disruption Type Detection =====")

    for news in test_news:

        disruption_type = detect_disruption_type(news)

        print("\nNews:", news)
        print("Disruption Type:", disruption_type)
