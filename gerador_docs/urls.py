from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="API Geração de PDFs",
      default_version='v1',
      description="Geração de forms de recrutamento com PDF, geração de contrato e rescisão com PDF, além do CRUD de "
                  "candidatos, estagiários, empresas, instituições de ensino e agentes integradores",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contato@sollenco.com.br"),
      license=openapi.License(name="BSD License"),
   ),
   public=False,
   permission_classes=(permissions.IsAdminUser,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('estagios.urls')),
    path('', include('estagios.web_urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

# Em produção, o seu servidor web deve ser configurado para servir os arquivos da pasta MEDIA_ROOT.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Painel de Controle de Candidatos Ellenco Estágios'

admin.site.index_title = 'Bem vindo ao painel de cadastro'
