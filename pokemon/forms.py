from django import forms

class PokemonComparisonForm(forms.Form):
    pokemon1 = forms.IntegerField(
        min_value=1,
        max_value=1010,
        error_messages={
            'required': 'First Pokemon ID is required.',
            'min_value': 'Pokemon ID must be between 1 and 1010.',
            'max_value': 'Pokemon ID must be between 1 and 1010.',
            'invalid': 'Enter a valid Pokemon ID.'
        }
    )
    
    pokemon2 = forms.IntegerField(
        min_value=1,
        max_value=1010,
        error_messages={
            'required': 'Second Pokemon ID is required.',
            'min_value': 'Pokemon ID must be between 1 and 1010.',
            'max_value': 'Pokemon ID must be between 1 and 1010.',
            'invalid': 'Enter a valid Pokemon ID.'
        }
    )
    
    def clean(self):
        """Custom validation for comparing same Pokemon"""
        cleaned_data = super().clean()
        p1 = cleaned_data.get('pokemon1')
        p2 = cleaned_data.get('pokemon2')
        
        if p1 and p2 and p1 == p2:
            raise forms.ValidationError("Cannot compare the same Pokémon.")
        
        return cleaned_data
