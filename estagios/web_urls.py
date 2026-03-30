from django.urls import path
from .views import ContratoListView, ContratoDeleteView, ContratoDetailView

urlpatterns = [
    path('contratos/', ContratoListView.as_view(), name='contrato-lista'),
    path('contratos/<int:pk>/', ContratoDetailView.as_view(), name='contrato-detalhe'),
    path('contratos/<int:pk>/excluir/', ContratoDeleteView.as_view(), name='contrato-excluir'),
]
