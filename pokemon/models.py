from django.db import models

class Pokemon(models.Model):
    api_id = models.IntegerField(
        unique=True
        )
    name = models.CharField(
        max_length=100
        )
    sprite_url = models.URLField(
        null=True, blank=True
        )
    created_at = models.DateTimeField(
        auto_now_add=True
        )

    class Meta:
        ordering = ['api_id']
    
    def __str__(self):
        return f"{self.name} (#{self.api_id})"
    
class PokemonType(models.Model):
    api_id = models.IntegerField(
        unique=True
        )
    name = models.CharField(
        max_length=50, 
        unique=True
        )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class PokemonTypeRelation(models.Model):
    pokemon = models.ForeignKey(
        Pokemon, on_delete=models.CASCADE, 
        related_name='types'
        )
    type = models.ForeignKey(
        PokemonType, 
        on_delete=models.CASCADE
        )
    slot = models.IntegerField()
    
    class Meta:
        unique_together = ['pokemon', 'slot']
        ordering = ['slot']

class PokemonAbility(models.Model):
    pokemon = models.ForeignKey(
        Pokemon, 
        on_delete=models.CASCADE, 
        related_name='abilities'
        )
    ability_name = models.CharField(
        max_length=100
        )
    is_hidden = models.BooleanField(
        default=False
        )
    slot = models.IntegerField()
    
    class Meta:
        unique_together = ['pokemon', 'ability_name']
        ordering = ['slot']