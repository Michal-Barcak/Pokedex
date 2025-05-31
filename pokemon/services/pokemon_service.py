import pokebase as pb
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ..models import Pokemon
import logging

logger = logging.getLogger(__name__)

def get_pokemon_details(pokemon_id: int):
    """Získa pokémon detaily s len 1 API call"""
    cache_key = f'pokemon_details_{pokemon_id}'
    
    result = cache.get(cache_key)
    if result:
        result['load_info'] = {'source': 'cache'}
        return result
    
    try:
        pokemon = get_object_or_404(Pokemon, api_id=pokemon_id)
        species = pb.pokemon_species(pokemon_id)
        
        result = {
            'basic_info': {
                'id': pokemon.api_id,
                'name': pokemon.name,
                'height': pokemon.height,
                'weight': pokemon.weight,
                'base_experience': pokemon.base_experience,
            },
            'sprites': {
                'front_default': pokemon.sprite_url,
                'front_shiny': None,
            },
            'types': [{'name': tr.type.name} for tr in pokemon.types.all()],
            'abilities': [
                {'name': ab.ability_name, 'is_hidden': ab.is_hidden} 
                for ab in pokemon.abilities.all()
            ],
            'stats': [],
            'species_info': {
                'capture_rate': species.capture_rate,
                'is_legendary': species.is_legendary,
                'habitat': species.habitat.name if species.habitat else None,
            },
            'load_info': {'source': 'hybrid'}
        }
        
        cache.set(cache_key, result, 3600)
        return result
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'error': True, 'message': str(e)}
