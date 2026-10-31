# One place for the "nearby cities" lookup. Keys and values are lowercase.
NEARBY_CITIES = {
    "colombo": ["dehiwala", "moratuwa", "kotte", "negombo"],
    "negombo": ["colombo", "gampaha", "ja-ela"],
    "gampaha": ["negombo", "ja-ela", "colombo"],
    "kandy": ["peradeniya", "katugastota", "gampola"],
    "galle": ["matara", "hikkaduwa", "ambalangoda"],
}


def nearby_cities(city):
    return NEARBY_CITIES.get(city.strip().lower(), [])