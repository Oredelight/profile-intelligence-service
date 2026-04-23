import re

COUNTRY_KEYWORDS = {
    "nigeria": "NG",
    "kenya": "KE",
    "angola": "AO"
}

def parse_query(q: str):
    q = q.lower()
    filters = {}

    # Gender
    if "male" in q and "female" not in q:
        pass

    # Age group
    if "child" in q:
        filters["age_group"] = "child"
    elif "teen" in q:
        filters["age_group"] = "teenager"
    elif "adult" in q:
        filters["age_group"] = "adult"
    elif "senior" in q:
        filters["age_group"] = "senior"

    # Young (special rule)
    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # Above age
    import re
    match = re.search(r"above (\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    # Country
    countries = {
        "nigeria": "NG",
        "kenya": "KE",
        "angola": "AO"
    }

    for name, code in countries.items():
        if name in q:
            filters["country_id"] = code

    return filters if filters else None