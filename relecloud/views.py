from django.shortcuts import render, redirect, get_object_or_404
from . import models
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, F, Q
from django.core.exceptions import ValidationError
from .forms import ReviewForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    """Vista de destinos ordenados por popularidad.
    
    Los destinos se ordenan por:
    1. Número de reviews (descendente) - más reviews = más popular
    2. Puntuación media (descendente) - mejor valoración = más popular
    3. Nombre (alfabético) - desempate final
    
    Optimización: Se usa annotate() para calcular num_reviews y avg_rating
    en la consulta SQL, evitando N+1 queries.
    
    Los destinos sin reviews tienen num_reviews=0 y avg_rating=NULL,
    por lo que aparecen al final de la ordenación.
    """
    all_destinations = models.Destination.objects.annotate(
        num_reviews=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by(
        '-num_reviews',          # Más reviews primero
        '-avg_rating',           # Mejor puntuación primero
        'name'                   # Desempate alfabético
    )
    
    return render(request, 'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['reviews'] = self.object.reviews.all()
        context['review_form'] = ReviewForm()
        
        # Verificar si el usuario puede hacer review
        if self.request.user.is_authenticated:
            # Verificar si ya ha hecho review
            has_reviewed = models.Review.objects.filter(
                user=self.request.user,
                destination=self.object
            ).exists()
            context['has_reviewed'] = has_reviewed
            
            # Verificar si tiene compra aprobada
            cruises_with_destination = self.object.cruises.all()
            has_purchase = models.InfoRequest.objects.filter(
                user=self.request.user,
                cruise__in=cruises_with_destination,
                approved=True
            ).exists()
            context['can_review'] = has_purchase and not has_reviewed
        else:
            context['has_reviewed'] = False
            context['can_review'] = False
        
        return context
    
class DestinationCreateView(generic.CreateView):
    model = models.Destination
    fields = ['name', 'description', 'slug']
    template_name = 'destination_form.html'
    success_url = reverse_lazy('destinations')
    
class DestinationUpdateView(generic.UpdateView):
    model = models.Destination
    fields = ['name', 'description', 'slug']
    template_name = 'destination_form.html'
    success_url = reverse_lazy('destinations')  

class DestinationDeleteView(generic.DeleteView):
    model = models.Destination
    template_name = 'destination_confirm_delete.html'
    success_url = reverse_lazy('destinations')
    
class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['reviews'] = self.object.reviews.all()
        context['review_form'] = ReviewForm()
        
        # Verificar si el usuario puede hacer review
        if self.request.user.is_authenticated:
            # Verificar si ya ha hecho review
            has_reviewed = models.Review.objects.filter(
                user=self.request.user,
                cruise=self.object
            ).exists()
            context['has_reviewed'] = has_reviewed
            
            # Verificar si tiene compra aprobada
            has_purchase = models.InfoRequest.objects.filter(
                user=self.request.user,
                cruise=self.object,
                approved=True
            ).exists()
            context['can_review'] = has_purchase and not has_reviewed
        else:
            context['has_reviewed'] = False
            context['can_review'] = False
        
        return context
    
class InfoRequestCreateView(SuccessMessageMixin, generic.CreateView):
    model = models.InfoRequest
    fields = ['name', 'email', 'notes', 'cruise']
    template_name = 'info_request_create.html'
    success_url = reverse_lazy('index')
    success_message = "¡Tu solicitud ha sido enviada correctamente!"
    
    def form_valid(self, form):
        """Asociar el usuario actual a la solicitud si está autenticado."""
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def add_destination_comment(request, pk):
    destination = get_object_or_404(models.Destination, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            models.Comment.objects.create(
                user=request.user,
                destination=destination,
                content=content
            )
            messages.success(request, '¡Tu opinión ha sido publicada correctamente!')
        else:
            messages.error(request, 'El comentario no puede estar vacío.')
    return redirect('destination_detail', pk=pk)

@login_required
def add_cruise_comment(request, pk):
    cruise = get_object_or_404(models.Cruise, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            models.Comment.objects.create(
                user=request.user,
                cruise=cruise,
                content=content
            )
            messages.success(request, '¡Tu opinión ha sido publicada correctamente!')
        else:
            messages.error(request, 'El comentario no puede estar vacío.')
    return redirect('cruise_detail', pk=pk)


@login_required
def add_destination_review(request, pk):
    """Vista para agregar review a un destino.
    
    Solo usuarios autenticados que hayan comprado un crucero que incluya
    este destino pueden dejar una review.
    """
    destination = get_object_or_404(models.Destination, pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(
            request.POST,
            user=request.user,
            destination=destination
        )
        
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f'¡Gracias por tu valoración de {destination.name}! Tu opinión ha sido publicada.'
                )
                return redirect('destination_detail', pk=pk)
            except ValidationError as e:
                # Errores de validación del modelo (ej: no ha comprado)
                for error in e.messages:
                    messages.error(request, error)
        else:
            # Errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    return redirect('destination_detail', pk=pk)


@login_required
def add_cruise_review(request, pk):
    """Vista para agregar review a un crucero.
    
    Solo usuarios autenticados que hayan comprado este crucero
    pueden dejar una review.
    """
    cruise = get_object_or_404(models.Cruise, pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(
            request.POST,
            user=request.user,
            cruise=cruise
        )
        
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f'¡Gracias por tu valoración de {cruise.name}! Tu opinión ha sido publicada.'
                )
                return redirect('cruise_detail', pk=pk)
            except ValidationError as e:
                # Errores de validación del modelo (ej: no ha comprado)
                for error in e.messages:
                    messages.error(request, error)
        else:
            # Errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    return redirect('cruise_detail', pk=pk)