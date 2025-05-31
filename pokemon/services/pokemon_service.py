import pokebase as pb
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ..models import Pokemon
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_pokemon_details(pokemon_id: int):
    """Jeden univerzálny formát pre všetky použitia"""
    cache_key = f"pokemon_details_{pokemon_id}"
    result = cache.get(cache_key)

    if result:
        return result

    try:
        pokemon = get_object_or_404(Pokemon, api_id=pokemon_id)
        species = pb.pokemon_species(pokemon_id)

        result = {
            "basic_info": {
                "id": pokemon.api_id,
                "name": pokemon.name,
                "height": pokemon.height,
                "weight": pokemon.weight,
                "base_experience": pokemon.base_experience,
            },
            "sprites": {
                "front_default": pokemon.sprite_url,
            },
            "types": [{"name": tr.type.name} for tr in pokemon.types.all()],
            "abilities": [
                {"name": ab.ability_name, "is_hidden": ab.is_hidden}
                for ab in pokemon.abilities.all()
            ],
            "stats": [
                {"name": stat.stat_name, "base_stat": stat.base_stat}
                for stat in pokemon.stats.all()
            ],
            "species_info": {
                "capture_rate": species.capture_rate,
                "is_legendary": species.is_legendary,
                "habitat": species.habitat.name if species.habitat else None,
            },
        }

        cache.set(cache_key, result, 3600)
        return result

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": True, "message": str(e)}


def get_pokemon_comparison(pokemon1_id: int, pokemon2_id: int) -> Dict[str, Any]:
    """Zjednodušená comparison - používa rovnaký formát"""
    cache_key = f"compare_{pokemon1_id}_{pokemon2_id}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    try:
        p1 = get_pokemon_details(pokemon1_id)
        p2 = get_pokemon_details(pokemon2_id)

        if p1.get("error") or p2.get("error"):
            return {"error": True}

        result = {
            "pokemon1": p1,
            "pokemon2": p2,
        }

        cache.set(cache_key, result, 3600)
        return result

    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return {"error": True}
