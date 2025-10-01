from django.urls import path
from .views import ContratoListView, ContratoDeleteView, ContratoCreateView, ContratoUpdateView, ContratoDetailView

urlpatterns = [
    path('contratos/', ContratoListView.as_view(), name='contrato-lista'),
    path('contratos/adicionar/', ContratoCreateView.as_view(), name='contrato-adicionar'),
    path('contratos/<int:pk>/', ContratoDetailView.as_view(), name='contrato-detalhe'),
    path('contratos/<int:pk>/editar/', ContratoUpdateView.as_view(), name='contrato-editar'),
    path('contratos/<int:pk>/excluir/', ContratoDeleteView.as_view(), name='contrato-excluir'),
]
