from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from estagios.models import ParteConcedente, Chamados, Aditivo, ContratoAceite, ContratoSocial
from .forms import ParteConcedenteForm, ContratoSocialForm, DetalhesAceiteFormSet, ContratoAceiteForm, ChamadoForm, \
    ChamadoUpdateForm


# 1. A tela de cadastro de nova empresa
class ParteConcedenteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ParteConcedente
    form_class = ParteConcedenteForm
    template_name = 'comercial/parte_concedente_form.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()

    def form_invalid(self, form):
        print("ERROS DO FORMULÁRIO:", form.errors)
        return super().form_invalid(form)


def dashboard_comercial(request):
    query = request.GET.get('q')

    if query:
        # Se houver pesquisa, traz todos os resultados correspondentes
        clientes = ParteConcedente.objects.filter(
            Q(razao_social__icontains=query) | Q(cnpj__icontains=query)
        ).order_by('-id')
    else:
        # Se não houver pesquisa, mantém os últimos 5 para o dashboard ficar organizado
        clientes = ParteConcedente.objects.all().order_by('-id')[:5]

    chamados_pendentes = Chamados.objects.filter(contrato_assinado=False).order_by('-data_contato')

    context = {
        'ultimos_clientes': clientes,
        'chamados_pendentes': chamados_pendentes,
        'total_clientes': ParteConcedente.objects.count(),
        'total_chamados': chamados_pendentes.count(),
        'query': query,
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


class ContratoSocialCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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


class ContratoAceiteCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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


class ChamadoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Chamados
    form_class = ChamadoForm
    template_name = 'comercial/chamado_form.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()


class ChamadoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Chamados
    form_class = ChamadoUpdateForm
    template_name = 'comercial/chamado_update.html'
    success_url = reverse_lazy('dashboard_comercial')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Comercial').exists()
