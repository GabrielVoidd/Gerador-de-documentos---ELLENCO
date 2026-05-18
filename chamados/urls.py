from django.urls import path
from . import views

urlpatterns = [
    path('<str:setor>/chamados/meus-chamados/', views.MeusChamadosListView.as_view(), name='meus_chamados'),
    path('<str:setor>/chamados/fila-trabalho/', views.FilaChamadosListView.as_view(), name='fila_trabalho'),
    path('<str:setor>/chamados/novo/', views.ChamadoCreateView.as_view(), name='novo_chamado'),
]