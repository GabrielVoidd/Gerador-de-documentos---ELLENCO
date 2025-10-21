from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Contrato, Rescisao, ParteConcedente, AgenteIntegrador, Estagiario, InstituicaoEnsino, Candidato, \
    CartaEncaminhamento, Arquivos

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('numero_contrato', 'estagiario', 'parte_concedente', 'data_inicio', 'gerar_termo_link')
    search_fields = ('numero_contrato', 'candidato__nome', 'parte_concedente__razao_social')
    list_filter = ('parte_concedente', 'data_inicio')

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('contrato-gerar-termo-compromisso', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Termo de Compromisso'
    gerar_termo_link.allow_tags = True


@admin.register(Rescisao)
class RescisaoAdmin(admin.ModelAdmin):
    list_display = ('contrato__numero_contrato', 'contrato__estagiario', 'contrato__parte_concedente', 'data_rescisao', 'gerar_termo_link')
    search_fields = ('contrato__numero_contrato', 'contrato__estagiario__candidato__nome', 'contrato__parte_concedente__razao_social')
    list_filter = ('contrato__parte_concedente', 'data_rescisao')

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('rescisao-gerar-termo-rescisao', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Termo de Rescisão'
    gerar_termo_link.allow_tags = True


@admin.register(Estagiario)
class EstagiarioAdmin(admin.ModelAdmin):
    list_display = ('candidato', 'candidato__curso', 'candidato__serie_semestre', 'instituicao_ensino__razao_social')
    search_fields = ('candidato__nome', 'candidato__curso', 'candidato__serie_semestre', 'instituicao_ensino__razao_social')
    list_filter = ('candidato__curso', 'candidato__serie_semestre', 'instituicao_ensino__razao_social')


@admin.register(InstituicaoEnsino)
class InstituicaoEnsinoAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')


@admin.register(ParteConcedente)
class ParteConcedenteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')


@admin.register(AgenteIntegrador)
class AgenteIntegadorAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')


class CartaEncaminhamentoInline(admin.TabularInline):
    model = CartaEncaminhamento
    extra = 1


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rg', 'celular', 'email', 'instituicao_ensino', 'gerar_termo_link')
    search_fields = ('nome', 'bairro', 'cpf', 'rg')
    list_filter = ('nome', 'bairro', 'cpf', 'rg')

    inlines = [CartaEncaminhamentoInline]
    inlines = [Arquivos]

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('candidato-gerar-cadastro', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Ficha de Cadastro'
    gerar_termo_link.allow_tags = True

    def get_readonly_fields(self, request, obj = None):
        """"Define o campo observacoes como somente leitura se o usuário não perterncer ao grupo Recrutamento"""
        readonly_fields = super().get_readonly_fields(request, obj)

        if request.user.is_superuser:
            return [] # nenhum campo será somente leitura

        if not request.user.groups.filter(name='Recrutamento').exists():
            # se ele não estiver no grupo, o campo observacoes será somente leitura
            return readonly_fields + ('observacoes',)

        return readonly_fields

    def get_inlines(self, request, obj=None):
        if request.user.is_superuser:
            return self.inlines

        return []
