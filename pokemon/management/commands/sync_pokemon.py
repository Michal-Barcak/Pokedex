from django.core.management.base import BaseCommand
import requests
import time
import logging
from datetime import datetime, timedelta
from pokemon.background_jobs.pokemon_save_job import save_pokemon_to_db

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Stiahne pokémonov z PokeAPI'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=151, help='Počet pokémonov (default: 151)')
        parser.add_argument('--delay', type=float, default=0.1, help='Pauza medzi requestami (default: 0.1s)')
    
    def handle(self, *args, **options):
        start_time = time.perf_counter()
        limit = options['limit']
        delay = options['delay']
        
        self.stdout.write(f'🚀 Synchronizácia {limit} pokémonov (pauza: {delay}s)...')
        logger.info(f"🚀 Začiatok synchronizácie {limit} pokémonov o {datetime.now().strftime('%H:%M:%S')}")
        
        saved_count = 0
        error_count = 0
        api_calls = 0
        
        pokemon_urls = self.get_pokemon_urls(limit)
        api_calls += 1
        
        if not pokemon_urls:
            self.stdout.write(self.style.ERROR('❌ Nepodarilo sa získať zoznam'))
            return
        
        self.stdout.write(f'📋 Našiel som {len(pokemon_urls)} pokémonov')
        total_pokemon = len(pokemon_urls)
        
        for i, url in enumerate(pokemon_urls, 1):
            pokemon_data = self.fetch_pokemon_data(url)
            
            if pokemon_data:
                try:
                    save_pokemon_to_db(pokemon_data)
                    saved_count += 1
                except Exception as e:
                    logger.error(f'Chyba pri ukladaní pokémona: {e}')
                    error_count += 1
            else:
                error_count += 1
            
            api_calls += 1
            time.sleep(delay)
            
            current_percent = (i / total_pokemon) * 100
            if i % max(1, total_pokemon // 20) == 0 or i == total_pokemon:  # Každých 5%
                logger.info(f"📊 Progress: {current_percent:.1f}% ({i}/{total_pokemon}) - Uložených: {saved_count}")
                self.stdout.write(f'⚡ {current_percent:.1f}% ({i}/{total_pokemon})')
        
        # Finálne štatistiky
        total_time = time.perf_counter() - start_time
        success_rate = (saved_count / total_pokemon) * 100
        
        logger.info(f"✅ Dokončené za {timedelta(seconds=total_time)}")
        logger.info(f"📊 Uložených: {saved_count}, Chýb: {error_count}, API calls: {api_calls}")
        logger.info(f"🚀 Rýchlosť: {api_calls/total_time:.1f} calls/s, Úspešnosť: {success_rate:.1f}%")
        
        time_status = "✅ Pod 1 min" if total_time < 60 else f"⚠️ {total_time:.0f}s"
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Hotovo za {timedelta(seconds=total_time)}! {time_status}\n'
                f'   Uložených: {saved_count}, Chýb: {error_count}, Úspešnosť: {success_rate:.1f}%'
            )
        )
    
    def get_pokemon_urls(self, limit):
        """Získa zoznam URL pre pokémonov podľa limitu"""
        try:
            url = f"https://pokeapi.co/api/v2/pokemon/?limit={limit}&offset=0"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return [p['url'] for p in response.json()['results']]
        except Exception as e:
            logger.error(f'Chyba pri získavaní zoznamu: {e}')
            return []
    
    def fetch_pokemon_data(self, url):
        """Stiahne dáta jedného pokémona s retry mechanikou"""
        try:
            pokemon_id = int(url.split('/')[-2])
            
            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=20 + attempt * 10)
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as e:
                    if attempt == 2:
                        logger.error(f'Finálna chyba po 3 pokusoch pre pokémon #{pokemon_id}: {e}')
                        return None
                    time.sleep(1)
            
        except Exception as e:
            pokemon_id = url.split('/')[-2] if '/' in url else 'unknown'
            logger.error(f'Chyba pri získavaní pokémon #{pokemon_id}: {e}')
            return None

