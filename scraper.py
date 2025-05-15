import json
from datetime import datetime

kortingscodes = [
    {"bedrijf": "Zalando", "code": "ZALANDODEAL10", "geldig_tot": "2025-06-01"},
    {"bedrijf": "Thuisbezorgd", "code": "ETEN5EURO", "geldig_tot": "2025-05-30"},
    {"bedrijf": "Coolblue", "code": "KOEL2025", "geldig_tot": "2025-06-15"},
]

bestandspad = "public/kortingscodes.json"
with open(bestandspad, "w") as f:
    json.dump({
        "laatst_bijgewerkt": datetime.utcnow().isoformat(),
        "kortingscodes": kortingscodes
    }, f, indent=2)

print(f"JSON gegenereerd: {bestandspad}")
