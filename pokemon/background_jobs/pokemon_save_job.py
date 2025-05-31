from typing import Dict, Any
from ..models import Pokemon, PokemonType, PokemonTypeRelation, PokemonAbility
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def save_pokemon_to_db(pokemon_data: Dict[str, Any]) -> None:
    try:
        with transaction.atomic():
            pokemon_obj = Pokemon.objects.create(
                api_id=pokemon_data["id"],
                name=pokemon_data["name"],
                sprite_url=pokemon_data["sprites"]["front_default"] or "",
                height=pokemon_data["height"] / 10,  # decimetre -> metre
                weight=pokemon_data["weight"] / 10,  # hektogram -> kilogram
                base_experience=pokemon_data.get("base_experience"),
            )
            
            for type_data in pokemon_data["types"]:
                type_obj, _ = PokemonType.objects.get_or_create(
                    name=type_data["type"]["name"],
                    defaults={
                        "api_id": int(type_data["type"]["url"].split("/")[-2])
                    },
                )
                PokemonTypeRelation.objects.create(
                    pokemon=pokemon_obj, 
                    type=type_obj, 
                    slot=type_data["slot"]
                )

            for ability_data in pokemon_data["abilities"]:
                PokemonAbility.objects.create(
                    pokemon=pokemon_obj,
                    ability_name=ability_data["ability"]["name"],
                    is_hidden=ability_data["is_hidden"],
                    slot=ability_data["slot"],
                )
                
            logger.info(f"Saved pokemon: {pokemon_obj.name}")
            
    except Exception as e:
        logger.error(f"Error saving pokemon to database: {e}")
