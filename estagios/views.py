from datetime import date
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
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
    TipoEvento, Lancamento, Recibo
from .serializers import(
InstituicaoEnsinoSerializer, ParteConcedenteSerializer, EstagiarioSerializer, AgenteIntegradorSerializer,
ContratoSerializer, ContratoCreateSerializer, RescisaoSerializer, RescisaoCreateSerializer, CandidatoSerializer,
TipoEventoSerializer, LancamentoSerializer, ReciboSerializer
)

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

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do contrato
        html_string = render_to_string('estagios/termo_compromisso.html', {'contrato': contrato, 'logo_path': logo_path, 'usuario_logado': usuario_que_gerou})

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

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        html_string = render_to_string('estagios/termo_rescisao.html', {'rescisao': rescisao, 'logo_path': logo_path})
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Rescisao_{rescisao.contrato.estagiario.nome}.pdf"'

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
