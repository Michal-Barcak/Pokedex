from django.core.management.base import BaseCommand
import requests
import time
import logging
from datetime import timedelta
from pokemon.background_jobs.pokemon_save_job import save_pokemon_to_db
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download all Pokemon from PokeAPI (1-1010)"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=1010, help="Number of Pokemon to download (default: 1010)")
        parser.add_argument("--start", type=int, default=1, help="Starting Pokemon ID (default: 1)")
        parser.add_argument("--delay", type=float, default=0.001, help="Pause between requests (default: 0.001s)")

    def handle(self, *args, **options):
        start_time = time.perf_counter()
        limit = options["limit"]
        start_id = options["start"]
        delay = options["delay"]
        
        end_id = start_id + limit - 1
        
        self.stdout.write(self.style.SUCCESS("🚀 POKEMON SYNCHRONIZATION STARTED"))
        self.stdout.write(f"📊 Range: Pokemon #{start_id} to #{end_id} ({limit} total)")
        self.stdout.write(f"⏱️  Delay: {delay}s between requests")
        self.stdout.write("=" * 60)
        
        logger.info(f"Starting Pokemon sync: {start_id}-{end_id}")

        saved_count = 0
        error_count = 0
        skipped_count = 0
        processed_count = 0

        # Process each Pokemon
        for i in range(limit):
            current_id = start_id + i
            processed_count += 1
            
            # Skip if exists
            if self.pokemon_exists(current_id):
                skipped_count += 1
                time.sleep(delay * 0.1)
                
                # Progress reporting
                if processed_count % 50 == 0 or processed_count == limit:
                    self.report_progress(processed_count, limit, saved_count, error_count, skipped_count, start_time)
                continue
            
            # Fetch and save
            pokemon_data = self.fetch_pokemon_data(current_id)
            if pokemon_data:
                try:
                    save_pokemon_to_db(pokemon_data)
                    saved_count += 1
                except IntegrityError as e:
                    logger.error(f"Database constraint error for Pokemon #{current_id}: {e}")
                    error_count += 1
                except Exception as e:
                    logger.error(f"Error saving Pokemon #{current_id}: {e}")
                    error_count += 1
            else:
                error_count += 1

            time.sleep(delay)

            # Progress reporting
            if processed_count % 50 == 0 or processed_count == limit:
                self.report_progress(processed_count, limit, saved_count, error_count, skipped_count, start_time)

        # Final stats
        self.final_report(start_time, saved_count, error_count, skipped_count, processed_count)

    def report_progress(self, processed, total, saved, errors, skipped, start_time):
        """Report progress with accurate counts"""
        percent = (processed / total) * 100
        elapsed = time.perf_counter() - start_time
        eta = (elapsed / processed) * (total - processed) if processed > 0 else 0
        
        self.stdout.write(
            f"⚡ {percent:.1f}% ({processed}/{total}) | "
            f"Saved: {saved} | Errors: {errors} | Skipped: {skipped} | "
            f"ETA: {timedelta(seconds=eta)}"
        )

    def final_report(self, start_time, saved_count, error_count, skipped_count, processed_count):
        """Generate final report with accurate statistics"""
        total_time = time.perf_counter() - start_time
        attempted = saved_count + error_count
        success_rate = (saved_count / attempted) * 100 if attempted > 0 else 0
        
        time_status = "✅ Very fast" if total_time < 60 else "⚠️ Slow"

        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 COMPLETED in {timedelta(seconds=total_time)} ({time_status})\n"
                f"📊 Processed: {processed_count} | Saved: {saved_count} | Errors: {error_count} | Skipped: {skipped_count}\n"
                f"✅ Success rate: {success_rate:.1f}% (of attempted downloads)"
            )
        )

        if skipped_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ℹ️  {skipped_count} Pokemon already existed in database (skipped).\n"
                    f"📥 {saved_count} new Pokemon downloaded successfully."
                )
            )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  {error_count} Pokemon failed to download/save.\n"
                    f"💡 Re-run command to retry failed Pokemon."
                )
            )

    def pokemon_exists(self, pokemon_id):
        """Check if Pokemon exists in database"""
        try:
            from pokemon.models import Pokemon
            return Pokemon.objects.filter(api_id=pokemon_id).exists()
        except Exception:
            return False

    def fetch_pokemon_data(self, pokemon_id):
        """Fetch Pokemon data with retry"""
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
        
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if data.get('id') and data.get('name'):
                    return data
                    
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Failed Pokemon #{pokemon_id}: {e}")
                else:
                    time.sleep(1)
                    
        return None
