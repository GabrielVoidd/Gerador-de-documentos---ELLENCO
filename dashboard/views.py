import openpyxl
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from datetime import date, timedelta
import json
from estagios.models import Candidato, Chamados, Vaga, Candidatura


def dashboard(request):
    hoje = date.today()
    trinta_dias_atras = hoje - timedelta(days=30)
    quinze_dias_atras = hoje - timedelta(days=15)

    # --- 1. KPIs (Cartões Menores) ---
    kpis = {
        'minhas_vagas': Vaga.objects.filter(status='A').count(),  # Vagas Abertas
        'novas_candidaturas': Candidatura.objects.filter(data_candidatura__gte=trinta_dias_atras).count(),
        'meus_convocados': Candidato.objects.filter(encaminhado=True).count(),
        # Regra de negócio 1 pra 1
        'minhas_mensagens': Chamados.objects.filter(proposta_enviada=False).count(),
    }

    # --- 2. GRÁFICO DE BARRAS (Status das Vagas) ---
    grafico_vagas_dados = {
        'labels': ['Aberta', 'Cancelada', 'Fechada', 'Reaberta', 'Suspensa'],
        'vagas': [
            Vaga.objects.filter(status='A').count(),
            Vaga.objects.filter(status='C').count(),
            Vaga.objects.filter(status='F').count(),
            Vaga.objects.filter(status='R').count(),
            Vaga.objects.filter(status='S').count(),
        ]
    }

    # --- 3. GRÁFICO DE LINHAS (Candidatos vs Candidaturas - 15 dias) ---
    # Agrupa Novos Candidatos (pelo campo DateField data_cadastro)
    # --- 3. GRÁFICO DE LINHAS (Candidatos vs Candidaturas - 15 dias) ---

    # Em vez de forçar o SQLite a agrupar, puxamos os registros brutos recentes
    candidatos_recentes = Candidato.objects.filter(data_cadastro__gte=quinze_dias_atras)
    candidaturas_recentes = Candidatura.objects.filter(data_candidatura__gte=quinze_dias_atras)

    # Agrupamos os Candidatos no Python (Seguro contra erros do SQLite)
    candidatos_dict = {}
    for c in candidatos_recentes:
        if c.data_cadastro:
            candidatos_dict[c.data_cadastro] = candidatos_dict.get(c.data_cadastro, 0) + 1

    # Agrupamos as Candidaturas no Python
    candidaturas_dict = {}
    for c in candidaturas_recentes:
        if c.data_candidatura:
            dia = c.data_candidatura.date()  # Extrai só o dia do DateTime
            candidaturas_dict[dia] = candidaturas_dict.get(dia, 0) + 1

    # Prepara as listas para o eixo X e Y do Chart.js
    dias_labels = []
    candidatos_linha = []
    candidaturas_linha = []

    for i in range(15, -1, -1):
        dia_atual = hoje - timedelta(days=i)
        dias_labels.append(dia_atual.strftime('%d/%m'))  # Ex: 31/03

        # Pega o total do dia no dicionário, se não tiver, coloca 0
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
    }

    return render(request, 'dashboard/dashboard.html', context)
