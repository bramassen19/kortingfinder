import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Bedrijvenlijst laden
with open("bedrijven.json", "r") as f:
    bedrijven = json.load(f)

def is_recent(datum):
    try:
        return (datetime.now() - datum).days <= 14
    except:
        return False

def ai_bevestiging(bedrijf, code):
    try:
        prompt = (
            f"De kortingscode '{code}' is aangetroffen voor het bedrijf '{bedrijf}'. "
            "Bevestig of dit een échte en werkende kortingscode is, gebaseerd op wat je weet. Antwoord alleen met JA of NEE."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        inhoud = response.choices[0].message.content.strip().upper()
        return "JA" in inhoud
    except:
        return False

def vind_kortingscodes_op_site(bedrijf, url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        teksten = soup.stripped_strings

        gevonden = set()
        for zin in teksten:
            if any(w in zin.lower() for w in ["kortingscode", "actiecode", "coupon", "code"]):
                woorden = zin.split()
                for woord in woorden:
                    if len(woord) >= 5 and woord.isalnum():
                        gevonden.add(woord.upper())
        return list(gevonden)
    except Exception as e:
        print(f"Fout bij {bedrijf}: {e}")
        return []

def scan_influencer_bios(accounts):
    resultaten = []
    for naam in accounts:
        # Dummy simulatie
        if "@" in naam:
            resultaten.append({"bron": f"bio van {naam}", "code": naam.replace("@", "")[:5].upper() + "10"})
    return resultaten

def genereer_json():
    alle_resultaten = []
    for bedrijf in bedrijven:
        naam = bedrijf.get("naam")
        print(f"Controleren: {naam}")

        # Bepaal URL-veld
        url = bedrijf.get("url") or bedrijf.get("bron")
        influencer_accounts = bedrijf.get("influencer_accounts", [])

        codes = []

        # 1. Webshop scraping
        if url:
            kandidaten = vind_kortingscodes_op_site(naam, url)
            for code in kandidaten:
                if ai_bevestiging(naam, code):
                    codes.append({
                        "bedrijf": naam,
                        "code": code,
                        "geldig_tot": "",
                        "bron": url
                    })
                    if len(codes) >= 5:
                        break

        # 2. Social media bios
        bios = scan_influencer_bios(influencer_accounts)
        for b in bios:
            c = b.get("code")
            if ai_bevestiging(naam, c):
                codes.append({
                    "bedrijf": naam,
                    "code": c,
                    "geldig_tot": "",
                    "bron": b["bron"]
                })
                if len(codes) >= 5:
                    break

        # 3. Geen codes gevonden
        if not codes:
            alle_resultaten.append({
                "bedrijf": naam,
                "bericht": f"Er zijn momenteel geen werkende kortingscodes voor {naam}. We blijven actief zoeken."
            })
        else:
            alle_resultaten.extend(codes)

    resultaat = {
        "laatst_bijgewerkt": datetime.utcnow().isoformat(),
        "kortingscodes": alle_resultaten
    }

    # Save JSON
    with open("public/kortingscodes.json", "w") as f:
        json.dump(resultaat, f, indent=2)

    print("✅ JSON opgeslagen in public/kortingscodes.json")

# Start script
if __name__ == "__main__":
    genereer_json()
