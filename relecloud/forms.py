from django import forms
from .models import Destination

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

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