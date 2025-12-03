from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InstituicaoEnsinoViewSet, ParteConcedenteViewSet, EstagiarioViewSet, ContratoViewSet, RescisaoViewSet,
    AgenteIntegracaoViewSet, CandidatoViewSet, TipoEventoViewSet, LancamentoViewSet, ReciboViewSet, get_contrato_data,
    ReciboRescisaoViewSet, ContratoSocialViewSet, AditivoViewSet, CriterioExclusaoViewSet, ContratoAceiteViewSet
)

router = DefaultRouter()
router.register('instituicoes', InstituicaoEnsinoViewSet)
router.register('empresa', ParteConcedenteViewSet)
router.register('estagiarios', EstagiarioViewSet)
router.register('contratos', ContratoViewSet)
router.register('rescisoes', RescisaoViewSet)
router.register('agentes-integradores', AgenteIntegracaoViewSet)
router.register(r'candidatos', CandidatoViewSet)
router.register(r'tipos-eventos', TipoEventoViewSet, basename='tipoevento')
router.register(r'Lancamentos', LancamentoViewSet, basename='lancamento')
router.register(r'recibos', ReciboViewSet, basename='recibo')
router.register(r'recibo_rescisao', ReciboRescisaoViewSet, basename='recibo-rescisao')
router.register(r'contrato_social', ContratoSocialViewSet, basename='contrato-social')
router.register(r'aditivo', AditivoViewSet, basename='aditivo')
router.register(r'criterios-exclusao', CriterioExclusaoViewSet, basename='criterios-exclusao')
router.register(r'contratos-aceite', ContratoAceiteViewSet, basename='contrato-aceite')

urlpatterns = [
    path('', include(router.urls)),
    path('get-contrato-data/<int:contrato_id>/', get_contrato_data, name='get_contrato_data'),
]
