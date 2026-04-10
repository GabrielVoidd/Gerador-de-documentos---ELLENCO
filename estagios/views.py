from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .forms import CandidatoForm, CandidatoStatusForm, VagaForm, ParteConcedenteForm, CandidaturaForm, VagaEditForm, \
    CandidaturaUpdateForm, CandidatoDocumentosForm, ArquivosFormSet, EmpresasFormSet
import os
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, get_object_or_404, redirect
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato, \
    TipoEvento, Lancamento, Recibo, ReciboRescisao, LancamentoRescisao, ContratoSocial, Aditivo, ContratoAceite, \
    RegistroContatoEmpresa, Chamados, Vaga, Candidatura
from .serializers import (
    InstituicaoEnsinoSerializer, ParteConcedenteSerializer, EstagiarioSerializer, AgenteIntegradorSerializer,
    ContratoSerializer, ContratoCreateSerializer, RescisaoSerializer, RescisaoCreateSerializer, CandidatoSerializer,
    TipoEventoSerializer, LancamentoSerializer, ReciboSerializer, ReciboRescisaoSerializer,
    LancamentoRescisaoSerializer, ContratoSocialSerializer, Aditivo, AditivoSerializer, CriterioExclusao, \
    CriterioExclusaoSerializer, ContratoAceiteSerializer, RegistroContatoEmpresaSerializer
)
from django.db import transaction
import openpyxl
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def check_rs(user):
    if user.is_superuser or user.groups.filter(name='Recrutamento').exists():
        return True
    raise PermissionDenied("Você não tem permissão para acessar o Recrutamento.")


# Função auxiliar que define quem manda na página
def is_recrutamento(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='Recrutamento').exists()


@login_required
def login_dispatcher(request):
    user = request.user

    # Se for superuser ou do Recrutamento, vai pra Home R&S
    if user.is_superuser or user.groups.filter(name='Recrutamento').exists():
        return redirect('dashboard_home')

    # Se for Comercial
    elif user.groups.filter(name='Comercial').exists():
        return redirect('dashboard_comercial')

    # Se for ADM
    elif user.groups.filter(name='RH').exists():
        return redirect('dashboard_adm')

    # Fallback (caso o usuário não tenha grupo nenhum)
    return redirect('/admin/')


class RecrutamentoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Recrutamento').exists()


class InstituicaoEnsinoViewSet(viewsets.ModelViewSet):
    queryset = InstituicaoEnsino.objects.all()
    serializer_class = InstituicaoEnsinoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['razao_social']


class ParteConcedenteViewSet(viewsets.ModelViewSet):
    queryset = ParteConcedente.objects.all()
    serializer_class = ParteConcedenteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['razao_social']


class EstagiarioViewSet(viewsets.ModelViewSet):
    queryset = Estagiario.objects.all()
    serializer_class = EstagiarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['estagiario__nome', 'parte_concedente__razao_social', 'setor', 'numero_contrato']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return ContratoCreateSerializer
        return ContratoSerializer

    @action(detail=True, methods=['get'], url_path='gerar-termo-compromisso', url_name='gerar-termo-compromisso')
    def gerar_termo_compromisso(self, request, pk=None):
        usuario_que_gerou = request.user
        contrato = self.get_object()
        candidato = contrato.estagiario.candidato

        # --- Verificação de maioridade para renderização do campo de assinatura do responsável ---
        precisa_responsavel = False
        if candidato.data_nascimento:
            hoje = date.today()
            nasc = candidato.data_nascimento

            # Cálculo da idade
            idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

            if idade < 18:
                precisa_responsavel = True

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do contrato
        html_string = render_to_string('estagios/termo_compromisso.html',
    {'contrato': contrato, 'logo_path': logo_path, 'usuario_logado': usuario_que_gerou,
            'precisa_responsavel': precisa_responsavel})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TCE_{contrato.estagiario.candidato.nome}.pdf"'

        return response

    @action(detail=True, methods=['get'], url_path='visualizar-termo', url_name='visualizar-termo-compromisso')
    def visualizer_termo_compromisso(self, request, pk=None):
        """"
        Essa action busca um contrato e renderiza a página HTML de visualização usando o template base com menu,
        cabeçalho, etc
        """
        # 1. Busca o objeto do contrato
        contrato = self.get_object()
        # 2. Prepara o contexto para enviar ao template
        context = {
            'contrato': contrato,
        }

        return render(request, 'estagios/contrato.html', context)


class RescisaoViewSet(viewsets.ModelViewSet):
    queryset = Rescisao.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['contrato.estagiario.nome']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return RescisaoCreateSerializer
        return RescisaoSerializer

    @action(detail=True, methods=['get'], url_path='gerar-termo-rescisao', url_name='gerar-termo-rescisao')
    def gerar_termo_rescisao(self, request, pk=None):
        rescisao = self.get_object()
        candidato = rescisao.contrato.estagiario.candidato

        # --- Verificação de maioridade para renderização do campo de assinatura do responsável ---
        precisa_responsavel = False
        if candidato.data_nascimento:
            hoje = date.today()
            nasc = candidato.data_nascimento

            # Cálculo da idade
            idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

            if idade < 18:
                precisa_responsavel = True

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        html_string = render_to_string('estagios/termo_rescisao.html',
                                       {'rescisao': rescisao, 'logo_path': logo_path, 'precisa_responsavel': precisa_responsavel})
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Rescisao_{rescisao.contrato.estagiario.candidato.nome}.pdf"'

        return response

    @action(detail=True, methods=['get'], url_path='visualizar-termo-rescisao', url_name='visualizar-termo-rescisao')
    def visualizer_termo_rescisao(self, request, pk=None):
        """"
        Essa action busca um contrato e renderiza a página HTML de visualização usando o template base com menu,
        cabeçalho, etc
        """
        # 1. Busca o objeto do contrato
        rescisao = self.get_object()
        # 2. Prepara o contexto para enviar ao template
        context = {
            'rescisao': rescisao,
        }

        return render(request, 'estagios/rescisao.html', context)


class AgenteIntegracaoViewSet(viewsets.ModelViewSet):
    queryset = AgenteIntegrador.objects.all()
    serializer_class = AgenteIntegradorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['razao_social']


class ContratoListView(ListView):
    model = Contrato
    template_name = 'estagios/contrato_list.html'
    context_object_name = 'contratos'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(estagiario__nome__icontains=query)
        return queryset.order_by('-data_inicio')


class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'instituicap_ensino__razao_social']

    @action(detail=True, methods=['get'], url_path='gerar-cadastro', url_name='gerar-cadastro')
    def gerar_cadastro(self, request, pk=None):
        candidato = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/cadastro_recrutamento.html',
                                       {'candidato': candidato, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Ficha_Cadastro_{candidato.nome}.pdf"'

        return response


class ContratoDetailView(DetailView):
    model = Contrato
    template_name = 'estagios/contrato_detail.html'
    context_object_name = 'contrato'


class ContratoDeleteView(SuccessMessageMixin, DeleteView):
    model = Contrato
    template_name = 'estagios/contrato_confirm_delete.html'
    success_url = reverse_lazy('contrato_lista')
    success_message = 'Contrato deletado com sucesso.'


class TipoEventoViewSet(viewsets.ModelViewSet):
    queryset = TipoEvento.objects.all()
    serializer_class = TipoEventoSerializer


class LancamentoViewSet(viewsets.ModelViewSet):
    queryset = Lancamento.objects.all()
    serializer_class = LancamentoSerializer


class LancamentoRescisaoViewSet(viewsets.ModelViewSet):
    queryset = LancamentoRescisao.objects.all()
    serializer_class = LancamentoRescisaoSerializer


class ReciboViewSet(viewsets.ModelViewSet):
    queryset = Recibo.objects.all()
    serializer_class = ReciboSerializer

    def create(self, request, *args, **kwargs):
        contrato_id = request.data.get('contrato_id')
        if not contrato_id:
            return Response({'error': 'O campo "contrato_id" é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contrato = Contrato.objects.get(id=contrato_id)
        except Contrato.DoesNotExist:
            return Response({'error': 'Contrato não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Texto informativo sobre benefício e horário
        texto_beneficio = '(BENEFÍCIO): A CRITÉRIO'
        texto_horario = contrato.jornada_estagio
        texto_combinado = f'{texto_beneficio} {texto_horario}'

        # Determina a data de referência (1° dia do mês anterior)
        hoje = date.today()
        data_referencia = hoje.replace(day=1) - relativedelta(months=1)

        # Evita recibos duplicados no mesmo mês para o mesmo contrato
        if Recibo.objects.filter(contrato=contrato, data_referencia=data_referencia).exists():
            mes_ref = data_referencia.strftime('%m/%Y')
            return Response(
                {'error': f'Já existe um recibo para este contrato na referência {mes_ref}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- CRIAÇÃO DO RECIBO ---
        try:
            novo_recibo = Recibo(
                contrato=contrato, beneficio_horario=texto_combinado,
                data_referencia=data_referencia, dias_falta=int(request.data.get('dias_falta', 0)),
            )

            novo_recibo.save()

        except Exception as e:
            return Response({'error': f'Erro ao criar o recibo: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # --- BOLSA AUXÍLIO ---
        try:
            tipo_bolsa = TipoEvento.objects.get(descricao='Bolsa Auxílio')
            Lancamento.objects.create(
                recibo=novo_recibo, tipo_evento=tipo_bolsa, valor=novo_recibo.valor,
            )
        except TipoEvento.DoesNotExist:
            return Response(
                {'error': 'TipoEvento "Bolsa Auxílio" não encontrado. Configure-o antes de criar recibos'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': f'Erro ao criar lançamento inicial: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(novo_recibo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='gerar-recibo-pagamento', url_name='gerar-recibo-pagamento')
    def gerar_recibo_pagamento(self, request, pk=None):
        recibo = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/recibo_pagamento.html',
                                       {'recibo': recibo, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Recibo_Bolsa_Auxilio_{recibo.contrato.estagiario.candidato.nome}.pdf"'

        return response


def get_contrato_data(request, contrato_id):
    try:
        contrato = Contrato.objects.get(pk=contrato_id)

        data = {
            'estagiario_nome': contrato.estagiario.candidato.nome,
            'parte_concedente_nome': contrato.parte_concedente.razao_social,
            'valor_bolsa': contrato.valor_bolsa,
            'data_inicio': contrato.data_inicio,
            'data_fim': contrato.data_termino_prevista
        }

        return JsonResponse(data)
    except Contrato.DoesNotExist:
        return JsonResponse({'error': 'Contrato não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class ReciboRescisaoViewSet(viewsets.ModelViewSet):
    queryset = ReciboRescisao.objects.all().order_by('-data_rescisao')
    serializer_class = ReciboRescisaoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    context_object_name = 'recibo_rescisao'

    # Filtros
    filterset_fields = ['contrato', 'motivo_rescisao', 'data_rescisao']

    # Campos de busca
    search_fields = ['estagiario_nome', 'parte_concedente_nome']

    # Campos para ordenação
    ordering_fields = ['data_rescisao', 'data_pagamento', 'estagiario_nome', 'valor_liquido']

    # Ordenação padrão
    ordering = ['-data_rescisao']

    @action(detail=True, methods=['post'])
    def adicionar_lancamento(self, request, pk=None):
        recibo = self.get_object()
        serializer = LancamentoRescisaoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(recibo_rescisao=recibo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def simular_calculos(self, request, pk=None):
        """Endpoint para simular cálculos sem salvar"""
        instance = self.get_object()

        # Recria os cálculos
        instance.calcular_totais()

        data = {
            'saldo_salario': instance.saldo_salario, 'recesso_remunerado': instance.recesso_remunerado,
            'total_creditos': instance.total_creditos, 'total_debitos': instance.total_debitos,
            'valor_liquido': instance.valor_liquido,
        }

        return Response(data)

    @action(detail=True, methods=['get'])
    def por_estagiario(self, request):
        """Endpoint para filtrar recibos por estagiário"""
        estagiario_nome = request.query_params.get('estagiario', None)

        if estagiario_nome:
            recibos = ReciboRescisao.objects.filter(estagiario_nome__icontains=estagiario_nome)
            serializer = self.get_serializer(recibos, many=True)
            return Response(serializer.data)

        return Response([])

    @action(detail=True, methods=['get'])
    def por_periodo(self, request):
        """Endpoint para filtrar recibos por período"""
        data_inicio = request.query_params.get('data_inicio', None)
        data_fim = request.query_params.get('data_fim', None)

        if data_inicio and data_fim:
            recibos = ReciboRescisao.objects.filter(
                data_rescisao__gte=data_inicio, data_rescisao__lte=data_fim
            )
            serializer = self.get_serializer(recibos, many=True)
            return Response(serializer.data)

        return Response({'error': 'Parâmetros data_inicio e data_fim são obrigatórios'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='gerar-recibo-rescisao', url_name='gerar-recibo-rescisao')
    def gerar_recibo_rescisao(self, request, pk=None):
        recibo_rescisao = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/recibo_rescisao.html',
                                       {'recibo_rescisao': recibo_rescisao, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="Recibo_Bolsa_Auxilio_{recibo_rescisao.contrato.estagiario.candidato.nome}.pdf"'

        return response

    # ---
    @action(detail=False, methods=['post'], url_path='gerar-lote-empresa')
    def gerar_lote_empresa(self, request):
        '''Gera recibos para todos os estagiários ativos de uma empresa e retorna um único PDF para todos eles'''

        parte_concedente_id = request.data.get('parte_concedente_id')
        dias_falta_padrao = int(request.data.get('dias_falta', 0))

        if not parte_concedente_id:
            return Response({'error': 'Empresa (parte_concedente_id) é obrigatória'}, status=status.HTTP_400_BAD_REQUEST)

        # Define a data de referência (mês anterior)
        hoje = date.today()
        data_referencia = hoje.replace(day=1) - relativedelta(months=1)

        # Busca contratos ativos da empresa
        contratos = Contrato.objects.filter(
            parte_concedente_id=parte_concedente_id,
            data_termino_prevista__gte=data_referencia
        ).select_related('estagiario__candidato', 'parte_concedente')

        if not contratos.exists():
            return Response({'error': 'Nenhum contrato ativo encontrado para esta empresa'}, status=status.HTTP_404_NOT_FOUND)

        recibos_gerados = []

        try:
            with transaction.atomic():
                for contrato in contratos:
                    # Verificação de duplicidade
                    if Recibo.objects.filter(contrato=contrato, data_referencia=data_referencia).exists():
                        # Se já existe, pega o existente para imprimir ou pula
                        recibo_existente = Recibo.objects.get(contrato=contrato, data_referencia=data_referencia)
                        recibos_gerados.append(recibo_existente)

                    # Lógica de texto
                    texto_beneficio = '(BENEFÍCIO): A CRITÉRIO'
                    texto_horario = contrato.jornada_estagio or ''
                    texto_combinado = f'{texto_beneficio} {texto_horario}'

                    # Criação do recibo
                    novo_recibo = Recibo.objects.create(
                        contrato=contrato,
                        beneficio_horario=texto_combinado,
                        data_referencia=data_referencia,
                        dias_falta=dias_falta_padrao
                    )

                    # Criação do lançamento
                    tipo_bolsa = TipoEvento.objects.filter(descricao='Bolsa Auxílio').first()
                    if tipo_bolsa:
                        Lancamento.objects.create(
                            recibo=novo_recibo,
                            tipo_evento=tipo_bolsa,
                            valor=contrato.valor_bolsa
                        )

                    recibos_gerados.append(novo_recibo)

            return self._gerar_pdf_lote(recibos_gerados, request)

        except Exception as e:
            return Response({'error': f'Erro processando lote: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    def _gerar_pdf_lote(self, lista_recibos, request):
        '''Método auxiliar para gerar PDF com múltiplos recibos'''
        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza UM html contendo TODOS os recibos
        html_string = render_to_string('estagios/recibo_pagamento.html', {
            'lista_recibos': lista_recibos,
            'logo_path': logo_path
        })

        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        nome_empresa = lista_recibos[0].contrato.parte_concedente.razao_social.replace(' ', '_')
        mes_ref = lista_recibos[0].data_referencia.strftime('%m-%Y')
        response['Content-Disposition'] = f'attachment; filename="Recibos_{nome_empresa}_{mes_ref}.pdf"'

        return response
    # ---


class ContratoSocialViewSet(viewsets.ModelViewSet):
    queryset = ContratoSocial.objects.all()
    serializer_class = ContratoSocialSerializer

    @action(detail=True, methods=['get'], url_path='gerar-contrato-social', url_name='gerar-contrato-social')
    def gerar_contrato_social(self, request, pk=None):
        contrato_social = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/contrato_social.html',
                                       {'contrato_social': contrato_social, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Empresa_x_Empresa_{contrato_social.parte_concedente.razao_social}.pdf"'

        return response


class AditivoViewSet(viewsets.ModelViewSet):
    queryset = Aditivo.objects.all()
    serializer_class = AditivoSerializer

    @action(detail=True, methods=['get'], url_path='gerar-aditivo', url_name='gerar-aditivo')
    def gerar_contrato_social(self, request, pk=None):
        aditivo = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/aditivo.html',
                                       {'aditivo': aditivo, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="aditivo_{aditivo.contrato_social.parte_concedente.razao_social}.pdf"'

        return response


class CriterioExclusaoViewSet(viewsets.ModelViewSet):
    queryset = CriterioExclusao.objects.all()
    serializer_class = CriterioExclusaoSerializer


class ContratoAceiteViewSet(viewsets.ModelViewSet):
    queryset = ContratoAceite.objects.all()
    serializer_class = ContratoAceiteSerializer

    @action(detail=True, methods=['get'], url_path='gerar-contrato-aceite', url_name='gerar-contrato-aceite')
    def gerar_contrato_aceite(self, request, pk=None):
        contrato_aceite = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/contrato_aceite.html',
                                       {'contrato_aceite': contrato_aceite, 'logo_path': logo_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="ContratoR&S_{contrato_aceite.parte_concedente.razao_social}.pdf"'

        return response


class RegistroContatoEmpresaViewSet(viewsets.ModelViewSet):
    queryset = RegistroContatoEmpresa.objects.all()
    serializer_class = RegistroContatoEmpresaSerializer


class ChamadosViewSet(viewsets.ModelViewSet):
    queryset = Chamados.objects.all()


@user_passes_test(check_rs)
class CandidatoCreateView(LoginRequiredMixin, CreateView):
    model = Candidato
    form_class = CandidatoForm
    template_name = 'estagios/candidato_form.html'
    success_url = reverse_lazy('candidato_sucesso')
    success_message = 'Seu cadastro foi realizado com sucesso!'

class CandidatoSucessoView(TemplateView):
    # Uma tela simples de "Obrigado" para ele não ficar perdido após salvar
    template_name = 'estagios/candidato_sucesso.html'


@user_passes_test(check_rs)
class CandidatoListView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Candidato
    template_name = 'estagios/candidato_list.html'
    context_object_name = 'candidatos'
    paginate_by = 20

    # O Django roda isso antes de abrir a página
    def test_func(self):
        return is_recrutamento(self.request.user)

    # (Opcional) Se quiser que dê uma tela de erro 403 ao invés de jogar pro login:
    def handle_no_permission(self):
        raise PermissionDenied("Você não tem permissão para acessar a base de candidatos.")

    def get_queryset(self):
        # select_related deixa a busca mais rápida (evita o problema N+1)
        queryset = Candidato.objects.select_related('instituicao_ensino').all().order_by('-data_cadastro')

        # 1. BARRA DE PESQUISA (q)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) |
                Q(cpf__icontains=q) |
                Q(rg__icontains=q) |
                Q(celular__icontains=q) |
                Q(bairro__icontains=q)
            )

        # 2. FILTROS LATERAIS (Dropdowns e Checkboxes)
        bairro = self.request.GET.get('bairro')
        if bairro:
            queryset = queryset.filter(bairro__icontains=bairro)

        escolaridade = self.request.GET.get('escolaridade')
        if escolaridade:
            queryset = queryset.filter(escolaridade=escolaridade)

        status = self.request.GET.get('status')
        if status:
            # Filtra pelos booleanos do seu banco dinamicamente
            if status == 'restrito':
                queryset = queryset.filter(restrito=True)
            elif status == 'em_processo':
                queryset = queryset.filter(em_processo=True)
            elif status == 'aprovado':
                queryset = queryset.filter(aprovado=True)
            elif status == 'trabalhando':
                queryset = queryset.filter(trabalhando=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passamos os choices para o template montar os selects automaticamente
        context['escolaridades'] = Candidato.Escolaridades.choices
        # Mantemos os filtros na URL para a paginação não perder a busca ao mudar de página
        context['filtros_url'] = self.request.GET.urlencode()
        # Busca todos os bairros preenchidos, sem repetir, em ordem alfabética
        context['bairros'] = Candidato.objects.exclude(bairro__isnull=True).exclude(bairro='').values_list('bairro',
                                                                                                           flat=True).distinct().order_by(
            'bairro')
        return context


# VIEW PARA EXPORTAR EXCEL (Ajustada com o caminho correto do banco)
@user_passes_test(check_rs)
def exportar_candidatos_excel(request):
    # Pega os mesmos parâmetros da URL para exportar só o que foi filtrado
    q = request.GET.get('q')
    queryset = Candidato.objects.select_related('instituicao_ensino', 'estagiario__contrato__parte_concedente').all()

    if q:
        queryset = queryset.filter(Q(nome__icontains=q) | Q(cpf__icontains=q))

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Candidatos'

    # Cabeçalhos
    headers = ['Nome', 'CPF', 'Celular', 'Email', 'Instituição de Ensino', 'Status', 'Empresa (Contrato)']
    sheet.append(headers)

    for c in queryset:
        # Puxa a empresa verificando se o candidato virou estagiário e tem contrato
        empresa = ''
        if hasattr(c, 'estagiario') and hasattr(c.estagiario, 'contrato'):
            empresa = c.estagiario.contrato.parte_concedente.razao_social

        # Define um status legível
        status_atual = 'Cadastrado'
        if c.trabalhando:
            status_atual = 'Trabalhando'
        elif c.em_processo:
            status_atual = 'Em Processo'

        sheet.append([
            c.nome, c.cpf, c.celular, c.email,
            c.instituicao_ensino.razao_social if c.instituicao_ensino else '',
            status_atual, empresa
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Candidatos_Filtrados.xlsx"'
    workbook.save(response)
    return response


class CandidatoPerfilView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Candidato
    form_class = CandidatoStatusForm
    template_name = 'estagios/candidato_perfil.html'
    context_object_name = 'candidato'

    # Mesma segurança da tela de busca!
    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_success_url(self):
        # Depois de salvar, recarrega a mesma página do perfil para a pessoa ver que salvou
        return reverse('perfil_candidato', kwargs={'pk': self.object.pk})


@user_passes_test(check_rs)
class VagaCreateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Vaga
    form_class = VagaForm
    template_name = 'estagios/vaga_form.html'

    # Se der tudo certo, joga a pessoa de volta pro Dashboard
    success_url = reverse_lazy('dashboard_home')

    def test_func(self):
        return is_recrutamento(self.request.user)


@user_passes_test(check_rs)
class ParteConcedenteCreateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ParteConcedente
    form_class = ParteConcedenteForm
    template_name = 'estagios/parte_concedente_form.html'

    success_url = reverse_lazy('dashboard_home')

    def test_func(self):
        return is_recrutamento(self.request.user)


@user_passes_test(check_rs)
class VagaListView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Vaga
    template_name = 'estagios/vaga_list.html'
    context_object_name = 'vagas'
    paginate_by = 15

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_queryset(self):
        # select_related deixa a consulta ao banco mais rápida puxando a empresa junto
        queryset = Vaga.objects.select_related('empresa').all().order_by('-data_abertura')

        # 1. Filtro de Texto (Título da Vaga ou Nome da Empresa)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(empresa__razao_social__icontains=q) |
                Q(empresa__nome__icontains=q)
            )

        # 2. Filtro de Status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa as opções de status para montar o Select do filtro dinamicamente
        context['status_choices'] = Vaga.StatusVaga.choices
        context['filtros_url'] = self.request.GET.urlencode()
        return context


@user_passes_test(check_rs)
class CandidaturaCreateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Candidatura
    form_class = CandidaturaForm
    template_name = 'estagios/candidatura_form.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def form_valid(self, form):
        # Pega o ID do candidato que veio na URL e já vincula automaticamente
        candidato = get_object_or_404(Candidato, pk=self.kwargs['pk'])
        form.instance.candidato = candidato
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Passa o nome do candidato para a tela para a recrutadora saber quem ela está vinculando
        context = super().get_context_data(**kwargs)
        context['candidato'] = get_object_or_404(Candidato, pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # Se der certo, devolve a recrutadora direto para o perfil dele!
        return reverse('perfil_candidato', kwargs={'pk': self.kwargs['pk']})


class VagaDetailView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Vaga
    template_name = 'estagios/vaga_detail.html'
    context_object_name = 'vaga'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Troca do .candidatura_set por uma busca direta
        context['candidatos_vinculados'] = Candidatura.objects.filter(
            vaga=self.object
        ).select_related('candidato').order_by('status')
        return context


class VagaUpdateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vaga
    form_class = VagaEditForm
    template_name = 'estagios/vaga_form.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_success_url(self):
        # Depois de salvar a edição, devolve a recrutadora pra tela de detalhes
        return reverse('vaga_detalhe', kwargs={'pk': self.object.pk})


class RelatorioRSView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'estagios/relatorios_rs.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. KPI Rápido
        context['total_vagas'] = Vaga.objects.count()
        context['vagas_abertas'] = Vaga.objects.filter(status='A').count()
        context['vagas_fechadas'] = Vaga.objects.filter(status='F').count()

        # 2. Dados para o Gráfico de Perdas
        perdas = Candidato.objects.aggregate(
            reprovados=Count('id', filter=Q(reprovado=True)),
            desistentes=Count('id', filter=Q(desistiu=True)),
            nao_compareceu=Count('id', filter=Q(nao_compareceu=True))
        )

        # Dicionário puro, sem json.dumps()
        context['grafico_perdas_json'] = {
            'labels': ['Reprovados', 'Desistiram', 'Não Compareceram'],
            'data': [perdas['reprovados'] or 0, perdas['desistentes'] or 0, perdas['nao_compareceu'] or 0]
        }

        # 3. Dados para o Gráfico de Funil
        status_candidaturas = Candidatura.objects.values('status').annotate(total=Count('id'))

        labels_funil = []
        data_funil = []
        mapa_status = dict(Candidatura._meta.get_field('status').choices)

        for item in status_candidaturas:
            labels_funil.append(mapa_status.get(item['status'], item['status']))
            data_funil.append(item['total'])

        # Dicionário puro, sem json.dumps()
        context['grafico_funil_json'] = {
            'labels': labels_funil,
            'data': data_funil
        }

        return context


class CandidaturaUpdateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Candidatura
    form_class = CandidaturaUpdateForm
    template_name = 'estagios/candidatura_form.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa o candidato para a tela para manter o nome dele lá em cima
        context['candidato'] = self.object.candidato
        return context

    def get_success_url(self):
        # Depois de salvar, devolve pro perfil do candidato
        return reverse('perfil_candidato', kwargs={'pk': self.object.candidato.pk})


class RelatorioBIView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'estagios/relatorios_bi.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Top Clientes (Empresas com mais vagas cadastradas)
        top_clientes = Vaga.objects.values('empresa__razao_social').annotate(total=Count('id')).order_by('-total')[:5]
        context['top_clientes_json'] = {
            'labels': [item['empresa__razao_social'] for item in top_clientes],
            'data': [item['total'] for item in top_clientes]
        }

        # 2. Top Instituições de Ensino (Fornecedoras de Candidatos)
        top_instituicoes = Candidato.objects.values('instituicao_ensino__razao_social').annotate(total=Count('id')).exclude(instituicao_ensino__isnull=True).order_by('-total')[:5]
        context['top_inst_json'] = {
            'labels': [item['instituicao_ensino__razao_social'] for item in top_instituicoes],
            'data': [item['total'] for item in top_instituicoes]
        }

        # 3. Top Bairros (Mapa de calor demográfico)
        top_bairros = Candidato.objects.values('bairro').annotate(total=Count('id')).exclude(bairro='').order_by('-total')[:5]
        context['top_bairros_json'] = {
            'labels': [item['bairro'] for item in top_bairros],
            'data': [item['total'] for item in top_bairros]
        }

        return context


class RelatorioContratosView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'estagios/relatorios_contratos.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        daqui_30_dias = hoje + timedelta(days=30)

        try:
            from .models import Contrato  # Agora sabemos que o nome é esse mesmo!

            # Contratos Ativos: Não foram rescindidos (data_rescisao é nula)
            contratos_ativos = Contrato.objects.filter(data_rescisao__isnull=True)

            context['total_ativos'] = contratos_ativos.count()

            # Filtra os que vencem nos próximos 30 dias usando a data_termino_prevista
            context['vencendo_30_dias'] = contratos_ativos.filter(
                data_termino_prevista__gte=hoje,
                data_termino_prevista__lte=daqui_30_dias
            ).select_related('estagiario', 'parte_concedente').order_by('data_termino_prevista')

            context['total_vencendo'] = context['vencendo_30_dias'].count()

        except ImportError:
            context['aviso_model'] = True
            context['total_ativos'] = 0
            context['total_vencendo'] = 0
            context['vencendo_30_dias'] = []

        return context


class CandidatoDocumentosUpdateView(RecrutamentoRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Candidato
    form_class = CandidatoDocumentosForm
    template_name = 'estagios/candidato_documentos_form.html'

    def test_func(self):
        return is_recrutamento(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # Se clicou em Salvar, popula os inlines com os dados enviados
            context['arquivos_formset'] = ArquivosFormSet(self.request.POST, self.request.FILES, instance=self.object)
            context['empresas_formset'] = EmpresasFormSet(self.request.POST, instance=self.object)
        else:
            # Se só abriu a página, gera inlines em branco (ou com dados existentes)
            context['arquivos_formset'] = ArquivosFormSet(instance=self.object)
            context['empresas_formset'] = EmpresasFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        arquivos_formset = context['arquivos_formset']
        empresas_formset = context['empresas_formset']

        # Só salva se TUDO estiver preenchido corretamente
        if arquivos_formset.is_valid() and empresas_formset.is_valid():
            self.object = form.save()
            arquivos_formset.instance = self.object
            arquivos_formset.save()
            empresas_formset.instance = self.object
            empresas_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('perfil_candidato', kwargs={'pk': self.object.pk})
