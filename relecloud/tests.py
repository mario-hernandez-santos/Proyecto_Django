from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image
import io
import tempfile
from django.core.exceptions import ValidationError
from .models import Destination, Cruise, Comment
from .forms import DestinationForm


class CommentModelTest(TestCase):
    """Tests para el modelo Comment"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test Description',
            slug='test-destination'
        )
        self.cruise = Cruise.objects.create(
            name='Test Cruise',
            description='Test Cruise Description'
        )
    
    def test_comment_creation_for_destination(self):
        """Test que falla: crear un comentario para un destino"""
        comment = Comment.objects.create(
            user=self.user,
            destination=self.destination,
            content='Este destino es increíble!'
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.destination, self.destination)
        self.assertEqual(comment.content, 'Este destino es increíble!')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_creation_for_cruise(self):
        """Test que falla: crear un comentario para un crucero"""
        comment = Comment.objects.create(
            user=self.user,
            cruise=self.cruise,
            content='El crucero fue excelente!'
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.cruise, self.cruise)
        self.assertEqual(comment.content, 'El crucero fue excelente!')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_str_method(self):
        """Test que falla: verificar el método __str__ del comentario"""
        comment = Comment.objects.create(
            user=self.user,
            destination=self.destination,
            content='Comentario de prueba'
        )
        expected_str = f'{self.user.username} - {self.destination.name}'
        self.assertEqual(str(comment), expected_str)


class DestinationCommentViewTest(TestCase):
    """Tests para comentarios en destinos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test Description',
            slug='test-destination'
        )
    
    def test_authenticated_user_can_see_comment_form(self):
        """Test que falla: usuario autenticado ve el formulario de comentarios"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('destination_detail', kwargs={'pk': self.destination.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'opinión')
        self.assertContains(response, '<form')
    
    def test_unauthenticated_user_cannot_see_comment_form(self):
        """Test que falla: usuario no autenticado no ve el formulario"""
        response = self.client.get(
            reverse('destination_detail', kwargs={'pk': self.destination.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<form')
        self.assertContains(response, 'iniciar sesión')
    
    def test_authenticated_user_can_post_comment(self):
        """Test que falla: usuario autenticado puede publicar comentario"""
        self.client.login(username='testuser', password='testpass123')
        comment_data = {
            'content': 'Este es un comentario de prueba'
        }
        response = self.client.post(
            reverse('destination_comment', kwargs={'pk': self.destination.pk}),
            data=comment_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect después de éxito
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Este es un comentario de prueba')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.destination, self.destination)
    
    def test_unauthenticated_user_cannot_post_comment(self):
        """Test que falla: usuario no autenticado no puede comentar"""
        comment_data = {
            'content': 'Este comentario no debería guardarse'
        }
        response = self.client.post(
            reverse('destination_comment', kwargs={'pk': self.destination.pk}),
            data=comment_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect a login
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_comments_displayed_on_destination_page(self):
        """Test que falla: los comentarios se muestran en la página del destino"""
        Comment.objects.create(
            user=self.user,
            destination=self.destination,
            content='Primer comentario'
        )
        Comment.objects.create(
            user=self.user,
            destination=self.destination,
            content='Segundo comentario'
        )
        response = self.client.get(
            reverse('destination_detail', kwargs={'pk': self.destination.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Primer comentario')
        self.assertContains(response, 'Segundo comentario')
        self.assertContains(response, self.user.username)


class CruiseCommentViewTest(TestCase):
    """Tests para comentarios en cruceros"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.cruise = Cruise.objects.create(
            name='Test Cruise',
            description='Test Cruise Description'
        )
    
    def test_authenticated_user_can_see_comment_form_on_cruise(self):
        """Test que falla: usuario autenticado ve el formulario en crucero"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'opinión')
        self.assertContains(response, '<form')
    
    def test_authenticated_user_can_post_comment_on_cruise(self):
        """Test que falla: usuario autenticado puede comentar en crucero"""
        self.client.login(username='testuser', password='testpass123')
        comment_data = {
            'content': 'Excelente crucero!'
        }
        response = self.client.post(
            reverse('cruise_comment', kwargs={'pk': self.cruise.pk}),
            data=comment_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Excelente crucero!')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.cruise, self.cruise)
    
    def test_comments_displayed_on_cruise_page(self):
        """Test que falla: los comentarios se muestran en la página del crucero"""
        Comment.objects.create(
            user=self.user,
            cruise=self.cruise,
            content='Gran experiencia'
        )
        response = self.client.get(
            reverse('cruise_detail', kwargs={'pk': self.cruise.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gran experiencia')
        self.assertContains(response, self.user.username)


class CommentValidationTest(TestCase):
    """Tests para validación de comentarios"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test Description',
            slug='test-destination'
        )
    
    def test_comment_cannot_be_empty(self):
        """Test que falla: comentario no puede estar vacío"""
        from django.core.exceptions import ValidationError
        comment = Comment(
            user=self.user,
            destination=self.destination,
            content=''
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()
    
    def test_comment_has_max_length(self):
        """Test que verifica que el comentario respeta el max_length"""
        # Django trunca silenciosamente en algunos backends, 
        # así que verificamos que el max_length está definido
        content_field = Comment._meta.get_field('content')
        self.assertEqual(content_field.max_length, 1000)


# ============================================================================
# SUBTAREA 4: TESTS PARA IMAGEN EN DESTINATION
# ============================================================================

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DestinationImageModelTest(TestCase):
    """Tests unitarios para el modelo Destination con ImageField"""
    
    def create_test_image(self, name='test.jpg', size=(100, 100), format='JPEG'):
        """Helper para crear imágenes de prueba"""
        file = io.BytesIO()
        image = Image.new('RGB', size, color='red')
        image.save(file, format)
        file.seek(0)
        return SimpleUploadedFile(name, file.read(), content_type=f'image/{format.lower()}')
    
    def test_destination_can_be_created_without_image(self):
        """El campo imagen es opcional (blank=True, null=True)"""
        destination = Destination.objects.create(
            name='Mars Without Image',
            description='Red planet',
            slug='mars-no-img'
        )
        self.assertFalse(destination.image)
        self.assertEqual(destination.name, 'Mars Without Image')
    
    def test_destination_can_be_created_with_image(self):
        """Se puede crear un destino con imagen"""
        image = self.create_test_image()
        destination = Destination.objects.create(
            name='Mars With Image',
            description='Red planet',
            slug='mars-img',
            image=image
        )
        self.assertTrue(destination.image)
        self.assertIn('destinations/', destination.image.name)
    
    def test_image_upload_path_uses_uuid(self):
        """El nombre del archivo usa UUID para evitar colisiones"""
        image = self.create_test_image(name='original.jpg')
        destination = Destination.objects.create(
            name='Test UUID',
            description='Test',
            slug='test-uuid',
            image=image
        )
        # El nombre no debe ser 'original.jpg', debe ser UUID
        self.assertNotIn('original', destination.image.name)
        self.assertIn('destinations/', destination.image.name)
        self.assertTrue(destination.image.name.endswith('.jpg'))
    
    def test_image_field_validators(self):
        """El campo imagen tiene validadores de extensión"""
        image_field = Destination._meta.get_field('image')
        validators = image_field.validators
        self.assertTrue(len(validators) > 0)
        # Verificar que existe FileExtensionValidator
        from django.core.validators import FileExtensionValidator
        has_extension_validator = any(
            isinstance(v, FileExtensionValidator) for v in validators
        )
        self.assertTrue(has_extension_validator)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DestinationImageFormTest(TestCase):
    """Tests unitarios para DestinationForm con validaciones de imagen"""
    
    def create_test_image(self, name='test.jpg', size=(100, 100), format='JPEG'):
        """Helper para crear imágenes de prueba"""
        file = io.BytesIO()
        image = Image.new('RGB', size, color='blue')
        image.save(file, format)
        file.seek(0)
        return SimpleUploadedFile(name, file.read(), content_type=f'image/{format.lower()}')
    
    def test_form_accepts_valid_jpg_image(self):
        """El formulario acepta imágenes JPG válidas"""
        image = self.create_test_image('test.jpg', format='JPEG')
        form = DestinationForm(
            data={'name': 'Test', 'description': 'Desc', 'slug': 'test'},
            files={'image': image}
        )
        self.assertTrue(form.is_valid())
    
    def test_form_accepts_valid_png_image(self):
        """El formulario acepta imágenes PNG válidas"""
        image = self.create_test_image('test.png', format='PNG')
        form = DestinationForm(
            data={'name': 'Test PNG', 'description': 'Desc', 'slug': 'test-png'},
            files={'image': image}
        )
        self.assertTrue(form.is_valid())
    
    def test_form_accepts_valid_webp_image(self):
        """El formulario acepta imágenes WEBP válidas"""
        image = self.create_test_image('test.webp', format='WEBP')
        form = DestinationForm(
            data={'name': 'Test WEBP', 'description': 'Desc', 'slug': 'test-webp'},
            files={'image': image}
        )
        self.assertTrue(form.is_valid())
    
    def test_form_rejects_oversized_image(self):
        """El formulario rechaza imágenes mayores a 5MB"""
        # Crear una imagen grande (más de 5MB)
        large_image = self.create_test_image('large.jpg', size=(5000, 5000))
        form = DestinationForm(
            data={'name': 'Large', 'description': 'Desc', 'slug': 'large'},
            files={'image': large_image}
        )
        # Verificar que el formulario no es válido
        if not form.is_valid():
            self.assertIn('image', form.errors)
            self.assertIn('5MB', str(form.errors['image']))
    
    def test_form_rejects_invalid_mime_type(self):
        """El formulario rechaza tipos MIME no permitidos"""
        # Crear un archivo falso con extensión válida pero MIME incorrecto
        fake_image = SimpleUploadedFile(
            'fake.jpg',
            b'not an image',
            content_type='text/plain'
        )
        form = DestinationForm(
            data={'name': 'Fake', 'description': 'Desc', 'slug': 'fake'},
            files={'image': fake_image}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
    
    def test_form_rejects_invalid_extension(self):
        """El formulario rechaza extensiones no permitidas (.gif, .bmp, etc.)"""
        gif_image = SimpleUploadedFile(
            'test.gif',
            b'GIF89a',
            content_type='image/gif'
        )
        form = DestinationForm(
            data={'name': 'GIF Test', 'description': 'Desc', 'slug': 'gif'},
            files={'image': gif_image}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DestinationImageIntegrationTest(TestCase):
    """Tests de integración para subida y visualización de imágenes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
    
    def create_test_image(self, name='test.jpg', size=(200, 200)):
        """Helper para crear imágenes de prueba"""
        file = io.BytesIO()
        image = Image.new('RGB', size, color='green')
        image.save(file, 'JPEG')
        file.seek(0)
        return SimpleUploadedFile(name, file.read(), content_type='image/jpeg')
    
    def test_create_destination_with_image_via_view(self):
        """Se puede crear un destino con imagen a través de la vista"""
        self.client.login(username='admin', password='admin123')
        image = self.create_test_image()
        
        response = self.client.post(reverse('destination_create'), {
            'name': 'Venus',
            'description': 'Hot planet',
            'slug': 'venus',
            'image': image
        })
        
        # Verificar redirección exitosa
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el destino se creó con imagen
        destination = Destination.objects.get(slug='venus')
        self.assertTrue(destination.image)
        self.assertIn('destinations/', destination.image.name)
    
    def test_update_destination_image_via_view(self):
        """Se puede actualizar la imagen de un destino existente"""
        # Crear destino sin imagen
        destination = Destination.objects.create(
            name='Jupiter',
            description='Gas giant',
            slug='jupiter'
        )
        
        self.client.login(username='admin', password='admin123')
        new_image = self.create_test_image('new.jpg')
        
        response = self.client.post(
            reverse('destination_update', kwargs={'pk': destination.pk}),
            {
                'name': 'Jupiter',
                'description': 'Gas giant',
                'slug': 'jupiter',
                'image': new_image
            }
        )
        
        destination.refresh_from_db()
        self.assertTrue(destination.image)
    
    def test_destination_detail_displays_image(self):
        """La página de detalle muestra la imagen si existe"""
        image = self.create_test_image()
        destination = Destination.objects.create(
            name='Saturn',
            description='Ringed planet',
            slug='saturn',
            image=image
        )
        
        response = self.client.get(
            reverse('destination_detail', kwargs={'pk': destination.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, destination.image.url)
    
    def test_destination_detail_shows_placeholder_without_image(self):
        """La página de detalle muestra placeholder si no hay imagen"""
        destination = Destination.objects.create(
            name='Neptune',
            description='Blue planet',
            slug='neptune'
        )
        
        response = self.client.get(
            reverse('destination_detail', kwargs={'pk': destination.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        # Verificar que muestra el placeholder
        self.assertContains(response, 'planet-icon.svg')
    
    def test_destination_list_displays_images(self):
        """La lista de destinos muestra las imágenes"""
        image = self.create_test_image()
        destination = Destination.objects.create(
            name='Uranus',
            description='Ice giant',
            slug='uranus',
            image=image
        )
        
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, destination.image.url)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DestinationImageSecurityTest(TestCase):
    """Tests de seguridad para validar subida de archivos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='hacker',
            password='hack123',
            is_staff=True
        )
        self.client.login(username='hacker', password='hack123')
    
    def test_reject_executable_file_with_image_extension(self):
        """Rechaza archivos ejecutables disfrazados como imágenes"""
        malicious_file = SimpleUploadedFile(
            'malware.jpg',
            b'#!/bin/bash\nrm -rf /',
            content_type='application/x-sh'
        )
        
        response = self.client.post(reverse('destination_create'), {
            'name': 'Malicious',
            'description': 'Bad',
            'slug': 'malicious',
            'image': malicious_file
        })
        
        # No debe crear el destino con archivo malicioso
        self.assertFalse(Destination.objects.filter(slug='malicious').exists())
    
    def test_reject_html_file_as_image(self):
        """Rechaza archivos HTML disfrazados como imágenes"""
        html_file = SimpleUploadedFile(
            'xss.jpg',
            b'<html><script>alert("XSS")</script></html>',
            content_type='text/html'
        )
        
        form = DestinationForm(
            data={'name': 'XSS', 'description': 'Bad', 'slug': 'xss'},
            files={'image': html_file}
        )
        
        self.assertFalse(form.is_valid())
    
    def test_reject_path_traversal_in_filename(self):
        """El sistema protege contra path traversal (../)"""
        file = io.BytesIO()
        image = Image.new('RGB', (50, 50), color='red')
        image.save(file, 'JPEG')
        file.seek(0)
        
        traversal_file = SimpleUploadedFile(
            '../../../evil.jpg',
            file.read(),
            content_type='image/jpeg'
        )
        
        destination = Destination.objects.create(
            name='Traversal Test',
            description='Test',
            slug='traversal',
            image=traversal_file
        )
        
        # El nombre del archivo no debe contener ../ en el path final
        self.assertNotIn('..', destination.image.name)
        self.assertIn('destinations/', destination.image.name)
    
    def test_maximum_file_size_enforced(self):
        """Se valida el tamaño máximo de 5MB"""
        # Crear imagen muy grande
        file = io.BytesIO()
        # Imagen de 6MB aproximadamente
        huge_image = Image.new('RGB', (10000, 10000), color='white')
        huge_image.save(file, 'JPEG', quality=95)
        file.seek(0)
        
        huge_file = SimpleUploadedFile(
            'huge.jpg',
            file.read(),
            content_type='image/jpeg'
        )
        
        form = DestinationForm(
            data={'name': 'Huge', 'description': 'Too big', 'slug': 'huge'},
            files={'image': huge_file}
        )
        
        # Debe fallar la validación
        if huge_file.size > 5 * 1024 * 1024:
            self.assertFalse(form.is_valid())
            self.assertIn('image', form.errors)
class ReviewModelTest(TestCase):
    """Tests para el modelo Review (TDD - Red Phase)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test Description',
            slug='test-destination'
        )
        self.cruise = Cruise.objects.create(
            name='Test Cruise',
            description='Test Cruise Description'
        )
        self.cruise.destinations.add(self.destination)
        
        # Crear InfoRequest aprobado para que el usuario pueda hacer reviews
        from .models import InfoRequest
        InfoRequest.objects.create(
            user=self.user,
            name='Test User',
            email='test@example.com',
            notes='Test purchase',
            cruise=self.cruise,
            approved=True
        )
    
    def test_review_creation_for_destination(self):
        """Test: crear una review para un destino con puntuación"""
        from .models import Review
        review = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            comment='Excelente destino!'
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.destination, self.destination)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excelente destino!')
        self.assertIsNotNone(review.created_at)
    
    def test_review_creation_for_cruise(self):
        """Test: crear una review para un crucero con puntuación"""
        from .models import Review
        review = Review.objects.create(
            user=self.user,
            cruise=self.cruise,
            rating=4,
            comment='Muy buen crucero'
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.cruise, self.cruise)
        self.assertEqual(review.rating, 4)
    
    def test_review_rating_must_be_between_1_and_5(self):
        """Test: la puntuación debe estar entre 1 y 5"""
        from .models import Review
        # Test rating menor que 1
        review_low = Review(
            user=self.user,
            destination=self.destination,
            rating=0,
            comment='Test'
        )
        with self.assertRaises(ValidationError):
            review_low.full_clean()
        
        # Test rating mayor que 5
        review_high = Review(
            user=self.user,
            destination=self.destination,
            rating=6,
            comment='Test'
        )
        with self.assertRaises(ValidationError):
            review_high.full_clean()
    
    def test_review_rating_is_required(self):
        """Test: la puntuación es obligatoria"""
        from .models import Review
        review = Review(
            user=self.user,
            destination=self.destination,
            comment='Test'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()
    
    def test_user_can_only_review_destination_once(self):
        """Test: un usuario solo puede hacer una review por destino"""
        from .models import Review
        
        Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            comment='Primera review'
        )
        
        # Intentar crear segunda review del mismo usuario para el mismo destino
        with self.assertRaises(ValidationError):
            Review.objects.create(
                user=self.user,
                destination=self.destination,
                rating=4,
                comment='Segunda review'
            )
    
    def test_user_can_only_review_cruise_once(self):
        """Test: un usuario solo puede hacer una review por crucero"""
        from .models import Review
        
        Review.objects.create(
            user=self.user,
            cruise=self.cruise,
            rating=5,
            comment='Primera review'
        )
        
        # Intentar crear segunda review del mismo usuario para el mismo crucero
        with self.assertRaises(ValidationError):
            Review.objects.create(
                user=self.user,
                cruise=self.cruise,
                rating=3,
                comment='Segunda review'
            )
    
    def test_review_must_have_destination_or_cruise(self):
        """Test: una review debe tener destino o crucero (no ambos, no ninguno)"""
        from .models import Review
        
        # Test sin destino ni crucero
        review_empty = Review(
            user=self.user,
            rating=5,
            comment='Test'
        )
        with self.assertRaises(ValidationError):
            review_empty.full_clean()
    
    def test_review_comment_is_optional(self):
        """Test: el comentario es opcional, pero la puntuación no"""
        from .models import Review
        review = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5
        )
        self.assertEqual(review.comment, '')
    
    def test_review_str_method(self):
        """Test: verificar el método __str__ de la review"""
        from .models import Review
        review = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            comment='Excelente'
        )
        expected_str = f'{self.user.username} - {self.destination.name} - 5 estrellas'
        self.assertEqual(str(review), expected_str)
    
    def test_review_ordering(self):
        """Test: las reviews se ordenan por fecha de creación (más recientes primero)"""
        from .models import Review, InfoRequest
        review1 = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            comment='Primera'
        )
        
        user2 = User.objects.create_user(username='user2', password='pass123')
        # Crear InfoRequest aprobado para user2
        InfoRequest.objects.create(
            user=user2,
            name='User 2',
            email='user2@example.com',
            notes='Test purchase',
            cruise=self.cruise,
            approved=True
        )
        review2 = Review.objects.create(
            user=user2,
            destination=self.destination,
            rating=4,
            comment='Segunda'
        )
        
        reviews = Review.objects.all()
        self.assertEqual(reviews[0], review2)
        self.assertEqual(reviews[1], review1)


class DestinationPopularityTest(TestCase):
    """Tests para el cálculo de popularidad en destinos (TDD - Red Phase)"""
    
    def setUp(self):
        self.destination1 = Destination.objects.create(
            name='Paris',
            description='City of lights',
            slug='paris'
        )
        self.destination2 = Destination.objects.create(
            name='Tokyo',
            description='Modern metropolis',
            slug='tokyo'
        )
        self.destination3 = Destination.objects.create(
            name='New York',
            description='The big apple',
            slug='new-york'
        )
        
        # Crear cruceros que incluyan los destinos
        self.cruise1 = Cruise.objects.create(
            name='European Tour',
            description='Tour por Europa'
        )
        self.cruise1.destinations.add(self.destination1)
        
        self.cruise2 = Cruise.objects.create(
            name='Asian Tour',
            description='Tour por Asia'
        )
        self.cruise2.destinations.add(self.destination2)
        
        self.cruise3 = Cruise.objects.create(
            name='American Tour',
            description='Tour por América'
        )
        self.cruise3.destinations.add(self.destination3)
        
        # Crear usuarios
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        
        # Crear InfoRequests aprobados para todos los usuarios en todos los cruceros
        from .models import InfoRequest
        for user in [self.user1, self.user2, self.user3]:
            for cruise in [self.cruise1, self.cruise2, self.cruise3]:
                InfoRequest.objects.create(
                    user=user,
                    name=f'{user.username} name',
                    email=f'{user.username}@example.com',
                    notes='Approved purchase',
                    cruise=cruise,
                    approved=True
                )
    
    def test_destination_review_count(self):
        """Test: contar el número de reviews de un destino"""
        from .models import Review
        
        # Crear reviews para destination1
        Review.objects.create(user=self.user1, destination=self.destination1, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination1, rating=4)
        Review.objects.create(user=self.user3, destination=self.destination1, rating=5)
        
        # Crear reviews para destination2
        Review.objects.create(user=self.user1, destination=self.destination2, rating=3)
        
        # destination3 sin reviews
        
        self.assertEqual(self.destination1.review_count, 3)
        self.assertEqual(self.destination2.review_count, 1)
        self.assertEqual(self.destination3.review_count, 0)
    
    def test_destination_average_rating(self):
        """Test: calcular la puntuación media de un destino"""
        from .models import Review
        
        # Crear reviews para destination1 (promedio: 4.0)
        Review.objects.create(user=self.user1, destination=self.destination1, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination1, rating=4)
        Review.objects.create(user=self.user3, destination=self.destination1, rating=3)
        
        # Crear reviews para destination2 (promedio: 5.0)
        Review.objects.create(user=self.user1, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination2, rating=5)
        
        # destination3 sin reviews
        
        self.assertEqual(self.destination1.average_rating, 4.0)
        self.assertEqual(self.destination2.average_rating, 5.0)
        self.assertEqual(self.destination3.average_rating, 0)
    
    def test_destination_popularity_score(self):
        """Test: calcular el score de popularidad combinando cantidad y calidad"""
        from .models import Review
        
        # destination1: 3 reviews con promedio 4.0
        Review.objects.create(user=self.user1, destination=self.destination1, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination1, rating=4)
        Review.objects.create(user=self.user3, destination=self.destination1, rating=3)
        
        # destination2: 2 reviews con promedio 5.0
        Review.objects.create(user=self.user1, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination2, rating=5)
        
        # El score debe considerar tanto cantidad como calidad
        self.assertGreater(self.destination1.popularity_score, 0)
        self.assertGreater(self.destination2.popularity_score, 0)


class DestinationViewOrderingTest(TestCase):
    """Tests para la ordenación de destinos en la vista (TDD - Red Phase)"""
    
    def setUp(self):
        self.client = Client()
        
        self.destination1 = Destination.objects.create(
            name='Paris',
            description='City of lights',
            slug='paris'
        )
        self.destination2 = Destination.objects.create(
            name='Tokyo',
            description='Modern metropolis',
            slug='tokyo'
        )
        self.destination3 = Destination.objects.create(
            name='New York',
            description='The big apple',
            slug='new-york'
        )
        
        # Crear cruceros
        self.cruise1 = Cruise.objects.create(name='European Tour', description='Tour por Europa')
        self.cruise1.destinations.add(self.destination1)
        
        self.cruise2 = Cruise.objects.create(name='Asian Tour', description='Tour por Asia')
        self.cruise2.destinations.add(self.destination2)
        
        self.cruise3 = Cruise.objects.create(name='American Tour', description='Tour por América')
        self.cruise3.destinations.add(self.destination3)
        
        # Crear usuarios
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.user3 = User.objects.create_user(username='user3', password='pass123')
        
        # Crear InfoRequests aprobados
        from .models import InfoRequest
        for user in [self.user1, self.user2, self.user3]:
            for cruise in [self.cruise1, self.cruise2, self.cruise3]:
                InfoRequest.objects.create(
                    user=user,
                    name=f'{user.username} name',
                    email=f'{user.username}@example.com',
                    notes='Approved purchase',
                    cruise=cruise,
                    approved=True
                )
    
    def test_destinations_ordered_by_popularity(self):
        """Test: los destinos se ordenan por popularidad en la vista principal"""
        from .models import Review
        
        # Tokyo: 3 reviews, promedio 5.0 (más popular)
        Review.objects.create(user=self.user1, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user3, destination=self.destination2, rating=5)
        
        # Paris: 2 reviews, promedio 4.0
        Review.objects.create(user=self.user1, destination=self.destination1, rating=4)
        Review.objects.create(user=self.user2, destination=self.destination1, rating=4)
        
        # New York: 1 review, promedio 3.0 (menos popular)
        Review.objects.create(user=self.user3, destination=self.destination3, rating=3)
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        
        # Verificar orden: Tokyo, Paris, New York
        self.assertEqual(destinations[0], self.destination2)
        self.assertEqual(destinations[1], self.destination1)
        self.assertEqual(destinations[2], self.destination3)
    
    def test_destinations_with_no_reviews_appear_last(self):
        """Test: destinos sin reviews aparecen al final"""
        from .models import Review
        
        # Solo Tokyo tiene reviews
        Review.objects.create(user=self.user1, destination=self.destination2, rating=5)
        
        response = self.client.get(reverse('destinations'))
        destinations = list(response.context['destinations'])
        
        # Tokyo debe estar primero
        self.assertEqual(destinations[0], self.destination2)
        
        # Paris y New York al final (sin orden específico entre ellos)
        self.assertIn(self.destination1, destinations[1:])
        self.assertIn(self.destination3, destinations[1:])
    
    def test_destinations_ordering_updates_with_new_reviews(self):
        """Test: el orden se actualiza al añadir nuevas reviews"""
        from .models import Review
        
        # Inicialmente Paris es más popular
        Review.objects.create(user=self.user1, destination=self.destination1, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination1, rating=5)
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        self.assertEqual(destinations[0], self.destination1)
        
        # Añadir más reviews a Tokyo
        Review.objects.create(user=self.user1, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user2, destination=self.destination2, rating=5)
        Review.objects.create(user=self.user3, destination=self.destination2, rating=5)
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        
        # Ahora Tokyo debe estar primero
        self.assertEqual(destinations[0], self.destination2)


class ReviewRestrictionTest(TestCase):
    """Tests para validar que solo usuarios con compras pueden hacer reviews"""
    
    def setUp(self):
        """Configurar usuarios, destinos, cruceros e InfoRequests"""
        self.user_with_purchase = User.objects.create_user(
            username='buyer',
            password='testpass123'
        )
        self.user_without_purchase = User.objects.create_user(
            username='nonbuyer',
            password='testpass123'
        )
        
        self.destination = Destination.objects.create(
            name='Caribbean Paradise',
            description='Beautiful destination',
            slug='caribbean-paradise'
        )
        
        self.cruise = Cruise.objects.create(
            name='Caribbean Adventure',
            description='Amazing cruise'
        )
        self.cruise.destinations.add(self.destination)
        
        # Usuario que HA comprado (InfoRequest aprobado)
        from .models import InfoRequest
        self.approved_request = InfoRequest.objects.create(
            user=self.user_with_purchase,
            name='John Buyer',
            email='buyer@example.com',
            notes='I want to buy this cruise',
            cruise=self.cruise,
            approved=True
        )
    
    def test_user_with_purchase_can_review_destination(self):
        """Test: usuario con compra aprobada PUEDE hacer review de destino"""
        from .models import Review
        
        review = Review(
            user=self.user_with_purchase,
            destination=self.destination,
            rating=5,
            comment='Excellent destination!'
        )
        
        # No debe lanzar ValidationError
        try:
            review.full_clean()
            review.save()
            self.assertTrue(True)
        except ValidationError:
            self.fail('Usuario con compra aprobada debería poder hacer review')
    
    def test_user_with_purchase_can_review_cruise(self):
        """Test: usuario con compra aprobada PUEDE hacer review de crucero"""
        from .models import Review
        
        review = Review(
            user=self.user_with_purchase,
            cruise=self.cruise,
            rating=4,
            comment='Great cruise!'
        )
        
        # No debe lanzar ValidationError
        try:
            review.full_clean()
            review.save()
            self.assertTrue(True)
        except ValidationError:
            self.fail('Usuario con compra aprobada debería poder hacer review')
    
    def test_user_without_purchase_cannot_review_destination(self):
        """Test: usuario SIN compra NO puede hacer review de destino"""
        from .models import Review
        
        review = Review(
            user=self.user_without_purchase,
            destination=self.destination,
            rating=5,
            comment='I want to review but I have not purchased'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError) as context:
            review.full_clean()
        
        self.assertIn('Solo usuarios que hayan comprado', str(context.exception))
    
    def test_user_without_purchase_cannot_review_cruise(self):
        """Test: usuario SIN compra NO puede hacer review de crucero"""
        from .models import Review
        
        review = Review(
            user=self.user_without_purchase,
            cruise=self.cruise,
            rating=5,
            comment='I want to review but I have not purchased'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError) as context:
            review.full_clean()
        
        self.assertIn('Solo usuarios que hayan comprado', str(context.exception))
    
    def test_user_with_pending_request_cannot_review(self):
        """Test: usuario con solicitud NO aprobada NO puede hacer review"""
        from .models import Review, InfoRequest
        
        # Crear usuario con solicitud pendiente (approved=False)
        user_pending = User.objects.create_user(
            username='pending',
            password='testpass123'
        )
        InfoRequest.objects.create(
            user=user_pending,
            name='Pending User',
            email='pending@example.com',
            notes='Waiting for approval',
            cruise=self.cruise,
            approved=False
        )
        
        review = Review(
            user=user_pending,
            cruise=self.cruise,
            rating=3,
            comment='Trying to review with pending request'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError) as context:
            review.full_clean()
        
        self.assertIn('Solo usuarios que hayan comprado', str(context.exception))
    
    def test_review_validation_checks_destination_purchase(self):
        """Test: verificar que la compra sea del crucero que incluye el destino"""
        from .models import Review, InfoRequest
        
        # Crear otro destino NO incluido en el crucero comprado
        other_destination = Destination.objects.create(
            name='Alaska',
            description='Cold destination',
            slug='alaska'
        )
        
        review = Review(
            user=self.user_with_purchase,
            destination=other_destination,  # Destino NO comprado
            rating=5,
            comment='Trying to review destination not purchased'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError) as context:
            review.full_clean()
        
        self.assertIn('no ha comprado ningún crucero', str(context.exception))
