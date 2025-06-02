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
            "sync_pokemon",
        ]:
            return

        if len(sys.argv) > 1 and sys.argv[1] == "runserver":
            try:
                from .models import Pokemon

                pokemon_count = Pokemon.objects.count()

                if pokemon_count == 0:
                    logger.info("🔄 No Pokemon found. Starting sync for all Pokemon...")
                    self.start_full_sync()
                else:
                    logger.info(f"ℹ️ Database contains {pokemon_count} Pokemon")
                    logger.info("💡 Use 'python manage.py sync_pokemon' to add more Pokemon")

            except Exception as e:
                logger.warning(f"⚠️ Cannot check Pokemon count: {e}")

    def start_full_sync(self):
        """Spustí sync pre všetkých 1010 Pokémonov"""
        try:
            from django.core.management import call_command
            
            print("\n" + "="*60)
            print("🎮 WELCOME TO POKEMON DATABASE SETUP!")
            print("="*60)
            print("Your database is empty. Starting download of ALL Pokemon!")
            print("This will download all 1010 Pokemon from all generations.")
            print("="*60)
            
            choice = input("🚀 Start downloading all Pokemon? (Y/n): ").strip().lower()
            
            if choice in ['', 'y', 'yes']:
                call_command('sync_pokemon')
            else:
                print("💡 You can run 'python manage.py sync_pokemon' later to add Pokemon.")
                
        except Exception as e:
            logger.error(f"Error in startup sync: {e}")
