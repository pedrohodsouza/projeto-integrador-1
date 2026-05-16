from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('denunciar/', views.criar_denuncia, name='criar_denuncia'),
    path('denuncias/<int:pk>/', views.detalhe_denuncia, name='detalhe_denuncia'),
    path('denuncias/<int:pk>/sucesso/', views.sucesso_denuncia, name='sucesso_denuncia'),
]
