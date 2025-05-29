from django.shortcuts import render
from .services.pokeapi_service import get_pokemon_from_db, fetch_from_api_and_save, has_all_pokemon_in_db, create_response_from_db
import logging

logger = logging.getLogger(__name__)

def pokemon(request):
    try:
        # Input validation - patrí do views
        page_number = int(request.GET.get('page', 1))
        if page_number < 1:
            page_number = 1
        
        per_page = 20
        
        pokemon_range_start = (page_number - 1) * per_page + 1
        pokemon_range_end = min(pokemon_range_start + per_page, 151 + 1)
        
        existing_pokemon = get_pokemon_from_db(pokemon_range_start, pokemon_range_end)
        expected_count = pokemon_range_end - pokemon_range_start
        
        if has_all_pokemon_in_db(existing_pokemon, expected_count):
            page_data = create_response_from_db(existing_pokemon, page_number, per_page)
        else:
            page_data = fetch_from_api_and_save(pokemon_range_start, pokemon_range_end, page_number, per_page)
        
        if not page_data['entries']:
            return render(request, 'pokemon/error.html', {
                'error': f'Page {page_number} contains no pokemon.'
            })
        
        return render(request, 'pokemon/pokemon.html', page_data)
        
    except Exception as e:
        logger.error(f"Error in pokemon view: {e}")
        return render(request, 'pokemon/error.html', {
            'error': 'An error occurred while loading pokemon.'
        })
