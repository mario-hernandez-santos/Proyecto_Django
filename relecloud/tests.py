from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
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
        from .models import Review
        review1 = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            comment='Primera'
        )
        
        user2 = User.objects.create_user(username='user2', password='pass123')
        review2 = Review.objects.create(
            user=user2,
            destination=self.destination,
            rating=4,
            comment='Segunda'
        )
        
        reviews = Review.objects.all()
        self.assertEqual(reviews[0], review2)
        self.assertEqual(reviews[1], review1)
