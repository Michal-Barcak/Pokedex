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

