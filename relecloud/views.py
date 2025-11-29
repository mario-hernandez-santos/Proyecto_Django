from django.shortcuts import render, redirect, get_object_or_404
from . import models
from . import models
from .forms import DestinationForm
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    all_destinations = models.Destination.objects.all()
    return render(request, 'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context
    
class DestinationCreateView(generic.CreateView):
    model = models.Destination
    form_class = DestinationForm
    template_name = 'destination_form.html'
    success_url = reverse_lazy('destinations')
    
class DestinationUpdateView(generic.UpdateView):
    model = models.Destination
    form_class = DestinationForm
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
        return context
    
class InfoRequestCreateView(SuccessMessageMixin, generic.CreateView):
    model = models.InfoRequest
    fields = ['name', 'email', 'notes', 'cruise']
    template_name = 'info_request_create.html'
    success_url = reverse_lazy('index')
    success_message = "¡Tu solicitud ha sido enviada correctamente!"

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