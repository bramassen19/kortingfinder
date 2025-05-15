
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Bedrijvenlijst inladen
with open("bedrijven.json", "r") as f:
    bedrijven = json.load(f)

def haal_kortingscodes_op(naam, url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Zoek op patronen zoals 'Kortingscode: ABC123'
        codes = set()
        for tag in soup.find_all(text=True):
            if any(woord in tag.lower() for woord in ["kortingscode", "code", "coupon"]):
                code_fragmenten = tag.strip().split()
                for frag in code_fragmenten:
                    if len(frag) >= 5 and frag.isalnum() and not frag.isdigit():
                        codes.add(frag.upper())
            if len(codes) >= 5:
                break

        if codes:
            return [{"bedrijf": naam, "code": code, "geldig_tot": "", "bron": url} for code in list(codes)[:5]]
        else:
            return [{"bedrijf": naam, "code": None, "geldig_tot": None, "bron": url}]
    except Exception as e:
        return [{"bedrijf": naam, "code": None, "geldig_tot": None, "bron": url, "opmerking": "Kon niet scrapen"}]

alle_codes = []
for bedrijf in bedrijven:
    naam = bedrijf["naam"]
    url = bedrijf["bron"]
    print(f"Scrapen: {naam} ({url})")
    resultaten = haal_kortingscodes_op(naam, url)
    alle_codes.extend(resultaten)

output = {
    "laatst_bijgewerkt": datetime.now().isoformat(),
    "kortingscodes": alle_codes
}

with open("public/kortingscodes.json", "w") as f:
    json.dump(output, f, indent=2)
print("✅ kortingscodes.json succesvol gegenereerd.")
