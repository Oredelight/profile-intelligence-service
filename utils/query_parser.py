import re

def parse_query(q: str):
    q = q.lower().strip()
    words = q.split()

    filters = {}

    # HANDLE gender (ignore if both present)
    if "male" in words and "female" not in words:
        filters["gender"] = "male"
    elif "female" in words and "male" not in words:
        filters["gender"] = "female"

    # AGE GROUPS
    if "child" in words:
        filters["age_group"] = "child"
    elif "teenager" in words:
        filters["age_group"] = "teenager"
    elif "adult" in words:
        filters["age_group"] = "adult"
    elif "senior" in words:
        filters["age_group"] = "senior"

    # YOUNG SPECIAL RULE
    if "young" in words:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # ABOVE
    if "above" in words:
        try:
            idx = words.index("above")
            filters["min_age"] = int(words[idx + 1])
        except:
            return None

    # COUNTRY MAP
    countries = {
        "nigeria": "NG",
        "kenya": "KE",
        "angola": "AO"
    }

    for word in words:
        if word in countries:
            filters["country_id"] = countries[word]

    return filters if filters else None