# Imágenes Temáticas Espaciales para ReleCloud

Este archivo contiene enlaces a imágenes gratuitas con temática espacial que puedes descargar para tu proyecto.

## Imágenes de Fondo y Hero

### 1. space-hero-bg.jpg
**Descripción**: Imagen de fondo principal con nebulosa y estrellas
**URL sugerida**: https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&h=1080&fit=crop
**Uso**: Fondo principal del hero section

### 2. earth-from-space.jpg
**Descripción**: Vista de la Tierra desde el espacio
**URL sugerida**: https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=1200&h=800&fit=crop
**Uso**: Imagen para destino "Tierra"

### 3. mars-surface.jpg
**Descripción**: Superficie del planeta Marte
**URL sugerida**: https://images.unsplash.com/photo-1630694093867-4b947d812bf0?w=1200&h=800&fit=crop
**Uso**: Imagen para destino "Marte"

### 4. moon-landscape.jpg
**Descripción**: Paisaje lunar con astronauta
**URL sugerida**: https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=1200&h=800&fit=crop
**Uso**: Imagen para destino "Luna"

### 5. space-station.jpg
**Descripción**: Estación espacial en órbita
**URL sugerida**: https://images.unsplash.com/photo-1596131397497-8bb4b5d2c6b4?w=1200&h=800&fit=crop
**Uso**: Imagen para destino "Estación Espacial"

## Iconos y Elementos UI

### 6. rocket-icon.png
**Descripción**: Icono de cohete para navegación
**URL sugerida**: Crear con CSS o usar: https://images.unsplash.com/photo-1517976487492-5750f3195933?w=100&h=100&fit=crop
**Uso**: Icono de navegación

### 7. planet-icon.png
**Descripción**: Icono de planeta
**URL sugerida**: https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=100&h=100&fit=crop
**Uso**: Icono para destinos

### 8. astronaut-helmet.png
**Descripción**: Casco de astronauta
**URL sugerida**: https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=200&h=200&fit=crop
**Uso**: Avatar o icono de usuario

## Imágenes de Galaxias y Nebulosas

### 9. galaxy-spiral.jpg
**Descripción**: Galaxia espiral para fondos
**URL sugerida**: https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=1600&h=1200&fit=crop
**Uso**: Fondo alternativo o imagen decorativa

### 10. nebula-colorful.jpg
**Descripción**: Nebulosa colorida
**URL sugerida**: https://images.unsplash.com/photo-1464802686167-b939a6910659?w=1600&h=1200&fit=crop
**Uso**: Fondo de secciones específicas

## Cómo usar estas imágenes:

1. Descarga las imágenes desde las URLs proporcionadas
2. Renómbralas con los nombres sugeridos
3. Guárdalas en la carpeta `static/res/`
4. Úsalas en tus templates HTML con la ruta: `{% load static %}{% static 'res/nombre-imagen.jpg' %}`

## Ejemplo de uso en templates:

```html
<!-- En tu template HTML -->
{% load static %}
<div class="hero" style="background-image: url('{% static 'res/space-hero-bg.jpg' %}');">
    <h1>Bienvenido a ReleCloud</h1>
    <p>Explora el universo con nosotros</p>
</div>

<div class="destination-card">
    <img src="{% static 'res/mars-surface.jpg' %}" alt="Marte">
    <h3>Viaje a Marte</h3>
    <p>Descubre el planeta rojo...</p>
</div>
```

## Nota sobre derechos de autor:
Todas las URLs apuntan a imágenes de Unsplash que son gratuitas para uso comercial y personal.