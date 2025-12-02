## APP (relecloud)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about' , views.about, name='about'),
    path('destinations', views.destinations, name='destinations'),
    path('destination/<int:pk>/', views.DestinationDetailView.as_view(), name='destination_detail'),
    path('destination/<int:pk>/update/', views.DestinationUpdateView.as_view(), name='destination_update'),
    path('destination/<int:pk>/delete/', views.DestinationDeleteView.as_view(), name='destination_delete'),
    path('destination/add/', views.DestinationCreateView.as_view(), name='destination_create'),
    path('destination/<int:pk>/comment/', views.add_destination_comment, name='destination_comment'),
    path('destination/<int:pk>/review/', views.add_destination_review, name='destination_review'),
    path('cruise/<int:pk>/', views.CruiseDetailView.as_view(), name='cruise_detail'),
    path('cruise/<int:pk>/comment/', views.add_cruise_comment, name='cruise_comment'),
    path('cruise/<int:pk>/review/', views.add_cruise_review, name='cruise_review'),
    path('info_request/', views.InfoRequestCreateView.as_view(), name='info_request'),
]