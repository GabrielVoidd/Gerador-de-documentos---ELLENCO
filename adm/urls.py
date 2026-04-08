from django.urls import path
from adm import views


urlpatterns = [
    path('painel/', views.dashboard_adm, name='dashboard_adm'),
    path('adm/contratos/', views.ContratoListView.as_view(), name='adm_contratos_list'),
    path('adm/contratos/novo/', views.ContratoCreateView.as_view(), name='adm_contrato_novo'),
]
