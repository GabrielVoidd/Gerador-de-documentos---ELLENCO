from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    InstituicaoEnsinoViewSet, ParteConcedenteViewSet, EstagiarioViewSet, ContratoViewSet, RescisaoViewSet,
    AgenteIntegracaoViewSet, CandidatoViewSet, TipoEventoViewSet, LancamentoViewSet, ReciboViewSet, get_contrato_data,
    ReciboRescisaoViewSet, ContratoSocialViewSet, AditivoViewSet, CriterioExclusaoViewSet, ContratoAceiteViewSet,
    RegistroContatoEmpresaViewSet, CandidatoCreateView, CandidatoSucessoView, CandidatoListView,
    exportar_candidatos_excel, CandidatoPerfilView, VagaCreateView
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
router.register(r'registros-contato-empresas', RegistroContatoEmpresaViewSet, basename='registro-contato-empresa')

urlpatterns = [
    path('login-candidato/', auth_views.LoginView.as_view(template_name='estagios/login_candidato.html'), name='login_candidato'),
    path('candidato/novo/', CandidatoCreateView.as_view(), name='candidato_novo'),
    path('candidato/sucesso/', CandidatoSucessoView.as_view(), name='candidato_sucesso'),
    path('', include(router.urls)),
    path('get-contrato-data/<int:contrato_id>/', get_contrato_data, name='get_contrato_data'),
    path('buscar-candidatos/', CandidatoListView.as_view(), name='buscar_candidatos'),
    path('exportar-candidatos/', exportar_candidatos_excel, name='exportar_candidatos_excel'),
    path('candidato/<int:pk>/perfil/', CandidatoPerfilView.as_view(), name='perfil_candidato'),
    path('vagas/nova/', VagaCreateView.as_view(), name='vaga_nova'),
]
