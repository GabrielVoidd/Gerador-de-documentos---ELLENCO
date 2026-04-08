from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView

from adm.forms import ContratoForm
# Ajuste os imports dos models conforme o seu projeto
from estagios.models import Contrato, Recibo, Rescisao

# Função de segurança (ajuste o nome do grupo conforme seu sistema)
def is_adm(user):
    return user.is_superuser or user.groups.filter(name='RH').exists()

@login_required
@user_passes_test(is_adm)
def dashboard_adm(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    daqui_30_dias = hoje + timedelta(days=30)

    # --- KPIs (Indicadores Rápidos) ---
    # Contratos ativos: sem data de rescisão e com término no futuro
    total_ativos = Contrato.objects.filter(
        data_rescisao__isnull=True,
        data_termino_prevista__gte=hoje
    ).count()

    # Contratos que vencem em até 30 dias (Radar de Renovação)
    vencendo_em_breve = Contrato.objects.filter(
        data_rescisao__isnull=True,
        data_termino_prevista__range=[hoje, daqui_30_dias]
    ).count()

    # Movimentações do Mês
    recibos_mes = Recibo.objects.filter(data_referencia__gte=inicio_mes).count()
    rescisoes_mes = Rescisao.objects.filter(data_rescisao__gte=inicio_mes).count()

    # --- Tabelas do Dashboard ---
    # Últimos contratos para ter histórico recente na tela
    ultimos_contratos = Contrato.objects.select_related(
        'estagiario__candidato', 'parte_concedente'
    ).order_by('-data_criacao', '-id')[:6]

    # Contratos em Alerta (vencem em até 15 dias ou já passaram e ninguém rescindiu)
    limite_alerta = hoje + timedelta(days=15)
    contratos_alerta = Contrato.objects.filter(
        data_rescisao__isnull=True,
        data_termino_prevista__lte=limite_alerta
    ).select_related('estagiario__candidato', 'parte_concedente').order_by('data_termino_prevista')[:6]

    context = {
        'total_ativos': total_ativos,
        'vencendo_em_breve': vencendo_em_breve,
        'recibos_mes': recibos_mes,
        'rescisoes_mes': rescisoes_mes,
        'ultimos_contratos': ultimos_contratos,
        'contratos_alerta': contratos_alerta,
    }

    return render(request, 'adm/dashboard.html', context)


class ContratoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Contrato
    template_name = 'adm/contrato_list.html'
    context_object_name = 'contratos'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrativo').exists()

    def get_queryset(self):
        queryset = Contrato.objects.select_related(
            'estagiario__candidato', 'parte_concedente'
        ).order_by('-data_criacao', '-id')

        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        hoje = timezone.now().date()

        if q:
            queryset = queryset.filter(
                Q(numero_contrato__icontains=q) |
                Q(estagiario__candidato__nome__icontains=q) |
                Q(parte_concedente__razao_social__icontains=q)
            )

        if status == 'ativos':
            queryset = queryset.filter(data_rescisao__isnull=True, data_termino_prevista__gte=hoje)
        elif status == 'rescindidos':
            queryset = queryset.filter(data_rescisao__isnull=False)
        elif status == 'vencidos':
            queryset = queryset.filter(data_rescisao__isnull=True, data_termino_prevista__lt=hoje)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['status'] = self.request.GET.get('status', '')
        return context


class ContratoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'adm/contrato_form.html'
    success_url = reverse_lazy('adm_contratos_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrativo').exists()
