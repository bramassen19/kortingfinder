import json
import requests
from bs4 import BeautifulSoup
import re
import openai
import os

# 🔐 API-sleutels
SERP_API_KEY = "ee016c0014f352b8633831e40522eabb5145bb14223f4e0a51b5317a31450bc8"
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📥 Inlezen bedrijvenlijst
with open("bedrijven.json", "r", encoding="utf-8") as f:
    bedrijven = json.load(f)

# 🔍 Stap 1: Nieuwsbriefkorting checken
def check_nieuwsbriefkorting(website):
    try:
        response = requests.get(website, timeout=10)
        if "nieuwsbrief" in response.text.lower() or "subscribe" in response.text.lower():
            return "10%"
    except:
        return None
    return None

# 🔍 Stap 2: Algemene kortingscode van site halen
def scrape_algemene_kortingscode(website):
    try:
        r = requests.get(website, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tekst = soup.get_text().lower()
        codes = re.findall(r"\b([A-Z0-9]{5,})\b", tekst)
        for code in codes:
            if "korting" in tekst or "discount" in tekst:
                return code.upper()
    except:
        return None
    return None

# 🔍 Stap 3: Influencers zoeken via Google
def zoek_influencers_links(bedrijfsnaam):
    query = f"{bedrijfsnaam} kortingscode site:instagram.com"
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
        title = res.get("title", "")
        link = res.get("link", "")
        if "instagram.com" in link:
            naam = title.split("-")[0].strip()
            influencers.append({"naam": naam, "link": link})
    return influencers[:5]

# 🔍 Stap 4: Bio uitlezen van Instagram-profiel (indien publiek)
def haal_instagram_bio(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(link, headers=headers, timeout=10)
        if r.status_code == 200:
            match = re.search(r'"biography":"(.*?)"', r.text)
            if match:
                return match.group(1).encode().decode("unicode_escape")
    except:
        return ""
    return ""

# 🧠 Stap 5: AI analyseert of bio een kortingscode bevat
def analyseer_bio_op_code(naam, bio, bedrijfsnaam):
    prompt = f"""
De volgende Instagram-bio is afkomstig van de influencer '{naam}'.
Bio: "{bio}"

Beoordeel of deze influencer een kortingscode aanbiedt voor het merk '{bedrijfsnaam}'.
Geef je antwoord als:

JA: [kortingscode]
of
NEE
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message["content"].strip()
    except:
        return "NEE"

# 🔁 Verwerk elk bedrijf
alle_resultaten = []

for bedrijf in bedrijven:
    naam = bedrijf["naam"]
    site = bedrijf.get("website") or bedrijf.get("bron")

    nieuwsbriefkorting = check_nieuwsbriefkorting(site)
    algemene_code = scrape_algemene_kortingscode(site)

    influencers = zoek_influencers_links(naam)
    relevante_influencers = []

    for inf in influencers:
        bio = haal_instagram_bio(inf["link"])
        if bio:
            analyse = analyseer_bio_op_code(inf["naam"], bio, naam)
            if analyse.startswith("JA"):
                code_match = re.search(r"[A-Z0-9]{4,}", analyse)
                code = code_match.group(0) if code_match else "onbekend"
                relevante_influencers.append(f"{inf['naam']}: {code}")

    # ⬇️ Format output per bedrijf
    resultaat = f"- {naam} biedt {nieuwsbriefkorting or 'geen'} korting voor het aanmelden voor de nieuwsbrief.\n"
    resultaat += "- Influencers/Ambassadeurs:\n"
    resultaat += "\n".join([f"  {ri}" for ri in relevante_influencers]) if relevante_influencers else "  Geen actieve codes gevonden"
    resultaat += f"\n\n- {naam} biedt de volgende code aan: {algemene_code or 'Geen'} via hun eigen site\n"

    alle_resultaten.append({"bedrijf": naam, "output": resultaat})

# 💾 Opslaan als JSON in Flutter-webmap
doelpad = os.path.join("build", "web", "kortingsresultaten_compleet.json")
os.makedirs(os.path.dirname(doelpad), exist_ok=True)

with open(doelpad, "w", encoding="utf-8") as f:
    json.dump(alle_resultaten, f, indent=2)

print(f"✅ Bestand opgeslagen als {doelpad}")
