# Pokédex Django Application
Simple Django web application for browsing Kanto region Pokémon with comparison and evolution features.

# # Description
The application provides a web interface for:

- Browsing all 151 Kanto Pokémon with pagination

- Filtering by type and abilities

- Viewing detailed Pokémon information

- Comparing two Pokémon side by side

- Exploring evolution chains



# # Requirements
- Python 3.8+

- Django 4.0+


# #  Installation

### Option 1: Local deployment (without Docker)

1. Clone the repository 
    - `git clone https://github.com/PokeAPI/pokebase.git`
    - `cd Pokedex`

2. Create virtual environment
    - `python -m venv pokedex_env`
    - `source pokedex_env/bin/activate`  # Linux/Mac
    - `pokedex_env\Scripts\activate`     # Windows

3. Install dependencies
    - `pip install -r requirements.txt`

4. Database setup
    - `python manage.py makemigrations`
    - `python manage.py migrate`

5. Create superuser (optional)
    - `python manage.py createsuperuser`

6. Run the development server
    - `python manage.py runserver`
     **Note:** Pokemon data will be automatically synchronized from PokeAPI on first run.

7. Manual sync pokemon from pokeapi
    - `python manage.py sync_pokemon`


# #  Basic Commands for download pokemons

1. Download all Pokemon (default)

    - `python manage.py sync_pokemon`
    - Downloads all 1010 Pokemon (ID 1-1010)
    - Uses default delay of 0.005s between requests
    - Automatically skips existing Pokemon

2. Download specific number of Pokemon

    - `python manage.py sync_pokemon --limit 151`
    - Downloads first 151 Pokemon (Kanto region)
    - Starts from Pokemon #1

# # # Regional Downloads
3. Kanto Region (Generation I)

    - `python manage.py sync_pokemon --start 1 --limit 151`
    - Original 151 Pokemon

4. Johto Region (Generation II)

    - `python manage.py sync_pokemon --start 152 --limit 100`
    - Pokemon #152-251

5. Hoenn Region (Generation III)

    - `python manage.py sync_pokemon --start 252 --limit 135`
    - Pokemon #252-386

6. Sinnoh Region (Generation IV)

    - `python manage.py sync_pokemon --start 387 --limit 107`
    - Pokemon #387-493

7. Unova Region (Generation V)

    - `python manage.py sync_pokemon --start 494 --limit 156`
    - Pokemon #494-649

8. Kalos Region (Generation VI)

    - `python manage.py sync_pokemon --start 650 --limit 72`
    - Pokemon #650-721

9. Alola Region (Generation VII)

    - `python manage.py sync_pokemon --start 722 --limit 88`
    - Pokemon #722-809

10. Galar Region (Generation VIII)

    - `python manage.py sync_pokemon --start 810 --limit 89`
    - Pokemon #810-898

11. Paldea Region (Generation IX)

    - `python manage.py sync_pokemon --start 899 --limit 112`
    Pokemon #899-1010

# # # Speed Control Commands
12. Ultra-fast download

    - `python manage.py sync_pokemon --delay 0.001`
    - Minimum delay (use with caution)


# # # Advanced Combinations
13. Multiple regions at once

    - `python manage.py sync_pokemon --start 1 --limit 251`
    - Multiple regions at once (Kanto + Johto)

# # # Clear database
14. Clear database from pokemons
    - `python manage.py flush`

# # # Command Parameters
Parameter	Type	Default	Description
--limit	    Integer	1010	Number of Pokemon to download
--start	    Integer	1	    Starting Pokemon ID
--delay	    Float	0.005	Delay between requests (seconds)

## Usage

### Main Features
- Browse Pokémon: Visit http://127.0.0.1:8000/ to see all Pokémon

- Filter by Type: Use dropdown to filter by Pokémon type

- Filter by Ability: Use dropdown to filter by abilities

- View Details: Click on Pokémon name to see detailed information

- Compare Pokémon: Select 2 Pokémon using checkboxes and click Compare

- Evolution Chains: View evolution trees in detail pages

### Navigation
- Home: / - Main Pokémon list

- Detail: /pokemon/{id}/ - Individual Pokémon details

- Compare: /compare/?pokemon1={id1}&pokemon2={id2} - Comparison view

