from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('denunciar/', views.criar_denuncia, name='criar_denuncia'),
    path('denuncias/<int:pk>/sucesso/', views.sucesso_denuncia, name='sucesso_denuncia'),
    path('acompanhar/', views.acompanhar_chamado, name='acompanhar_chamado'),
    path('acompanhar/<int:pk>/', views.detalhe_chamado, name='detalhe_chamado'),
]
