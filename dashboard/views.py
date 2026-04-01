from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import date, timedelta
import json
from django.utils import timezone
from estagios.models import Candidato, Chamados, Vaga, Candidatura


@login_required
def dashboard(request):
    hoje = timezone.now().date()
    trinta_dias_atras = hoje - timedelta(days=30)

    # --- 1. KPIs (Cartões Menores) ---
    kpis = {
        'minhas_vagas': Vaga.objects.filter(status='A').count(),
        'novas_candidaturas': Candidatura.objects.filter(data_candidatura__gte=trinta_dias_atras).count(),
        'meus_convocados': Candidato.objects.filter(encaminhado=True).count(),
        'minhas_mensagens': Chamados.objects.filter(proposta_enviada=False).count(),
    }

    # --- CAPTURAR OS FILTROS INDEPENDENTES ---
    try:
        dias_vagas = int(request.GET.get('dias_vagas', 15))
    except ValueError:
        dias_vagas = 15

    try:
        dias_candidatos = int(request.GET.get('dias_candidatos', 15))
    except ValueError:
        dias_candidatos = 15

    data_limite_vagas = hoje - timedelta(days=dias_vagas)
    data_limite_candidatos = hoje - timedelta(days=dias_candidatos)

    # --- 2. GRÁFICO DE BARRAS (Vagas - Agora com Filtro!) ---
    grafico_vagas_dados = {
        'labels': ['Aberta', 'Cancelada', 'Fechada', 'Reaberta', 'Suspensa'],
        'vagas': [
            Vaga.objects.filter(status='A', data_abertura__gte=data_limite_vagas).count(),
            Vaga.objects.filter(status='C', data_abertura__gte=data_limite_vagas).count(),
            Vaga.objects.filter(status='F', data_abertura__gte=data_limite_vagas).count(),
            Vaga.objects.filter(status='R', data_abertura__gte=data_limite_vagas).count(),
            Vaga.objects.filter(status='S', data_abertura__gte=data_limite_vagas).count(),
        ]
    }

    # --- 3. GRÁFICO DE LINHAS (Candidatos vs Candidaturas) ---
    candidatos_recentes = Candidato.objects.filter(data_cadastro__gte=data_limite_candidatos)
    candidaturas_recentes = Candidatura.objects.filter(data_candidatura__gte=data_limite_candidatos)

    candidatos_dict = {}
    for c in candidatos_recentes:
        if c.data_cadastro:
            candidatos_dict[c.data_cadastro] = candidatos_dict.get(c.data_cadastro, 0) + 1

    candidaturas_dict = {}
    for c in candidaturas_recentes:
        if c.data_candidatura:
            dia = c.data_candidatura.date()
            candidaturas_dict[dia] = candidaturas_dict.get(dia, 0) + 1

    dias_labels = []
    candidatos_linha = []
    candidaturas_linha = []

    for i in range(dias_candidatos, -1, -1):
        dia_atual = hoje - timedelta(days=i)
        dias_labels.append(dia_atual.strftime('%d/%m'))
        candidatos_linha.append(candidatos_dict.get(dia_atual, 0))
        candidaturas_linha.append(candidaturas_dict.get(dia_atual, 0))

    grafico_candidatos_dados = {
        'labels': dias_labels,
        'novos_candidatos': candidatos_linha,
        'candidaturas': candidaturas_linha
    }

    context = {
        'kpis': kpis,
        'grafico_vagas_dados_json': json.dumps(grafico_vagas_dados),
        'grafico_candidatos_dados_json': json.dumps(grafico_candidatos_dados),
        # Passando de volta para o HTML para manter o <select> marcado na opção certa
        'dias_vagas': dias_vagas,
        'dias_candidatos': dias_candidatos,
    }

    return render(request, 'dashboard/dashboard.html', context)
