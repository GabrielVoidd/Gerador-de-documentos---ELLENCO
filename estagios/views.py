from datetime import date
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .forms import ContratoForm
import os
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato, \
    TipoEvento, Lancamento, Recibo, ReciboRescisao, LancamentoRescisao, ContratoSocial, Aditivo, ContratoAceite
from .serializers import (
    InstituicaoEnsinoSerializer, ParteConcedenteSerializer, EstagiarioSerializer, AgenteIntegradorSerializer,
    ContratoSerializer, ContratoCreateSerializer, RescisaoSerializer, RescisaoCreateSerializer, CandidatoSerializer,
    TipoEventoSerializer, LancamentoSerializer, ReciboSerializer, ReciboRescisaoSerializer,
    LancamentoRescisaoSerializer, ContratoSocialSerializer, Aditivo, AditivoSerializer, CriterioExclusao, \
    CriterioExclusaoSerializer, ContratoAceiteSerializer
)
from django.db import transaction
import openpyxl


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


class ContratoCreateView(SuccessMessageMixin, CreateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'estagios/contrato_form.html'
    success_url = reverse_lazy('contrato_lista') # Redireciona para a lista depois da criação
    success_message = 'Contrato criado com sucesso.'


class ContratoUpdateView(SuccessMessageMixin, UpdateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'estagios/contrato_form.html'
    success_url = reverse_lazy('contrato_lista')
    success_message = 'Contrato atualizado com sucesso.'


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

        agencia_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'agencia.png')
        agencia_path = 'file:///' + agencia_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do cadastro
        html_string = render_to_string('estagios/contrato_aceite.html',
                                       {'contrato_aceite': contrato_aceite, 'agencia_path': agencia_path})

        # Gera o PDF
        pdf_file = HTML(string=html_string).write_pdf()

        # Cria a resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="ContratoR&S_{contrato_aceite.parte_concedente.razao_social}.pdf"'

        return response
