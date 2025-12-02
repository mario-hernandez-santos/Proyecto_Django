from django.contrib import admin
from . import models


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    """Administración personalizada para el modelo Review."""
    list_display = ['user', 'target_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'destination__name', 'cruise__name', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Objetivo de la Review', {
            'fields': ('destination', 'cruise'),
            'description': 'Selecciona SOLO un destino O un crucero, no ambos.'
        }),
        ('Valoración', {
            'fields': ('rating', 'comment')
        }),
        ('Información Adicional', {
            'fields': ('created_at',)
        }),
    )
    
    def target_name(self, obj):
        """Muestra el nombre del objetivo (destino o crucero)."""
        return obj.target_name
    target_name.short_description = 'Objetivo'


# Register other models
admin.site.register(models.Destination)
admin.site.register(models.Cruise)
admin.site.register(models.InfoRequest)
admin.site.register(models.Comment)