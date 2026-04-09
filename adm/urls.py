from django.urls import path
from adm import views


urlpatterns = [
    path('painel/', views.dashboard_adm, name='dashboard_adm'),
    path('adm/contratos/', views.ContratoListView.as_view(), name='adm_contratos_list'),
    path('adm/contratos/novo/', views.ContratoCreateView.as_view(), name='adm_contrato_novo'),
    path('adm/rescisao/nova/', views.RescisaoCreateView.as_view(), name='adm_rescisao_nova'),
    path('adm/recibos/', views.ReciboListView.as_view(), name='adm_recibos_list'),
    path('adm/recibos/novo/', views.ReciboCreateView.as_view(), name='adm_recibo_novo'),
    path('adm/converter-contrato/<int:candidato_id>/', views.converter_para_contrato, name='adm_converter_contrato'),
    path('cadastro-expresso/', views.cadastro_expresso, name='cadastro_expresso'),
    path('adm/recibos/lote/', views.gerar_recibos_lote, name='adm_recibos_lote'),
]
