import pokebase as pb
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ..models import Pokemon
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_pokemon_details(pokemon_id: int) -> Dict[str, Any]:
    """Get pokemon details by id"""
    cache_key = f"pokemon_details_{pokemon_id}"
    result = cache.get(cache_key)

    if result:
        return result

    try:
        pokemon = get_object_or_404(Pokemon, api_id=pokemon_id)
        species = pb.pokemon_species(pokemon_id)

        evolution_data = get_evolution_chain(species.evolution_chain.id)

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
                {"name": ab.ability_name, "is_hidden": ab.is_hidden, "slot": ab.slot}
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
            "evolution_chain": evolution_data,
        }

        cache.set(cache_key, result, 3600)
        return result

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": True, "message": str(e)}


def get_evolution_chain(evolution_chain_id: int) -> Dict[str, Any]:
    """Evolution chain details"""
    try:
        cache_key = f"evolution_chain_{evolution_chain_id}"
        cached_evolution = cache.get(cache_key)

        if cached_evolution:
            return cached_evolution

        evolution_chain = pb.evolution_chain(evolution_chain_id)

        evolution_list = []

        def process_chain(chain_node, stage=1):
            species_name = chain_node.species.name
            species_id = int(chain_node.species.url.split("/")[-2])

            try:
                pokemon_db = Pokemon.objects.get(api_id=species_id)
                image_url = pokemon_db.sprite_url
                print(image_url)
            except Pokemon.DoesNotExist:
                pokemon_api = pb.pokemon(species_id)
                image_url = pokemon_api.sprites.front_default or ""

            evolution_list.append(
                {
                    "id": species_id,
                    "name": species_name,
                    "image_url": image_url,
                    "stage": stage,
                }
            )

            for evolution in chain_node.evolves_to:
                process_chain(evolution, stage + 1)

        process_chain(evolution_chain.chain)
        evolution_list.sort(key=lambda x: x["stage"])

        result = {
            "evolutions": evolution_list,
            "total_stages": (
                max([evo["stage"] for evo in evolution_list])
                if evolution_list
                else 1
            ),
        }

        cache.set(cache_key, result, 3600)
        return result

    except Exception as e:
        logger.error(f"Evolution error: {e}")
        return {"evolutions": [], "total_stages": 1}


def get_pokemon_comparison(pokemon1_id: int, pokemon2_id: int) -> Dict[str, Any]:
    """Compare two pokemon by their ids"""
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
