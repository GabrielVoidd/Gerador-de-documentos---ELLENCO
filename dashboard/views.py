from django.shortcuts import render
import json
from estagios.models import Candidato


def dashboard(request):
    """View para renderizar o dashboard com dados simulados."""

    # Dados simulados para os KPIs menores (Minhas Vagas, Novas Candidaturas, etc.)
    total_candidatos = Candidato.objects.count()
    kpis = {
        'minhas_vagas': 0,
        'novas_candidaturas': total_candidatos,
        'meus_convocados': 0,
        'minhas_mensagens': 0,
    }

    # Dados simulados para o gráfico de barras (Vagas)
    grafico_vagas_dados = {
        'labels': ['Aberto', 'Cancelado', 'Fechado', 'Reaberta', 'Suspensa'],
        'vagas': [310, 0, 90, 0, 0]  # Números aproximados da imagem
    }

    # Dados simulados para o gráfico de linhas (Candidatos / Candidaturas)
    grafico_candidatos_dados = {
        'labels': ['Mai 6', 'Mai 7', 'Mai 8', 'Mai 9', 'Mai 10', 'Mai 11', 'Mai 12', 'Mai 13', 'Mai 14', 'Mai 15',
                   'Mai 16', 'Mai 17', 'Mai 18', 'Mai 19', 'Mai 20', 'Mai 21'],
        'novos_candidatos': [150, 100, 200, 150, 250, 180, 280, 200, 180, 120, 180, 150, 220, 200, 180, 160],
        # Aproximações
        'candidaturas': [350, 300, 450, 380, 680, 580, 620, 500, 480, 380, 500, 450, 600, 580, 500, 420]  # Aproximações
    }

    # Transforma os dados em JSON para passar para o template de forma segura
    context = {
        'notificacoes_ativas': True,  # Exemplo de estado para o sino
        'kpis': kpis,
        'grafico_vagas_dados_json': json.dumps(grafico_vagas_dados),
        'grafico_candidatos_dados_json': json.dumps(grafico_candidatos_dados),
    }

    return render(request, 'dashboard/dashboard.html', context)