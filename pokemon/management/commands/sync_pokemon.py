from django.core.management.base import BaseCommand
import requests
import time
import logging
from datetime import datetime, timedelta
from pokemon.background_jobs.pokemon_save_job import save_pokemon_to_db

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download Pokemon from PokeAPI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=151, help="Number of Pokemon (default: 151)"
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.1,
            help="Pause between requests (default: 0.1s)",
        )

    def handle(self, *args, **options):
        start_time = time.perf_counter()
        limit = options["limit"]
        delay = options["delay"]

        self.stdout.write(f"🚀 Synchronizing {limit} Pokemon (pause: {delay}s)...")
        logger.info(
            f"🚀 Starting synchronization of {limit} Pokemon at {datetime.now().strftime('%H:%M:%S')}"
        )

        saved_count = 0
        error_count = 0
        api_calls = 0

        pokemon_urls = self.get_pokemon_urls(limit)
        api_calls += 1

        if not pokemon_urls:
            self.stdout.write(self.style.ERROR("❌ Failed to get list"))
            return

        self.stdout.write(f"📋 Found {len(pokemon_urls)} Pokemon")
        total_pokemon = len(pokemon_urls)

        for i, url in enumerate(pokemon_urls, 1):
            pokemon_data = self.fetch_pokemon_data(url)

            if pokemon_data:
                try:
                    save_pokemon_to_db(pokemon_data)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving Pokemon: {e}")
                    error_count += 1
            else:
                error_count += 1

            api_calls += 1
            time.sleep(delay)

            current_percent = (i / total_pokemon) * 100
            if (
                i % max(1, total_pokemon // 20) == 0 or i == total_pokemon
            ):  # Every 5%
                logger.info(
                    f"📊 Progress: {current_percent:.1f}% ({i}/{total_pokemon}) - Saved: {saved_count}"
                )
                self.stdout.write(f"⚡ {current_percent:.1f}% ({i}/{total_pokemon})")

        # Final statistics
        total_time = time.perf_counter() - start_time
        success_rate = (saved_count / total_pokemon) * 100

        logger.info(f"✅ Completed in {timedelta(seconds=total_time)}")
        logger.info(
            f"📊 Saved: {saved_count}, Errors: {error_count}, API calls: {api_calls}"
        )
        logger.info(
            f"🚀 Speed: {api_calls/total_time:.1f} calls/s, Success rate: {success_rate:.1f}%"
        )

        time_status = "✅ Under 1 min" if total_time < 60 else f"⚠️ {total_time:.0f}s"

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Done in {timedelta(seconds=total_time)}! {time_status}\n"
                f"   Saved: {saved_count}, Errors: {error_count}, Success rate: {success_rate:.1f}%"
            )
        )

    def get_pokemon_urls(self, limit):
        """Gets list of URLs for Pokemon by limit"""
        try:
            url = f"https://pokeapi.co/api/v2/pokemon/?limit={limit}&offset=0"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return [p["url"] for p in response.json()["results"]]
        except Exception as e:
            logger.error(f"Error getting list: {e}")
            return []

    def fetch_pokemon_data(self, url):
        """Downloads data for one Pokemon with retry mechanism"""
        try:
            pokemon_id = int(url.split("/")[-2])

            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=20 + attempt * 10)
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as e:
                    if attempt == 2:
                        logger.error(
                            f"Final error after 3 attempts for Pokemon #{pokemon_id}: {e}"
                        )
                        return None
                    time.sleep(1)

        except Exception as e:
            pokemon_id = url.split("/")[-2] if "/" in url else "unknown"
            logger.error(f"Error getting Pokemon #{pokemon_id}: {e}")
            return None
