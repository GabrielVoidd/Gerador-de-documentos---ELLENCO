from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from estagios.models import ParteConcedente, Chamados, Aditivo, ContratoAceite, ContratoSocial
from .forms import ParteConcedenteForm, ContratoSocialForm, DetalhesAceiteFormSet, ContratoAceiteForm, ChamadoForm, \
    ChamadoUpdateForm, AditivoForm


class ComercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()


# 1. A tela de cadastro de nova empresa
class ParteConcedenteCreateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ParteConcedente
    form_class = ParteConcedenteForm
    template_name = 'comercial/parte_concedente_form.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def form_invalid(self, form):
        print("ERROS DO FORMULÁRIO:", form.errors)
        return super().form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        chamado_id = self.request.GET.get('chamado')  # Pega o ID da URL

        if chamado_id:
            chamado = get_object_or_404(Chamados, pk=chamado_id)
            # Mapeia os dados do Chamado para os campos da Parte Concedente
            initial['razao_social'] = chamado.nome_empresa
            initial['cnpj'] = chamado.cnpj
            initial['email'] = chamado.email
            initial['telefone'] = chamado.numero
            initial['representante_legal'] = chamado.nome

        return initial


def dashboard_comercial(request):
    query = request.GET.get('q')

    if query:
        clientes = ParteConcedente.objects.filter(Q(razao_social__icontains=query) | Q(cnpj__icontains=query)).order_by(
            '-id')
        chamados = Chamados.objects.filter(
            Q(nome_empresa__icontains=query) | Q(cnpj__icontains=query) | Q(nome__icontains=query)).order_by(
            '-data_contato')
    else:
        clientes = ParteConcedente.objects.all().order_by('-id')[:5]
        chamados = Chamados.objects.all().order_by('contrato_assinado', '-data_contato')[:8]

    # --- DADOS PARA O GRÁFICO DO FUNIL ---
    qtd_aguardando = Chamados.objects.filter(proposta_enviada=False, contrato_assinado=False).count()
    qtd_propostas = Chamados.objects.filter(proposta_enviada=True, contrato_assinado=False).count()
    qtd_assinados = Chamados.objects.filter(contrato_assinado=True).count()
    taxa_conversao = 0
    total_leads = Chamados.objects.count()
    if total_leads > 0:
        taxa_conversao = int((qtd_assinados / total_leads) * 100)

    context = {
        'ultimos_clientes': clientes,
        'chamados_pendentes': chamados,
        'total_clientes': ParteConcedente.objects.count(),
        'total_chamados': Chamados.objects.filter(contrato_assinado=False).count(),
        'query': query,

        # Variáveis do Gráfico
        'chart_aguardando': qtd_aguardando,
        'chart_propostas': qtd_propostas,
        'chart_assinados': qtd_assinados,
        'taxa_conversao': taxa_conversao,
    }
    return render(request, 'comercial/dashboard.html', context)


def perfil_empresa(request, pk):
    empresa = get_object_or_404(ParteConcedente, pk=pk)
    contratos_sociais = ContratoSocial.objects.filter(parte_concedente=empresa)

    # Adicionamos o .prefetch_related('detalhes') aqui:
    contratos_aceite = ContratoAceite.objects.filter(parte_concedente=empresa).prefetch_related('detalhes')

    aditivos = Aditivo.objects.filter(contrato_social__parte_concedente=empresa)

    context = {
        'empresa': empresa,
        'contratos_sociais': contratos_sociais,
        'contratos_aceite': contratos_aceite,
        'aditivos': aditivos,
    }
    return render(request, 'comercial/perfil_empresa.html', context)


class ContratoSocialCreateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ContratoSocial
    form_class = ContratoSocialForm
    template_name = 'comercial/contrato_social_form.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def form_valid(self, form):
        # Aqui está o pulo do gato: pegamos a empresa pelo ID da URL e salvamos no contrato
        empresa_id = self.kwargs.get('pk')
        form.instance.parte_concedente_id = empresa_id
        return super().form_valid(form)

    def get_success_url(self):
        # Após salvar, volta para o perfil da empresa
        return reverse_lazy('perfil_empresa', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = get_object_or_404(ParteConcedente, pk=self.kwargs.get('pk'))
        return context


class ContratoAceiteCreateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ContratoAceite
    form_class = ContratoAceiteForm
    template_name = 'comercial/contrato_aceite_form.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def get_initial(self):
        # Pré-preenche os campos com os dados da empresa cadastrada
        initial = super().get_initial()
        empresa = get_object_or_404(ParteConcedente, pk=self.kwargs.get('pk'))
        initial['empresa_nome_documento'] = empresa.razao_social or empresa.nome
        initial['empresa_cnpj_documento'] = empresa.cnpj
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = get_object_or_404(ParteConcedente, pk=self.kwargs.get('pk'))
        context['empresa'] = empresa
        if self.request.POST:
            context['vagas_formset'] = DetalhesAceiteFormSet(self.request.POST)
        else:
            context['vagas_formset'] = DetalhesAceiteFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        vagas_formset = context['vagas_formset']
        if vagas_formset.is_valid():
            form.instance.parte_concedente_id = self.kwargs.get('pk')
            self.object = form.save()
            vagas_formset.instance = self.object
            vagas_formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('perfil_empresa', kwargs={'pk': self.kwargs.get('pk')})


class ChamadoCreateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Chamados
    form_class = ChamadoForm
    template_name = 'comercial/chamado_form.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()


class ChamadoUpdateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Chamados
    form_class = ChamadoUpdateForm
    template_name = 'comercial/chamado_update.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()


class AditivoCreateView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Aditivo
    form_class = AditivoForm
    template_name = 'comercial/aditivo_form.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def form_valid(self, form):
        form.instance.parte_concedente_id = self.kwargs.get('pk')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('perfil_empresa', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = get_object_or_404(ParteConcedente, pk=self.kwargs.get('pk'))
        return context


class ChamadoListView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Chamados
    template_name = 'comercial/chamado_list.html'
    context_object_name = 'chamados'
    paginate_by = 15  # Mostra 15 por página

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def get_queryset(self):
        queryset = Chamados.objects.all().order_by('-data_contato')
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')

        if q:
            queryset = queryset.filter(Q(nome_empresa__icontains=q) | Q(cnpj__icontains=q) | Q(nome__icontains=q))

        if status == 'pendente':
            queryset = queryset.filter(contrato_assinado=False)
        elif status == 'assinado':
            queryset = queryset.filter(contrato_assinado=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        return context


class EmpresaListView(ComercialRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ParteConcedente
    template_name = 'comercial/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 15

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def get_queryset(self):
        queryset = ParteConcedente.objects.all().order_by('razao_social')
        q = self.request.GET.get('q')

        if q:
            queryset = queryset.filter(Q(razao_social__icontains=q) | Q(cnpj__icontains=q))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
