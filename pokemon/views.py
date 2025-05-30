from django.shortcuts import render
from django.db.models import Q
from .models import Pokemon, PokemonType, PokemonAbility
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
        
        # Vytvorenie Q filtra
        query_filter = Q()
        
        if pokemon_type:
            query_filter &= Q(types__type__name=pokemon_type)
        
        if pokemon_ability:
            query_filter &= Q(abilities__ability_name=pokemon_ability)
        
        # Optimalizovaný queryset s prefetch_related
        pokemon_queryset = (
            Pokemon.objects
            .select_related()
            .prefetch_related("types__type", "abilities")  # Kľúčová optimalizácia
            .filter(query_filter)
            .order_by('api_id')
            .distinct()
        )
        
        total_count = pokemon_queryset.count()
        paginated_pokemon = pokemon_queryset[offset:offset + per_page]
        
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # Vytvorenie context pre template
        context = {
            "pokemon_list": list(paginated_pokemon),  # Priamo queryset
            "current_page": page_number,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page_number < total_pages,
            "has_previous": page_number > 1,
            "data_source": "database",
            "available_types": PokemonType.objects.values_list('name', flat=True).order_by('name'),
            "available_abilities": PokemonAbility.objects.values_list('ability_name', flat=True).distinct().order_by('ability_name'),
            "selected_type": pokemon_type,
            "selected_ability": pokemon_ability,
        }

        if not paginated_pokemon:
            return render(request, "pokemon/error.html", {"error": "No pokémon found."})

        return render(request, "pokemon/pokemon.html", context)

    except Exception as e:
        logger.error(f"Error in pokemon view: {e}")
        return render(request, "pokemon/error.html", {"error": "An error occurred."})
