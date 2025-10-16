from PIL.ImageFilter import DETAIL
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
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato
from .serializers import(
InstituicaoEnsinoSerializer, ParteConcedenteSerializer, EstagiarioSerializer, AgenteIntegradorSerializer,
ContratoSerializer, ContratoCreateSerializer, RescisaoSerializer, RescisaoCreateSerializer, CandidatoSerializer
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
        contrato = self.get_object()

        logo_path_raw = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO.jpg')
        logo_path = 'file:///' + logo_path_raw.replace('\\', '/')

        # Renderiza o template HTML com o contexto do contrato
        html_string = render_to_string('estagios/termo_compromisso.html', {'contrato': contrato, 'logo_path': logo_path})

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
