import re

COUNTRY_MAP = {
    "nigeria": "NG",
    "nigerian": "NG",
    "kenya": "KE",
    "kenyan": "KE",
    "angola": "AO",
    "angolan": "AO",
    "benin": "BJ",
    "beninese": "BJ",
    "ghana": "GH",
    "ghanaian": "GH",
    "south africa": "ZA",
    "south african": "ZA",
    "egypt": "EG",
    "egyptian": "EG",
    "morocco": "MA",
    "moroccan": "MA",
    "uganda": "UG",
    "ugandan": "UG",
    "tanzania": "TZ",
    "tanzanian": "TZ",
    "sudan": "SD",
    "sudanese": "SD",
    "united states": "US",
    "usa": "US",
    "united kingdom": "GB",
    "uk": "GB",
}

AGE_GROUP_MAP = {
    "child": "child",
    "children": "child",
    "teen": "teenager",
    "teenager": "teenager",
    "teenagers": "teenager",
    "adolescent": "teenager",
    "adult": "adult",
    "adults": "adult",
    "senior": "senior",
    "seniors": "senior",
    "elderly": "senior",
    "old": "senior",
}


def parse_query(q: str):
    """
    Parse natural language query into filters.
    Uses lenient matching: parses what it can, ignores unparseable fragments.
    
    Returns: dict with filters or None if nothing can be parsed
    """
    if not q:
        return None

    q_lower = q.lower().strip()
    filters = {}

    # Parse gender - use word boundaries to match female/females and male/males separately
    has_male = re.search(r'\bmales?\b', q_lower) is not None
    has_female = re.search(r'\bfemales?\b', q_lower) is not None

    if has_male and not has_female:
        filters["gender"] = "male"
    elif has_female and not has_male:
        filters["gender"] = "female"

    # Parse age groups
    for term, age_group in AGE_GROUP_MAP.items():
        if term in q_lower:
            filters["age_group"] = age_group
            break

    # Parse "young" - special case for age range
    if "young" in q_lower:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # Parse numeric age patterns
    # "above X" or "above X years" or "X and above"
    match = re.search(r"(?:above|over)\s+(\d+)", q_lower)
    if match:
        filters["min_age"] = int(match.group(1))

    # "below X" or "below X years" or "under X"
    match = re.search(r"(?:below|under)\s+(\d+)", q_lower)
    if match:
        filters["max_age"] = int(match.group(1))

    # "between X and Y"
    match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", q_lower)
    if match:
        filters["min_age"] = int(match.group(1))
        filters["max_age"] = int(match.group(2))

    # Parse countries - check multi-word countries first, then single words
    for country_name, code in COUNTRY_MAP.items():
        if country_name in q_lower:
            filters["country_id"] = code
            break

    # If we parsed nothing, return None
    return filters if filters else None
