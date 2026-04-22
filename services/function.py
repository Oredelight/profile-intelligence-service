import httpx
import asyncio

async def fetch_external_data(name: str):
    async with httpx.AsyncClient(timeout=10) as client:
        gender_res, age_res, country_res = await asyncio.gather(
            client.get(f"https://api.genderize.io?name={name}"),
            client.get(f"https://api.agify.io?name={name}"),
            client.get(f"https://api.nationalize.io?name={name}")
        )

    if gender_res.status_code != 200:
        raise Exception("Genderize")
    if age_res.status_code != 200:
        raise Exception("Agify")
    if country_res.status_code != 200:
        raise Exception("Nationalize")

    return (
        gender_res.json(),
        age_res.json(),
        country_res.json()
    )

def get_age_group(age: int) -> str:
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"
