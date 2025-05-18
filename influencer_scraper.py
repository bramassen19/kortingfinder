import json
import requests
import re
import openai

# API-sleutels
SERP_API_KEY = "ee016c0014f352b8633831e40522eabb5145bb14223f4e0a51b5317a31450bc8"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Bedrijven inladen
with open("bedrijven.json", "r") as f:
    bedrijven = json.load(f)

def zoek_influencers(bedrijfsnaam):
    query = f"{bedrijfsnaam} ambassador OR influencer site:instagram.com"
    params = {
        "q": query,
        "engine": "google",
        "api_key": SERP_API_KEY,
        "num": 10
    }
    r = requests.get("https://serpapi.com/search", params=params)
    data = r.json()

    influencers = []
    for res in data.get("organic_results", []):
        naam = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+)", res.get("title", ""))
        if naam:
            influencers.append({
                "naam": naam[0],
                "snippet": res.get("snippet", ""),
                "link": res.get("link", "")
            })
    return influencers[:3]

def analyseer_code_met_ai(naam, snippet):
    prompt = f"""
De influencer {naam} wordt genoemd met dit fragment: '{snippet}'.
Is dit iemand die op dit moment een kortingscode aanbiedt voor een merk? Antwoord alleen met:

JA: CODE
of
NEE
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message["content"].strip()

# Verzamelen
resultaten = []

for bedrijf in bedrijven:
    naam = bedrijf["naam"]
    influencers = zoek_influencers(naam)

    resultaat = {
        "bedrijf": naam,
        "influencers": []
    }

    for inf in influencers:
        analyse = analyseer_code_met_ai(inf["naam"], inf["snippet"])
        if analyse.startswith("JA"):
            code = re.search(r"[A-Z0-9]{4,}", analyse)
            resultaat["influencers"].append(f"{inf['naam']}: {code.group(0) if code else 'onbekend'}")

    if not resultaat["influencers"]:
        resultaat["influencers"].append("Geen actieve codes gevonden")

    resultaten.append(resultaat)

# Opslaan
with open("influencer_resultaten.json", "w") as f:
    json.dump(resultaten, f, indent=2)

print("✅ influencer_resultaten.json aangemaakt")
