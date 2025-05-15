
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai

# Voeg je eigen OpenAI API sleutel hier toe
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def check_code_via_ai(bedrijf, code):
    try:
        prompt = f"Is '{code}' een geldige kortingscode voor {bedrijf}? Beantwoord met 'JA' of 'NEE' en leg kort uit."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.5
        )
        antwoord = response.choices[0].message.content
        return "JA" in antwoord.upper()
    except Exception as e:
        return True  # Als AI faalt, gaan we door

def haal_codes_op_van_pagina(naam, url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        codes = set()
        for tag in soup.find_all(text=True):
            if any(w in tag.lower() for w in ["kortingscode", "code", "coupon"]):
                for stuk in tag.strip().split():
                    if len(stuk) >= 5 and stuk.isalnum():
                        codes.add(stuk.upper())
            if len(codes) >= 10:
                break
        gefilterd = []
        for code in list(codes):
            if check_code_via_ai(naam, code):
                gefilterd.append(code)
            if len(gefilterd) >= 5:
                break
        return [{"bedrijf": naam, "code": c, "geldig_tot": "", "bron": url} for c in gefilterd]
    except Exception:
        return [{"bedrijf": naam, "code": None, "geldig_tot": None, "bron": url, "opmerking": "Scraping mislukt"}]

# Simpele social media zoekopdracht (placeholder)
def zoek_social_codes(merknaam):
    zoekwoorden = f"{merknaam} kortingscode site:twitter.com"
    return [{"bedrijf": merknaam, "code": f"{merknaam.upper()}SOCIAL", "geldig_tot": "", "bron": "Twitter"}]

# Laad bedrijvenlijst
with open("bedrijven.json", "r") as f:
    bedrijven = json.load(f)

resultaten = []
for b in bedrijven:
    naam, bron = b["naam"], b["bron"]
    print(f"Scrapen: {naam}")
    resultaten += haal_codes_op_van_pagina(naam, bron)
    resultaten += zoek_social_codes(naam)

output = {
    "laatst_bijgewerkt": datetime.now().isoformat(),
    "kortingscodes": resultaten
}

with open("public/kortingscodes.json", "w") as f:
    json.dump(output, f, indent=2)
print("✅ AI-scraper klaar.")
