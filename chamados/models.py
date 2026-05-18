from django.db import models
from django.contrib.auth.models import User


class Chamado(models.Model):
    # Opções de escolha
    class TipoChamado(models.TextChoices):
        ERRO = 'ERRO', 'Erro / Sistema fora do ar'
        DUVIDA = 'DUVIDA', 'Dúvida de Uso'
        MELHORIA = 'MELHORIA', 'Nova Funcionalidade / Melhoria'

    class Urgencia(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa (Quando der tempo)'
        MEDIA = 'MEDIA', 'Média (No fluxo normal)'
        ALTA = 'ALTA', 'Alta (Prioridade da semana)'
        CRITICA = 'CRITICA', 'Crítica (Pare tudo e resolva)'

    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto (Aguardando Dev)'
        AGENDADO = 'AGENDADO', 'Agendado'
        ANDAMENTO = 'ANDAMENTO', 'Em Andamento'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        CANCELADO = 'CANCELADO', 'Cancelado'

    # Dados do solicitante
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='chamados abertos')
    tipo = models.CharField(max_length=20, choices=TipoChamado.choices, default=TipoChamado.DUVIDA)
    descricao = models.TextField(verbose_name='O que precisa ser feito?')
    justificativa = models.TextField(verbose_name='Por que isso é necessário?')

    # Controle do desenvolvedor
    urgencia = models.CharField(max_length=10, choices=Urgencia.choices, blank=True, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ABERTO)
    data_agendada = models.DateTimeField(blank=True, null=True, verbose_name='Dia e hora para execução')
    resposta_dev = models.TextField(blank=True, null=True, verbose_name='Sua resposta para o setor')

    # Data automáticas
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    concluido_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Chamado {self.id} - {self.solicitante.first_name} ({self.get_status_display()})'
