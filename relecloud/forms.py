from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Destination

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

class UserRegistrationForm(UserCreationForm):
    """Formulario de registro de usuarios con campos adicionales."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets para las contraseñas
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ["name", "description", "slug", "image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > MAX_IMAGE_SIZE_BYTES:
                raise forms.ValidationError("La imagen supera el tamaño máximo de 5MB.")
            content_type = getattr(image, 'content_type', '')
            if content_type and content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise forms.ValidationError("Tipo de archivo no soportado. Usa JPG, PNG o WEBP.")
        return image
from django.core.exceptions import ValidationError
from .models import Review, InfoRequest


class ReviewForm(forms.ModelForm):
    """Formulario para crear reviews de destinos y cruceros.
    
    Valida que el usuario haya comprado (InfoRequest aprobado) antes de permitir
    la creación de la review.
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} estrellas') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                    'required': True
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Escribe tu opinión sobre tu experiencia... (opcional)',
                    'maxlength': 1000
                }
            ),
        }
        labels = {
            'rating': 'Puntuación',
            'comment': 'Comentario (opcional)',
        }
        help_texts = {
            'rating': 'Selecciona de 1 a 5 estrellas',
            'comment': 'Máximo 1000 caracteres',
        }
    
    def __init__(self, *args, user=None, destination=None, cruise=None, **kwargs):
        """Inicializar formulario con usuario, destino y/o crucero.
        
        Args:
            user: Usuario que crea la review
            destination: Destino a valorar (opcional)
            cruise: Crucero a valorar (opcional)
        """
        super().__init__(*args, **kwargs)
        self.user = user
        self.destination = destination
        self.cruise = cruise
    
    def clean(self):
        """Validación adicional para verificar que el usuario puede hacer review."""
        cleaned_data = super().clean()
        
        if not self.user or not self.user.is_authenticated:
            raise ValidationError('Debes estar autenticado para hacer una review.')
        
        # Verificar si ya existe una review de este usuario
        if self.destination:
            existing_review = Review.objects.filter(
                user=self.user,
                destination=self.destination
            ).exists()
            if existing_review:
                raise ValidationError(
                    f'Ya has valorado este destino. Solo puedes dejar una review por destino.'
                )
        
        if self.cruise:
            existing_review = Review.objects.filter(
                user=self.user,
                cruise=self.cruise
            ).exists()
            if existing_review:
                raise ValidationError(
                    f'Ya has valorado este crucero. Solo puedes dejar una review por crucero.'
                )
        
        # La validación de compra se hace en Review.clean() del modelo
        # Aquí solo validamos la duplicación de reviews
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar review asignando usuario, destino y/o crucero."""
        # Crear instancia sin llamar a full_clean() todavía
        review = super().save(commit=False)
        
        # Asignar los campos requeridos
        review.user = self.user
        
        if self.destination:
            review.destination = self.destination
            review.cruise = None
        elif self.cruise:
            review.cruise = self.cruise
            review.destination = None
        
        if commit:
            # Ahora sí validar y guardar con todos los campos asignados
            review.full_clean()
            review.save()
        
        return review
