# from django.apps import AppConfig


# class PokemonConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "pokemon"


from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)


class PokemonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pokemon"

    def ready(self):
        """Run during start Django app"""
        if len(sys.argv) > 1 and sys.argv[1] in [
            "makemigrations",
            "migrate",
            "shell",
            "test",
            "collectstatic",
            "check",
            "showmigrations",
        ]:
            return

        if len(sys.argv) > 1 and sys.argv[1] == "runserver":
            try:
                from .models import Pokemon

                pokemon_count = Pokemon.objects.count()

                if pokemon_count < 151:
                    logger.info("🔄 Starting automatic pokemon sync...")
                    from django.core.management import call_command

                    call_command("sync_pokemon", limit=151)
                    logger.info("✅ Automatic sync done")
                else:
                    logger.info(f"ℹ️ Database contains {pokemon_count} pokemons")

            except Exception as e:
                logger.warning(f"⚠️ Can not run sync: {e}")
