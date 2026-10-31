"""Sri Lankan districts and main towns (one place for every city dropdown)."""

DISTRICTS = {
    "Colombo": ["Colombo", "Dehiwala-Mount Lavinia", "Moratuwa", "Sri Jayawardenepura Kotte",
                "Maharagama", "Nugegoda", "Kesbewa", "Piliyandala", "Homagama", "Kaduwela",
                "Avissawella", "Boralesgamuwa", "Kolonnawa"],
    "Gampaha": ["Gampaha", "Negombo", "Ja-Ela", "Wattala", "Kelaniya", "Ragama", "Katunayake",
                "Minuwangoda", "Veyangoda", "Nittambuwa", "Divulapitiya"],
    "Kalutara": ["Kalutara", "Panadura", "Horana", "Beruwala", "Aluthgama", "Matugama",
                 "Bandaragama"],
    "Kandy": ["Kandy", "Peradeniya", "Katugastota", "Kundasale", "Gampola", "Nawalapitiya",
              "Akurana"],
    "Matale": ["Matale", "Dambulla", "Sigiriya", "Rattota", "Ukuwela"],
    "Nuwara Eliya": ["Nuwara Eliya", "Hatton", "Talawakele", "Ginigathhena"],
    "Galle": ["Galle", "Hikkaduwa", "Ambalangoda", "Elpitiya", "Baddegama"],
    "Matara": ["Matara", "Weligama", "Dikwella", "Akuressa", "Hakmana"],
    "Hambantota": ["Hambantota", "Tangalle", "Tissamaharama", "Ambalantota", "Beliatta"],
    "Jaffna": ["Jaffna", "Chavakachcheri", "Point Pedro", "Nallur"],
    "Kilinochchi": ["Kilinochchi"],
    "Mannar": ["Mannar"],
    "Vavuniya": ["Vavuniya"],
    "Mullaitivu": ["Mullaitivu"],
    "Batticaloa": ["Batticaloa", "Kattankudy", "Eravur"],
    "Ampara": ["Ampara", "Kalmunai", "Akkaraipattu", "Sammanthurai"],
    "Trincomalee": ["Trincomalee", "Kinniya", "Mutur"],
    "Kurunegala": ["Kurunegala", "Kuliyapitiya", "Narammala", "Pannala", "Mawathagama"],
    "Puttalam": ["Puttalam", "Chilaw", "Wennappuwa", "Nattandiya"],
    "Anuradhapura": ["Anuradhapura", "Kekirawa", "Tambuttegama", "Eppawala"],
    "Polonnaruwa": ["Polonnaruwa", "Hingurakgoda", "Medirigiriya"],
    "Badulla": ["Badulla", "Bandarawela", "Haputale", "Welimada", "Mahiyanganaya"],
    "Monaragala": ["Monaragala", "Wellawaya", "Bibile"],
    "Ratnapura": ["Ratnapura", "Embilipitiya", "Balangoda", "Pelmadulla"],
    "Kegalle": ["Kegalle", "Mawanella", "Warakapola", "Rambukkana"],
}

CITY_CHOICES = sorted((t, t) for towns in DISTRICTS.values() for t in towns)
DISTRICT_CHOICES = sorted((d, d) for d in DISTRICTS)
CITY_TO_DISTRICT = {t: d for d, towns in DISTRICTS.items() for t in towns}