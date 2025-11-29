from django.contrib import admin
from django.utils.html import format_html
from . import models
from .forms import DestinationForm


@admin.register(models.Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationForm
    list_display = ('name', 'description', 'thumbnail')
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'slug')
        }),
        ('Imagen', {
            'fields': ('image', 'image_preview'),
            'description': 'Formatos permitidos: JPG, PNG, WEBP. Tamaño máximo: 5MB'
        }),
    )
    
    def thumbnail(self, obj):
        """Small thumbnail for list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<span style="color: #999; font-style: italic;">Sin imagen</span>')
    thumbnail.short_description = 'Vista previa'
    
    def image_preview(self, obj):
        """Large preview for detail form"""
        if obj.image:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<div style="margin-bottom: 8px; font-weight: 600; color: #417690;">Imagen actual:</div>'
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e1e4e8;" />'
                '<div style="margin-top: 8px; font-size: 12px; color: #666;">📁 {}</div>'
                '</div>',
                obj.image.url,
                obj.image.name.split('/')[-1]
            )
        return format_html('<div style="color: #999; font-style: italic; padding: 10px;">No hay imagen cargada</div>')
    image_preview.short_description = 'Previsualización'


admin.site.register(models.Cruise)
admin.site.register(models.InfoRequest)
admin.site.register(models.Comment)