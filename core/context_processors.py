from .models import is_dengue_mode


def dengue(request):
    return {"dengue_mode": is_dengue_mode()}