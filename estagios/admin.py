from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Contrato, Rescisao, ParteConcedente, AgenteIntegrador, Estagiario, InstituicaoEnsino, Candidato, \
    CartaEncaminhamento, Arquivos, Empresa, DetalhesEmpresa, DetalhesParteConcedente, TipoEvento, Lancamento, Recibo, \
    MotivoRescisao, ReciboRescisao, LancamentoRescisao, ContratoSocial, Aditivo, CriterioExclusao
from nested_inline.admin import NestedTabularInline, NestedModelAdmin
import string, openpyxl
from django.http import HttpResponse


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('numero_contrato', 'estagiario', 'parte_concedente', 'data_inicio', 'gerar_termo_link')
    search_fields = ('numero_contrato', 'estagiario__candidato__nome', 'parte_concedente__razao_social')
    list_filter = ('parte_concedente', 'data_inicio')
    autocomplete_fields = ['parte_concedente', 'estagiario']

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('contrato-gerar-termo-compromisso', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Termo de Compromisso'
    gerar_termo_link.allow_tags = True

    actions = ['exportar_para_excel']

    @admin.action(description='Exportar contratos Excel')
    def exportar_para_excel(self, request, queryset):
        # Configuração do Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="contratos.xlsx"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Contratos'
        ws.append(['Nome da Empresa', 'CNPJ', 'Nome do Estagiário', 'CPF', 'Nome da Escola / Faculdade',
               'Data de Início', 'Data de Término Prevista', 'Valor da Bolsa'])

        queryset = Contrato.objects.all().values_list(
            'parte_concedente__razao_social', 'parte_concedente__cnpj', 'estagiario__candidato__nome',
            'estagiario__candidato__cpf', 'estagiario__candidato__instituicao_ensino__razao_social',
            'data_inicio', 'data_termino_prevista', 'valor_bolsa'
        )

        # Preenchendo os dados
        for linha in queryset:
            # Cada linha é uma tupla ('Empresa X', '46536567/0001-99',)
            ws.append(linha)

        wb.save(response)
        return response


@admin.register(MotivoRescisao)
class MotivoRescisaoAdmin(admin.ModelAdmin):
    list_display = ('motivo',)


@admin.register(Rescisao)
class RescisaoAdmin(admin.ModelAdmin):
    list_display = ('contrato__numero_contrato', 'contrato__estagiario', 'contrato__parte_concedente', 'data_rescisao', 'gerar_termo_link')
    search_fields = ('contrato__numero_contrato', 'contrato__estagiario__candidato__nome', 'contrato__parte_concedente__razao_social')
    list_filter = ('contrato__parte_concedente', 'data_rescisao')
    autocomplete_fields = ['contrato']

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
    autocomplete_fields = ['candidato', 'instituicao_ensino']


@admin.register(InstituicaoEnsino)
class InstituicaoEnsinoAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')


class DetalhesParteConcedenteInline(admin.TabularInline):
    model = DetalhesParteConcedente
    fields = (
        'dia_pagamento_estagiario', 'dia_cobranca_agencia', 'dia_fechamento', 'mensalidade_contrato', 'taxa_cliente')
    extra = 1


@admin.register(ParteConcedente)
class ParteConcedenteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')

    inlines = [DetalhesParteConcedenteInline]

    def get_inlines(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='Comercial').exists():
            return self.inlines

        return []


@admin.register(AgenteIntegrador)
class AgenteIntegadorAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone', 'email')
    search_fields = ('razao_social', 'cnpj', 'cidade')
    list_filter = ('razao_social', 'cidade')


class CartaEncaminhamentoInline(NestedTabularInline):
    model = CartaEncaminhamento
    extra = 1


class ArquivosInline(NestedTabularInline):
    model = Arquivos
    extra = 1


class DetalhesEmpresaInline(NestedTabularInline):
    model = DetalhesEmpresa
    fields = ('arquivos',)
    extra = 1


class EmpresaInline(NestedTabularInline):
    model = Empresa
    fields = ('nome', 'observacoes')
    extra = 1
    show_change_link = True
    inlines = [DetalhesEmpresaInline]


class FiltroPrimeiraLetra(admin.SimpleListFilter):
    title = 'primeira letra' # Título que aparece na barra lateral
    parameter_name = 'letra' # Parâmetro que vai na URL

    def lookups(self, request, model_admin):
        return [(letra, letra) for letra in string.ascii_uppercase]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(nome__istartswith=self.value())
        return queryset


@admin.register(CriterioExclusao)
class CriterioExclusaoAdmin(admin.ModelAdmin):
    list_display = ('criterio',)
    list_filter = ('criterio',)


@admin.register(Candidato)
class CandidatoAdmin(NestedModelAdmin):
    list_display = (
        'nome', 'rg', 'celular', 'email', 'instituicao_ensino', 'gerar_termo_link', 'data_cadastro', 'restrito')
    search_fields = ('nome', 'bairro', 'cpf', 'rg')
    list_filter = (FiltroPrimeiraLetra, 'bairro', 'escolaridade', 'ano_semestre', 'criterio_exclusao__criterio')
    actions = ['exportar_para_excel']
    autocomplete_fields = ['instituicao_ensino']
    list_per_page = 20

    def exportar_para_excel(self, request, queryset):
        '''Exporta os dados do candidato junto com a Parte Concedente e Instituição de Ensino. Inclui somente os
        registros selecionados no admin'''
        queryset = queryset.select_related(
            'contrato__parte_concedente', 'contrato__instituicao_ensino'
        )

        data = []
        for candidato in queryset:
            contrato = getattr(candidato, 'contrato', None)
            parte_concedente = getattr(candidato, 'parte_concedente', None)
            instituicao = getattr(candidato, 'instituicao_ensino', None)

            data.append({
                # --- CANDIDATO ---
                'Nome Candidato': candidato.nome,
                'CPF Candidato': candidato.cpf,
                'Telefone Candidato': candidato.telefone if hasattr(candidato, 'telefone') else '',
                'Email Candidato': candidato.email,

                # --- PARTE CONCEDENTE ---
                'Razão Social (Parte Concedente)': parte_concedente.razao_social if parte_concedente else '',
                'CNPJ (Parte Concedente)': parte_concedente.cnpj if parte_concedente else '',
            })


    class Media:
        # css = {'all': ('admin/css/custom_admin.css',)}
        js = ('js/admin_custom.js',)

    inlines = [CartaEncaminhamentoInline, ArquivosInline, EmpresaInline]

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('candidato-gerar-cadastro', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Ficha de Cadastro'
    gerar_termo_link.allow_tags = True

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))

        tem_permissao = request.user.is_superuser or request.user.groups.filter(name='Recrutamento').exists()

        if not tem_permissao:
            if 'serie_semestre' in fields:
                fields.remove('serie_semestre', 'criterio_exclusao')

        return fields

    def get_readonly_fields(self, request, obj = None):
        """"Define os campos observacoes e restrito como somente leitura se o usuário não perterncer ao grupo Recrutamento"""
        readonly_fields = super().get_readonly_fields(request, obj)

        if request.user.is_superuser:
            return [] # nenhum campo será somente leitura

        if not request.user.groups.filter(name='Recrutamento').exists():
            # se ele não estiver no grupo, o campo observacoes será somente leitura
            return readonly_fields + ('observacoes', 'restrito')

        return readonly_fields

    def get_inlines(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='Recrutamento').exists():
            return self.inlines

        return []


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo')


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ('recibo', 'tipo_evento', 'valor')


@admin.register(LancamentoRescisao)
class LancamentoRescisaoAdmin(admin.ModelAdmin):
    list_display = ('recibo_rescisao', 'tipo_evento', 'valor')


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('estagiario_nome', 'contrato__parte_concedente', 'gerar_termo_link')
    list_filter = ('estagiario_nome', 'contrato__parte_concedente')
    search_fields = ('estagiario_nome', 'contrato__parte_concedente__razao_social')
    readonly_fields = ('valor', 'dias_trabalhados', 'estagiario_nome', 'parte_concedente_nome', 'valor_bolsa',
        'data_inicio', 'data_fim')

    class Media:
        js = ('js/preencher_recibo.js',)

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('recibo-gerar-recibo-pagamento', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)

    gerar_termo_link.short_description = 'Recibo de pagamento bolsa auxílio'
    gerar_termo_link.allow_tags = True


@admin.register(ReciboRescisao)
class ReciboRescisaoAdmin(admin.ModelAdmin):
    list_display = ('parte_concedente_nome', 'estagiario_nome', 'gerar_termo_link')
    search_fields = ('parte_concedente_nome', 'estagiario_nome')
    list_filter = ('parte_concedente_nome', 'estagiario_nome')
    list_per_page = 20

    class Media:
        js = ('js/preencher_recibo.js',)

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('recibo-rescisao-gerar-recibo-rescisao', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar PDF</a>', url)


@admin.register(ContratoSocial)
class ContratoSocialAdmin(admin.ModelAdmin):
    list_display = ('parte_concedente__razao_social', 'gerar_termo_link')
    search_fields = ('parte_concedente__razao_social',)

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('contrato-social-gerar-contrato-social', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar Contrato</a>', url)


@admin.register(Aditivo)
class AditivoAdmin(admin.ModelAdmin):
    list_display = ('contrato_social__parte_concedente__razao_social', 'data_cadastro', 'gerar_termo_link')
    search_fields = ('contrato_social__parte_concedente__razao_social',)

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('aditivo-gerar-aditivo', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar Aditivo</a>', url)
