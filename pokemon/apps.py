# from django.apps import AppConfig


# class PokemonConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "pokemon"


from django.apps import AppConfig
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class PokemonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pokemon'
    
    def ready(self):
        """Spustí sa pri štarte Django aplikácie"""
        try:
            from .models import Pokemon
            pokemon_count = Pokemon.objects.count()
            
            if pokemon_count < 10:  # Ak máme menej ako 10 pokémonov
                logger.info("🔄 Spúšťam automatickú synchronizáciu pokémonov...")
                call_command('sync_pokemon', '--limit=151')
                logger.info("✅ Automatická synchronizácia dokončená")
            else:
                logger.info(f"ℹ️ Databáza už obsahuje {pokemon_count} pokémonov")
                
        except Exception as e:
            # Tabuľky ešte neexistujú alebo iná chyba
            logger.warning(f"⚠️ Nemôžem spustiť sync: {e}")
