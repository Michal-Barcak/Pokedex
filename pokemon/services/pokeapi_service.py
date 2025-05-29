import requests
from ..models import Pokemon
import logging
from typing import List, Dict, Any
from ..background_jobs.pokemon_save_job import save_pokemon_list_async


logger = logging.getLogger(__name__)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
KANTO_POKEMON_LIMIT = 151
DEFAULT_PAGE_SIZE = 20

def get_pokemon_from_db(pokemon_range_start: int, pokemon_range_end: int) -> List[Pokemon]:
    return list(Pokemon.objects.filter(
        api_id__gte=pokemon_range_start, 
        api_id__lt=pokemon_range_end
    ).prefetch_related('types__type', 'abilities'))

def has_all_pokemon_in_db(existing_pokemon: List[Pokemon], expected_count: int) -> bool:
    return len(existing_pokemon) == expected_count

def create_response_from_db(existing_pokemon: List[Pokemon], page: int, per_page: int) -> Dict[str, Any]:
    pokemon_list = []
    for pokemon in existing_pokemon:
        pokemon_list.append({
            'id': pokemon.api_id,
            'name': pokemon.name,
            'sprite_url': pokemon.sprite_url,
            'types': [
                pokemon_type_relation.type.name 
                for pokemon_type_relation in pokemon.types.all()
            ],
            'abilities': [
                pokemon_ability.ability_name 
                for pokemon_ability in pokemon.abilities.all()
            ]
        })
    return create_page_response(pokemon_list, page, per_page, 'database')


def fetch_from_api_and_save(pokemon_range_start: int, pokemon_range_end: int, page: int, per_page: int) -> Dict[str, Any]:
    offset = pokemon_range_start - 1
    actual_limit = pokemon_range_end - pokemon_range_start
    try:
        with requests.Session() as session:
            pokemon_list_response = session.get(
                f"{POKEAPI_BASE_URL}/pokemon?limit={actual_limit}&offset={offset}"
            )
            pokemon_list_data = pokemon_list_response.json()
            display_pokemon_list = []
            background_save_data = []
            for pokemon_entry in pokemon_list_data['results']:
                pokemon_detail_response = session.get(pokemon_entry['url'])
                pokemon_detail_data = pokemon_detail_response.json()
                background_save_data.append(pokemon_detail_data)
                display_pokemon_list.append(format_pokemon_for_display(pokemon_detail_data))
            
            save_pokemon_list_async(background_save_data)
            return create_page_response(display_pokemon_list, page, per_page, 'api')
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        return create_page_response([], page, per_page, 'empty')

def format_pokemon_for_display(pokemon_detail_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': pokemon_detail_data['id'],
        'name': pokemon_detail_data['name'],
        'sprite_url': pokemon_detail_data['sprites']['front_default'] or '',
        'types': [type_info['type']['name'] for type_info in pokemon_detail_data['types']],
        'abilities': [
            ability_info['ability']['name'] 
            for ability_info in pokemon_detail_data['abilities'] 
            if not ability_info['is_hidden']
        ]
    }

def create_page_response(pokemon_list: List[Dict[str, Any]], page: int, per_page: int, data_source: str) -> Dict[str, Any]:
    total_pages = (KANTO_POKEMON_LIMIT + per_page - 1) // per_page
    return {
        'entries': pokemon_list,
        'current_page': page,
        'total_count': KANTO_POKEMON_LIMIT,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1,
        'data_source': data_source
    }
