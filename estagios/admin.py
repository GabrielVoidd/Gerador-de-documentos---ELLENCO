from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Contrato, Rescisao, ParteConcedente, AgenteIntegrador, Estagiario, InstituicaoEnsino, Candidato, \
    CartaEncaminhamento, Arquivos, Empresa, DetalhesEmpresa, DetalhesParteConcedente, TipoEvento, Lancamento, Recibo, \
    MotivoRescisao, ReciboRescisao, LancamentoRescisao, ContratoSocial, Aditivo, CriterioExclusao, ContratoAceite, \
    DetalhesContratoAceite
from nested_inline.admin import NestedTabularInline, NestedModelAdmin
import string, openpyxl
from django.http import HttpResponse
from django.forms import CheckboxSelectMultiple
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from datetime import date, timedelta
import re

admin.site.unregister(User)


class VencimentoContratoFilter(admin.SimpleListFilter):
    title = 'Urgência de Vencimento'

    # O parâmetro que vai na URL (ex: ?vencimento=15_dias)
    parameter_name = 'vencimento'

    def lookups(self, request, model_admin):
        return (
            ('vencidos', 'Já vencidos'),
            ('15_dias', 'Vencem nos próximos 15 dias'),
            ('30_dias', 'Vencem nos próximos 30 dias'),
            ('60_dias', 'Vencem nos próximos 60 dias')
        )

    def queryset(self, request, queryset):
        # A lógica da filtragem
        hoje = date.today()

        if self.value() == 'vencidos':
            return queryset.filter(data_termino_prevista__lt=hoje)

        if self.value() == '15_dias':
            limite = hoje + timedelta(days=15)
            # Filtra de hoje até daqui 15 dias
            return queryset.filter(data_termino_prevista__gte=hoje, data_termino_prevista__lt=limite)

        if self.value() == '30_dias':
            limite = hoje + timedelta(days=30)
            return queryset.filter(data_termino_prevista__gte=hoje, data_termino_prevista__lt=limite)

        if self.value() == '60_dias':
            limite = hoje + timedelta(days=60)
            return queryset.filter(data_termino_prevista__gte=hoje, data_termino_prevista__lt=limite)

        return queryset


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('estagiario', 'parte_concedente', 'data_inicio', 'gerar_termo_link', 'status_cor', 'assinatura_icon')
    search_fields = ('numero_contrato', 'estagiario__candidato__nome', 'parte_concedente__razao_social')
    list_filter = (VencimentoContratoFilter, 'parte_concedente', 'data_inicio')
    autocomplete_fields = ['parte_concedente', 'estagiario']

    def assinatura_icon(self, obj):
        if obj.assinatura:
            # Tamanho (1.2rem) e cor (orange) pra destacar.
            return format_html('<span style="color: orange; font-size: 1.4rem;">★</span>')

        # Se for False, mantém o 'X' vermelho padrão do Django
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="Não Assinado">')

    # Configurações da coluna
    assinatura_icon.short_description = 'Assinatura'  # Nome que aparece no cabeçalho da tabela
    assinatura_icon.admin_order_field = 'assinatura' # Permite ordenar a coluna clicando no cabeçalho

    def status_cor(self, obj):
        if not obj.data_termino_prevista:
            return ''

        hoje = date.today()
        dias_restantes = (obj.data_termino_prevista - hoje).days

        color = ''

        # Lógica das cores (hexadecimais)
        if dias_restantes <= 15:
            color = '#ff6666' # Vermelho forte
        elif dias_restantes <= 30:
            color = '#ffb3b3' # Vermelho médio
        elif dias_restantes <= 60:
            color = '#ffe6e6' # Vermelho claro

        # Retorna um span oculto com a cor, que o JS vai ler
        return format_html(
            '<span class="row-color-indicator" style="display:none;" data-color="{}"></span>',
            color
        )

    status_cor.short_description = ''

    class Media:
        js = ('js/admin_row_color.js',)

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

    # def get_model_perms(self, request):
    #     if request.user.is_superuser:
    #         return super().get_model_perms(request)
    #     return {}


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
        'nome', 'rg', 'celular', 'botao_whatsapp', 'email', 'instituicao_ensino', 'gerar_termo_link', 'data_cadastro', 'restrito')
    search_fields = ('nome', 'bairro', 'cpf', 'rg')
    list_filter = (FiltroPrimeiraLetra, 'bairro', 'escolaridade', 'ano_semestre', 'criterio_exclusao__criterio',
                   'instituicao_ensino__razao_social')
    actions = ['exportar_para_excel']
    autocomplete_fields = ['instituicao_ensino']
    list_per_page = 20

    def get_search_results(self, request, queryset, search_term):
        # 1. Executa a busca padrão do Django
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # 2. Se houver um termo de busca, é procurado nos labels do TextChoices
        if search_term:
            choices_list = self.model._meta.get_field('periodo').choices
            # Encontra quais chaves tem os labels batendo com a busca
            chaves_encontradas = [
                valor for valor, label in choices_list
                if search_term.lower() in label.lower()
            ]

            # 3. Se achou alguma chave correspondente, filtra o queryset
            if chaves_encontradas:
                # Usando |= (or) para somar os resultados que o Django já encontrou
                queryset |= self.model.objects.filter(periodo__in=chaves_encontradas)

        return queryset, use_distinct

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

    def botao_whatsapp(self, obj):
        if not obj.celular:
            return '-'

        # \D significa 'tudo o que não for dígito'
        apenas_numeros = re.sub(r'\D', '', str(obj.celular or ''))

        if not apenas_numeros.startswith('55'):
            apenas_numeros = f'55{apenas_numeros}'

        url = f'https://wa.me/{apenas_numeros}?'

        return format_html(
            '''
            <a href="{}" target="_blank" style="
                background-color: #25D366; 
                color: white; 
                padding: 5px 10px; 
                border-radius: 20px; 
                text-decoration: none; 
                font-weight: bold; 
                font-size: 12px;
                white-space: nowrap;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 80px;
            ">Abrir WhatsApp</a>''',
            url
        )

    botao_whatsapp.short_description = 'Contato'
    botao_whatsapp.allow_tags = True

    class Media:
        # css = {'all': ('admin/css/custom_admin.css',)}
        js = ('js/admin_custom.js', 'js/jquery.mask.min.js', 'js/mascaras_admin.js', 'js/mascara_cpf_admin.js',
              'js/mascara_rg_admin.js', 'js/viacep_admin.js')

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
                fields.remove('serie_semestre')
                fields.remove('criterio_exclusao')
                fields.remove('observacoes')
                fields.remove('restrito')

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

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


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


class DetalhesContratoAceiteInline(admin.TabularInline):
    model = DetalhesContratoAceite
    extra = 1


@admin.register(ContratoAceite)
class ContratoAceiteAdmin(admin.ModelAdmin):
    list_display = ('parte_concedente__razao_social', 'plano', 'gerar_termo_link')
    list_filter = ('plano',)

    inlines = [DetalhesContratoAceiteInline]

    def gerar_termo_link(self, obj):
        # Cria a URL para o endpoint da API que gera o PDF
        url = reverse('contrato-aceite-gerar-contrato-aceite', kwargs={'pk': obj.pk})
        return format_html('<a class="button" href="{}" target="_blank">Gerar Contrato R&S</a>', url)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = set(super().get_readonly_fields(request, obj))

        # Se quem está logado NÃO é superuser, tornamos alguns campos sensíveis apenas leitura
        if not request.user.is_superuser:
            readonly_fields.add('is_superuser')
            readonly_fields.add('user_permissions')

        return list(readonly_fields)

    def get_fieldsets(self, request, obj=None):
        # Opcional: Se você quiser ESCONDER campos inteiros em vez de apenas travar
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # Aqui você poderia filtrar campos específicos se quisesse
            pass
        return fieldsets
