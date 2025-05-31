from django.shortcuts import render
from django.db.models import Q
from .models import Pokemon, PokemonType, PokemonAbility
from .services.pokemon_service import get_pokemon_details, get_pokemon_comparison
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
            Pokemon.objects.select_related()
            .prefetch_related("types__type", "abilities", "stats")
            .filter(query_filter)
            .order_by("api_id")
            .distinct()
        )
        available_types = list(
            PokemonType.objects.values_list("name", flat=True).order_by("name")
        )
        available_abilities = list(
            PokemonAbility.objects.values_list("ability_name", flat=True)
            .distinct()
            .order_by("ability_name")
        )

        total_count = pokemon_queryset.count()
        paginated_pokemon = list(pokemon_queryset[offset : offset + per_page])

        total_pages = (
            (total_count + per_page - 1) // per_page if total_count > 0 else 1
        )

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
            return render(
                request, "pokemon/error.html", {"error": "No pokémon found."}
            )

        return render(request, "pokemon/pokemon.html", context)

    except Exception as e:
        logger.error(f"Error in pokemon view: {e}")
        return render(request, "pokemon/error.html", {"error": "An error occurred."})


def pokemon_detail(request, pokemon_id):
    try:
        pokemon_details = get_pokemon_details(pokemon_id)

        if pokemon_details.get("error"):
            return render(
                request,
                "pokemon/error.html",
                {"error": f"Could not load details for Pokémon #{pokemon_id}"},
            )

        context = {
            "details": pokemon_details,
        }

        return render(request, "pokemon/pokemon_detail.html", context)

    except Exception as e:
        logger.error(f"Error in pokemon_detail view: {e}")
        return render(
            request,
            "pokemon/error.html",
            {"error": "An error occurred while loading Pokémon details."},
        )

def pokemon_comparison(request):
    """Bezpečné porovnanie pokémonov s proper validation"""
    try:
        p1_id = request.GET.get("pokemon1")
        p2_id = request.GET.get("pokemon2")

        if not p1_id or not p2_id:
            logger.warning("Missing pokemon parameters in comparison request")
            return render(
                request,
                "pokemon/error.html",
                {"error": "Missing pokemon parameters for comparison."},
            )

        try:
            p1_id = int(p1_id)
            p2_id = int(p2_id)

            if not (1 <= p1_id <= 151) or not (1 <= p2_id <= 151):
                logger.warning(f"Invalid pokemon IDs: {p1_id}, {p2_id}")
                return render(
                    request,
                    "pokemon/error.html",
                    {"error": "Pokemon IDs must be between 1 and 151."},
                )

            if p1_id == p2_id:
                return render(
                    request,
                    "pokemon/error.html",
                    {"error": "Cannot compare the same Pokémon."},
                )

        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid pokemon ID format: {e}")
            return render(
                request,
                "pokemon/error.html",
                {"error": "Invalid pokemon IDs provided."},
            )

        data = get_pokemon_comparison(p1_id, p2_id)

        if data.get("error"):
            logger.error(f"Comparison service error for {p1_id} vs {p2_id}")
            return render(
                request,
                "pokemon/error.html",
                {"error": "Could not compare these Pokémon."},
            )

        logger.info(f"Successful comparison: {p1_id} vs {p2_id}")
        return render(request, "pokemon/comparison.html", data)

    except Exception as e:
        logger.error(f"Unexpected error in comparison view: {e}")
        return render(
            request, "pokemon/error.html", {"error": "An unexpected error occurred."}
        )
