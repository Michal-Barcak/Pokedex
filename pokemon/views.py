from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Pokemon, PokemonType, PokemonAbility
from .services.pokemon_service import get_pokemon_details
import logging

logger = logging.getLogger(__name__)

def pokemon(request):
    try:
        page_number = int(request.GET.get("page", 1))
        pokemon_type = request.GET.get("type", "").strip().lower()
        pokemon_ability = request.GET.get("ability", "").strip().lower()
        
        if page_number < 1:
            page_number = 1

        per_page = 20
        offset = (page_number - 1) * per_page
        
        query_filter = Q()
        
        if pokemon_type:
            query_filter &= Q(types__type__name=pokemon_type)
        
        if pokemon_ability:
            query_filter &= Q(abilities__ability_name=pokemon_ability)
        
        pokemon_queryset = (
            Pokemon.objects
            .select_related()
            .prefetch_related("types__type", "abilities")
            .filter(query_filter)
            .order_by('api_id')
            .distinct()
        )
        available_types = PokemonType.objects.values_list('name', flat=True).order_by('name')
        available_abilities = PokemonAbility.objects.values_list('ability_name', flat=True).distinct().order_by('ability_name')

        total_count = pokemon_queryset.count()
        paginated_pokemon = list(pokemon_queryset[offset:offset + per_page])
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        context = {
            "pokemon_list": paginated_pokemon,
            "current_page": page_number,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page_number < total_pages,
            "has_previous": page_number > 1,
            "data_source": "database",
            "available_types": available_types,
            "available_abilities": available_abilities,
            "selected_type": pokemon_type,
            "selected_ability": pokemon_ability,
        }

        if not paginated_pokemon:
            return render(request, "pokemon/error.html", {"error": "No pokémon found."})

        return render(request, "pokemon/pokemon.html", context)

    except Exception as e:
        logger.error(f"Error in pokemon view: {e}")
        return render(request, "pokemon/error.html", {"error": "An error occurred."})

def pokemon_detail(request, pokemon_id):
    try:
        pokemon_details = get_pokemon_details(pokemon_id)
        
        if pokemon_details.get('error'):
            return render(request, 'pokemon/error.html', {
                'error': f"Could not load details for Pokémon #{pokemon_id}"
            })
        
        context = {
            'details': pokemon_details,
            'load_info': pokemon_details.get('load_info', {}),
        }
        
        return render(request, 'pokemon/pokemon_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in pokemon_detail view: {e}")
        return render(request, 'pokemon/error.html', {
            'error': "An error occurred while loading Pokémon details."
        })
