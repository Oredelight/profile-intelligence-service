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
    if "female" in q:
        filters["gender"] = "female"
    elif "male" in q:
        filters["gender"] = "male"

    # Age group
    if "child" in q:
        filters["age_group"] = "child"
    elif "teenager" in q:
        filters["age_group"] = "teenager"
    elif "adult" in q:
        filters["age_group"] = "adult"
    elif "senior" in q:
        filters["age_group"] = "senior"

    # Young
    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # Above / below
    match = re.search(r"above (\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    match = re.search(r"below (\d+)", q)
    if match:
        filters["max_age"] = int(match.group(1))

    # Country
    for name, code in COUNTRY_KEYWORDS.items():
        if name in q:
            filters["country_id"] = code

    if not filters:
        return None

    return filters