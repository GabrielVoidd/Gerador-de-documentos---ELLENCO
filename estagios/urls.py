from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InstituicaoEnsinoViewSet, ParteConcedenteViewSet, EstagiarioViewSet, ContratoViewSet, RescisaoViewSet,
    AgenteIntegracaoViewSet, CandidatoViewSet
)

router = DefaultRouter()
router.register('instituicoes', InstituicaoEnsinoViewSet)
router.register('empresa', ParteConcedenteViewSet)
router.register('estagiarios', EstagiarioViewSet)
router.register('contratos', ContratoViewSet)
router.register('rescisoes', RescisaoViewSet)
router.register('agentes-integradores', AgenteIntegracaoViewSet)
router.register(r'candidatos', CandidatoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
