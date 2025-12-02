from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Count, Avg

# Create your models here.
class Destination(models.Model):
    """Modelo para destinos turísticos.
    
    Incluye propiedades calculadas para popularidad basadas en reviews.
    """
    
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=50,
        verbose_name='Nombre'
    )
    description = models.TextField(
        null=True,
        blank=False,
        max_length=2000,
        verbose_name='Descripción'
    )
    slug = models.SlugField(verbose_name='Slug')
    
    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Destinos'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('destination_detail', kwargs={'pk': self.pk})
    
    @property
    def review_count(self):
        """Retorna el número de reviews del destino.
        
        Nota: Para consultas optimizadas en vistas, usar annotate() en lugar
        de esta propiedad para evitar N+1 queries.
        """
        return self.reviews.count()
    
    @property
    def average_rating(self):
        """Retorna la puntuación media del destino.
        
        Returns:
            float: Puntuación media redondeada a 1 decimal, o 0 si no hay reviews.
        
        Nota: Para consultas optimizadas en vistas, usar annotate() en lugar
        de esta propiedad para evitar N+1 queries.
        """
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else 0
    
    @property
    def popularity_score(self):
        """Calcula un score de popularidad combinando cantidad y calidad de reviews.
        
        Fórmula: número_de_reviews * puntuación_media
        
        Esto premia tanto la cantidad como la calidad de las reviews.
        Un destino con muchas reviews de calidad media puede tener un score
        similar a uno con pocas reviews de máxima calidad.
        
        Returns:
            float: Score de popularidad (0 si no hay reviews).
        """
        return self.review_count * self.average_rating
    
class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=50
    )
    description = models.TextField(
        null=False,
        blank=False,
        max_length=2000
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )
    def __str__(self):
        return self.name
    
class InfoRequest(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    content = models.TextField(
        max_length=1000,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.destination:
            return f'{self.user.username} - {self.destination.name}'
        elif self.cruise:
            return f'{self.user.username} - {self.cruise.name}'
        return f'{self.user.username} - Comment'


class Review(models.Model):
    """Modelo para las opiniones/reviews de usuarios sobre destinos y cruceros.
    
    Cada usuario puede dejar una review por destino o crucero, incluyendo
    una puntuación de 1-5 estrellas y un comentario opcional.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Usuario'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='Destino'
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
        verbose_name='Crucero'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, message='La puntuación mínima es 1 estrella.'),
            MaxValueValidator(5, message='La puntuación máxima es 5 estrellas.')
        ],
        null=False,
        blank=False,
        verbose_name='Puntuación',
        help_text='Puntuación de 1 a 5 estrellas'
    )
    comment = models.TextField(
        max_length=1000,
        null=False,
        blank=True,
        default='',
        verbose_name='Comentario',
        help_text='Comentario opcional (máximo 1000 caracteres)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'destination'],
                name='unique_user_destination_review',
                condition=models.Q(destination__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'cruise'],
                name='unique_user_cruise_review',
                condition=models.Q(cruise__isnull=False)
            ),
        ]
    
    def clean(self):
        """Validar que la review tenga destino O crucero, no ambos ni ninguno."""
        if not self.destination and not self.cruise:
            raise ValidationError(
                'La review debe estar asociada a un destino o a un crucero.'
            )
        if self.destination and self.cruise:
            raise ValidationError(
                'La review no puede estar asociada a un destino y a un crucero simultáneamente.'
            )
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para ejecutar validaciones."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def target(self):
        """Retorna el objetivo de la review (destino o crucero)."""
        return self.destination or self.cruise
    
    @property
    def target_name(self):
        """Retorna el nombre del objetivo de la review."""
        target = self.target
        return target.name if target else 'Sin objetivo'
    
    @property
    def stars_display(self):
        """Retorna una representación visual de las estrellas."""
        return '⭐' * self.rating
    
    def __str__(self):
        return f'{self.user.username} - {self.target_name} - {self.rating} estrellas'
