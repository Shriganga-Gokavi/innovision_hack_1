import datetime


def get_dynamic_background():
    """Return time-based background style info."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return {
            "time": "morning",
            "greeting": "Good Morning ☀️",
            "style": "background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 30%, #ff9a9e 70%, #fecfef 100%);"
        }
    elif 12 <= hour < 17:
        return {
            "time": "afternoon",
            "greeting": "Good Afternoon 🌤️",
            "style": "background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 40%, #d4fc79 80%, #96e6a1 100%);"
        }
    elif 17 <= hour < 21:
        return {
            "time": "evening",
            "greeting": "Good Evening 🌇",
            "style": "background: linear-gradient(135deg, #f093fb 0%, #f5576c 30%, #fda085 60%, #f6d365 100%);"
        }
    else:
        return {
            "time": "night",
            "greeting": "Good Night 🌙",
            "style": "background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);"
        }
