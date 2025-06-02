from typing import Dict, Any
from ..models import (
    Pokemon,
    PokemonType,
    PokemonTypeRelation,
    PokemonAbility,
    PokemonStats,
)
from django.db import transaction, IntegrityError
import logging

logger = logging.getLogger(__name__)


def save_pokemon_to_db(pokemon_data: Dict[str, Any]) -> None:
    """Save pokemon to db with duplicate handling"""
    try:
        with transaction.atomic():
            # Create Pokemon
            pokemon_obj = Pokemon.objects.create(
                api_id=pokemon_data["id"],
                name=pokemon_data["name"],
                sprite_url=pokemon_data["sprites"]["front_default"] or "",
                height=pokemon_data["height"] / 10,  # decimetre -> metre
                weight=pokemon_data["weight"] / 10,  # hektogram -> kilogram
                base_experience=pokemon_data.get("base_experience"),
            )

            # Save types
            for type_data in pokemon_data["types"]:
                type_obj, _ = PokemonType.objects.get_or_create(
                    name=type_data["type"]["name"],
                    defaults={
                        "api_id": int(type_data["type"]["url"].split("/")[-2])
                    },
                )
                PokemonTypeRelation.objects.create(
                    pokemon=pokemon_obj, type=type_obj, slot=type_data["slot"]
                )

            processed_abilities = set()  # Track processed abilities
            for ability_data in pokemon_data["abilities"]:
                ability_name = ability_data["ability"]["name"]
                is_hidden = ability_data["is_hidden"]
                slot = ability_data["slot"]
                
                # Create unique key to avoid duplicates
                ability_key = (ability_name, is_hidden, slot)
                
                if ability_key not in processed_abilities:
                    try:
                        PokemonAbility.objects.create(
                            pokemon=pokemon_obj,
                            ability_name=ability_name,
                            is_hidden=is_hidden,
                            slot=slot,
                        )
                        processed_abilities.add(ability_key)
                    except IntegrityError:
                        # Skip duplicate ability
                        logger.warning(f"Duplicate ability {ability_name} for Pokemon {pokemon_obj.name}")
                        continue

            # Save stats
            for stat_data in pokemon_data["stats"]:
                PokemonStats.objects.create(
                    pokemon=pokemon_obj,
                    stat_name=stat_data["stat"]["name"],
                    base_stat=stat_data["base_stat"],
                    effort=stat_data["effort"],
                )

            logger.info(f"Successfully saved Pokemon: {pokemon_obj.name}")

    except IntegrityError as e:
        logger.error(f"IntegrityError saving Pokemon {pokemon_data.get('name', 'unknown')}: {e}")
        raise 
    except Exception as e:
        logger.error(f"Unexpected error saving Pokemon {pokemon_data.get('name', 'unknown')}: {e}")
        raise
