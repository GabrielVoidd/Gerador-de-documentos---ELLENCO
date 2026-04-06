from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.dashboard_comercial, name='dashboard_comercial'),
    path('empresa/novo/', views.ParteConcedenteCreateView.as_view(), name='parte_concedente_add'),
    path('empresa/<int:pk>/', views.perfil_empresa, name='perfil_empresa'),
    path('empresa/<int:pk>/novo-contrato-social/', views.ContratoSocialCreateView.as_view(), name='novo_contrato_social'),
    path('empresa/<int:pk>/novo-aceite/', views.ContratoAceiteCreateView.as_view(), name='novo_contrato_aceite'),
]