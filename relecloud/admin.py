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


@admin.register(models.InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    """Administración personalizada para el modelo InfoRequest."""
    list_display = ['name', 'email', 'cruise', 'user', 'approved', 'created_at', 'approval_status']
    list_filter = ['approved', 'cruise', 'created_at']
    search_fields = ['name', 'email', 'notes', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_editable = ['approved']  # Permitir editar aprobación desde la lista
    actions = ['approve_requests', 'reject_requests']
    
    fieldsets = (
        ('Información del Solicitante', {
            'fields': ('user', 'name', 'email')
        }),
        ('Solicitud', {
            'fields': ('cruise', 'notes')
        }),
        ('Estado', {
            'fields': ('approved', 'created_at'),
            'description': '✅ Las compras se aprueban automáticamente. '
                          'Puedes desmarcar si necesitas cancelar una compra.'
        }),
    )
    
    def approval_status(self, obj):
        """Muestra el estado visual de aprobación."""
        if obj.approved:
            return '✅ Aprobado'
        return '⏳ Pendiente'
    approval_status.short_description = 'Estado'
    
    def approve_requests(self, request, queryset):
        """Acción masiva para aprobar solicitudes."""
        updated = queryset.update(approved=True)
        self.message_user(request, f'✅ {updated} solicitud(es) aprobada(s).')
    approve_requests.short_description = '✅ Aprobar solicitudes seleccionadas'
    
    def reject_requests(self, request, queryset):
        """Acción masiva para rechazar/desaprobar solicitudes."""
        updated = queryset.update(approved=False)
        self.message_user(request, f'❌ {updated} solicitud(es) marcada(s) como pendiente.')
    reject_requests.short_description = '❌ Marcar como pendiente'


# Register other models
admin.site.register(models.Cruise)
admin.site.register(models.Comment)