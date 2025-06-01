// =================================
// POKEMON COMPARISON FUNCTIONS
// =================================

function getSelectedPokemon() {
    try {
        const data = localStorage.getItem('selectedPokemon');
        if (!data) return [];
        
        const parsed = JSON.parse(data);
        return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
        console.warn('Invalid localStorage data, clearing');
        localStorage.removeItem('selectedPokemon');
        return [];
    }
}

function saveSelectedPokemon(pokemon) {
    try {
        localStorage.setItem('selectedPokemon', JSON.stringify(pokemon));
    } catch (e) {
        console.error('Failed to save selection');
    }
}

function togglePokemonSelection(checkbox) {
    const pokemonId = parseInt(checkbox.dataset.pokemonId, 10);
    const pokemonName = checkbox.dataset.pokemonName;
    
    if (!pokemonId || !pokemonName) return;
    
    let selected = getSelectedPokemon();
    
    if (checkbox.checked) {
        if (selected.length >= 2) {
            alert('You can only compare 2 Pokémon at once');
            checkbox.checked = false;
            return;
        }
        selected.push({id: pokemonId, name: pokemonName});
    } else {
        selected = selected.filter(p => p.id != pokemonId);
    }
    
    saveSelectedPokemon(selected);
    updateCompareButton();
}

function updateCompareButton() {
    const selected = getSelectedPokemon();
    const compareBtn = document.getElementById('compare-btn');
    
    if (!compareBtn) return;
    
    if (selected.length === 2 && selected[0].id && selected[1].id) {
        compareBtn.style.display = 'block';
        
        const p1 = encodeURIComponent(selected[0].id);
        const p2 = encodeURIComponent(selected[1].id);
        compareBtn.href = `compare/?pokemon1=${p1}&pokemon2=${p2}`;
    } else {
        compareBtn.style.display = 'none';
    }
}

function clearSelection() {
    try {
        localStorage.removeItem('selectedPokemon');
        document.querySelectorAll('.pokemon-compare-checkbox').forEach(cb => {
            if (cb) cb.checked = false;
        });
        updateCompareButton();
    } catch (e) {
        console.error('Failed to clear selection');
    }
}

// =================================
// INITIALIZATION
// =================================

document.addEventListener('DOMContentLoaded', function() {
    try {
        const selected = getSelectedPokemon();
        selected.forEach(pokemon => {
            if (pokemon && pokemon.id) {
                const checkbox = document.querySelector(`[data-pokemon-id="${pokemon.id}"]`);
                if (checkbox) checkbox.checked = true;
            }
        });
        updateCompareButton();
    } catch (e) {
        console.error('Failed to restore selection');
    }
});
