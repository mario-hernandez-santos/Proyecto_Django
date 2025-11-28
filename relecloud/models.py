from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Destination(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=50
    )
    description = models.TextField(
        null=True,
        blank=False,
        max_length=2000
    )
    slug = models.SlugField()
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('destination_detail', kwargs={'pk': self.pk})
    
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