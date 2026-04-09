from django.core.checks import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView
from adm.forms import ContratoForm, RescisaoForm, ReciboForm, CandidatoExpressoForm, LoteRecibosForm
from estagios.models import Contrato, Recibo, Rescisao, TipoEvento, Lancamento, Candidato, Estagiario


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

    # FILA DE CONTRATAÇÃO
    # Buscamos candidatos que:
    # 1. Estão marcados como aprovados (aprovado=True)
    # 2. NÃO estão marcados como 'trabalhando' (evita quem já foi efetivado)
    # 3. Excluímos apenas quem já possui um contrato ATIVO vinculado
    fila_contratacao = Candidato.objects.filter(
        aprovado=True,
        trabalhando=False
    ).exclude(
        estagiario__contrato__data_rescisao__isnull=True,
        estagiario__contrato__data_termino_prevista__gte=hoje
    ).select_related('instituicao_ensino').distinct()

    context = {
        'total_ativos': total_ativos,
        'vencendo_em_breve': vencendo_em_breve,
        'recibos_mes': recibos_mes,
        'rescisoes_mes': rescisoes_mes,
        'ultimos_contratos': ultimos_contratos,
        'contratos_alerta': contratos_alerta,
        'fila_contratacao': fila_contratacao,
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

    def get_initial(self):
        initial = super().get_initial()
        # Se vier um id na URL (?estagiario_id=X), a gente pré-seleciona no formulário
        estagiario_id = self.request.GET.get('estagiario_id')
        if estagiario_id:
            initial['estagiario'] = estagiario_id
        return initial


class RescisaoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Rescisao
    form_class = RescisaoForm
    template_name = 'adm/rescisao_form.html'
    success_url = reverse_lazy('adm_contratos_list')  # Volta para a lista de contratos

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrativo').exists()

    def form_valid(self, form):
        # 1. Salva a Rescisão no banco
        response = super().form_valid(form)

        # 2. Atualiza a data_rescisao diretamente no Contrato vinculado
        contrato = form.instance.contrato
        contrato.data_rescisao = form.instance.data_rescisao
        contrato.save(update_fields=['data_rescisao'])

        return response


class ReciboListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Recibo
    template_name = 'adm/recibo_list.html'
    context_object_name = 'recibos'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrativo').exists()

    def get_queryset(self):
        queryset = Recibo.objects.select_related(
            'contrato__estagiario__candidato', 'contrato__parte_concedente'
        ).order_by('-data_referencia', '-id')

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(estagiario_nome__icontains=q) |
                Q(parte_concedente_nome__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ReciboCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'adm/recibo_form.html'
    success_url = reverse_lazy('adm_recibos_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Administrativo').exists()

    def form_valid(self, form):
        # 1. Salva o Recibo e roda o cálculo automático do seu model (dias trabalhados, valor_liquido)
        response = super().form_valid(form)
        novo_recibo = self.object

        # 2. Cria o Lançamento padrão (Bolsa Auxílio) garantindo que o TipoEvento exista
        tipo_bolsa, created = TipoEvento.objects.get_or_create(
            descricao='Bolsa Auxílio',
            defaults={'tipo': 'CREDITO'}
        )

        Lancamento.objects.create(
            recibo=novo_recibo,
            tipo_evento=tipo_bolsa,
            valor=novo_recibo.valor
        )

        messages.success(self.request, "Recibo gerado com sucesso!")
        return response


@login_required
@user_passes_test(is_adm)
def converter_para_contrato(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)

    # 1. Cria o Estagiário (se ainda não existir) usando os dados do Candidato
    estagiario, created = Estagiario.objects.get_or_create(
        candidato=candidato,
        defaults={'instituicao_ensino': candidato.instituicao_ensino}
    )

    # 2. Redireciona para a tela de Novo Contrato que criamos antes
    # Passamos o ID do estagiário via URL para facilitar o preenchimento
    return redirect(f"{reverse('adm_contrato_novo')}?estagiario_id={estagiario.id}")


def cadastro_expresso(request):
    if request.method == 'POST':
        form = CandidatoExpressoForm(request.POST, request.FILES)
        if form.is_valid():
            candidato = form.save(commit=False)

            # --- Injeção de Dados Obrigatórios (Via Rápida) ---
            candidato.area_interesse = "REPASSE / INDICAÇÃO"
            candidato.conheceu_agencia = "Indicação da Empresa"
            candidato.microsoft_365 = 'SC'
            candidato.trabalho = 'N'
            candidato.habilitacao = 'NP'
            candidato.vale_transporte = 'NT'

            # Forçar aprovação para cair direto na fila do ADM
            candidato.aprovado = True
            candidato.observacoes = "Candidato de Repasse - Aguardando TCE."

            # Tratamento do CPF nulo (a correção que discutimos)
            if not candidato.cpf:
                candidato.cpf = None

            candidato.save()
            return render(request, 'adm/sucesso_cadastro.html')
    else:
        form = CandidatoExpressoForm()

    return render(request, 'adm/cadastro_expresso.html', {'form': form})


@login_required
@user_passes_test(is_adm)
def gerar_recibos_lote(request):
    if request.method == 'POST':
        form = LoteRecibosForm(request.POST)
        if form.is_valid():
            empresa = form.cleaned_data['parte_concedente']
            data_ref = form.cleaned_data['data_referencia']
            faltas = form.cleaned_data['dias_falta_padrao']

            # Busca contratos ativos dessa empresa
            contratos = Contrato.objects.filter(
                parte_concedente=empresa,
                data_rescisao__isnull=True,
                data_termino_prevista__gte=data_ref
            )

            recibos_criados = 0
            with transaction.atomic():
                for contrato in contratos:
                    # Evita duplicados no mesmo mês
                    if not Recibo.objects.filter(contrato=contrato, data_referencia=data_ref).exists():
                        # O save() do Recibo já vai usar a lógica proporcional que corrigimos!
                        novo_recibo = Recibo.objects.create(
                            contrato=contrato,
                            data_referencia=data_ref,
                            dias_falta=faltas
                        )

                        # Cria o lançamento de Bolsa Auxílio
                        tipo_bolsa, _ = TipoEvento.objects.get_or_create(descricao='Bolsa Auxílio',
                                                                         defaults={'tipo': 'CREDITO'})
                        Lancamento.objects.create(recibo=novo_recibo, tipo_evento=tipo_bolsa, valor=novo_recibo.valor)
                        recibos_criados += 1

            messages.success(request, f"Processamento concluído! {recibos_criados} recibos gerados.")
            return redirect('adm_recibos_list')
    else:
        form = LoteRecibosForm()

    return render(request, 'adm/lote_recibos_form.html', {'form': form})
