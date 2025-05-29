import threading
import logging
from typing import List, Dict, Any
from ..models import Pokemon, PokemonType, PokemonTypeRelation, PokemonAbility

logger = logging.getLogger(__name__)

def save_pokemon_list_async(pokemon_data_list: List[Dict[str, Any]]) -> None:
    def save_pokemon_in_background():
        successful_saves = 0
        failed_saves = 0
        try:
            for pokemon_data in pokemon_data_list:
                try:
                    save_pokemon_to_db(pokemon_data)
                    successful_saves += 1
                except Exception as save_error:
                    failed_saves += 1
                    logger.error(
                        f"Error saving pokemon {pokemon_data.get('name', 'unknown')}: {save_error}"
                    )
            logger.info(
                f"Background save completed: {successful_saves} successful, {failed_saves} failed"
            )
        except Exception as general_error:
            logger.error(f"Critical error during background save: {general_error}")

    background_save_thread = threading.Thread(
        target=save_pokemon_in_background,
        name=f"PokemonSaveThread-{len(pokemon_data_list)}"
    )
    background_save_thread.daemon = True
    background_save_thread.start()

def save_pokemon_to_db(pokemon_data: Dict[str, Any]) -> None:
    try:
        pokemon_obj, created = Pokemon.objects.get_or_create(
            api_id=pokemon_data['id'],
            defaults={
                'name': pokemon_data['name'],
                'sprite_url': pokemon_data['sprites']['front_default'] or ''
            }
        )
        if created:
            # Save types
            for type_data in pokemon_data['types']:
                type_obj, _ = PokemonType.objects.get_or_create(
                    name=type_data['type']['name'],
                    defaults={'api_id': int(type_data['type']['url'].split('/')[-2])}
                )
                PokemonTypeRelation.objects.get_or_create(
                    pokemon=pokemon_obj,
                    type=type_obj,
                    slot=type_data['slot']
                )
            
            # Save abilities
            for ability_data in pokemon_data['abilities']:
                PokemonAbility.objects.get_or_create(
                    pokemon=pokemon_obj,
                    ability_name=ability_data['ability']['name'],
                    defaults={
                        'is_hidden': ability_data['is_hidden'],
                        'slot': ability_data['slot']
                    }
                )
            logger.info(f"Saved pokemon: {pokemon_obj.name}")
    except Exception as e:
        logger.error(f"Error saving pokemon to database: {e}")
