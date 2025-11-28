from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Destination, Cruise, Comment


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
