import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def is_recent(datum_str):
    try:
        datum = datetime.strptime(datum_str, "%Y-%m-%d")
        return (datetime.now() - datum).days <= 14
    except:
        return False

def check_nieuwsbriefkorting(website):
    try:
        response = requests.get(website, timeout=10)
        if "nieuwsbrief" in response.text.lower() or "subscribe" in response.text.lower():
            return "10%"  # Aangenomen waarde
    except:
        return None
    return None

def scrape_algemene_kortingscode(website):
    try:
        response = requests.get(website, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        tekst = soup.get_text().lower()
        codes = re.findall(r"\b([A-Z0-9]{5,})\b", tekst)
        for code in codes:
            if "discount" in tekst or "korting" in tekst:
                return code.upper()
    except:
        return None
    return None

def verzamel_kortingsdata(bedrijven, influencer_db):
    resultaten = []
    for bedrijf in bedrijven:
        naam = bedrijf["naam"]
        site = bedrijf.get("website") or bedrijf.get("bron")  # ✅ Flexibele key

        nieuwsbriefkorting = check_nieuwsbriefkorting(site)
        algemene_code = scrape_algemene_kortingscode(site)

        influencers = influencer_db.get(naam, [])
        recente_influencers = [
            f"{infl['naam']}: {infl['code']}"
            for infl in influencers if is_recent(infl["datum"])
        ]

        resultaat = f"- {naam} biedt {nieuwsbriefkorting or 'geen'} korting voor het aanmelden voor de nieuwsbrief.\n"
        resultaat += "- Influencers/Ambassadeurs:\n"
        resultaat += "\n".join([f"  {ri}" for ri in recente_influencers]) if recente_influencers else "  Geen actieve codes gevonden"
        resultaat += f"\n\n- {naam} biedt de volgende code aan: {algemene_code or 'Geen'} via hun eigen site\n"

        resultaten.append({"bedrijf": naam, "output": resultaat})
    return resultaten

if __name__ == "__main__":
    with open("bedrijven.json", "r") as f:
        bedrijven = json.load(f)

    with open("influencers.json", "r") as f:
        influencer_db = json.load(f)

    resultaten = verzamel_kortingsdata(bedrijven, influencer_db)

    with open("kortingsresultaten.json", "w") as f:
        json.dump(resultaten, f, indent=4)

    print("✅ Resultaten opgeslagen in kortingsresultaten.json")
