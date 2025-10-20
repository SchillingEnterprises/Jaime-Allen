from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('ai/chat/', views.AIChatView.as_view(), name='ai_chat'),
    path('contact/', views.contact, name='contact'),
]
