from django.contrib import admin
from .models import Chamado


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    # As colunas que vão aparecer na lista do Admin
    list_display = ('id', 'solicitante', 'tipo', 'status', 'urgencia', 'criado_em')

    # Filtros laterais para facilitar a sua vida
    list_filter = ('status', 'urgencia', 'tipo', 'criado_em')

    # Barra de pesquisa
    search_fields = ('solicitante__first_name', 'solicitante__username', 'descricao')

    # Impede que alguém edite a data de criação sem querer
    readonly_fields = ('criado_em', 'atualizado_em', 'concluido_em')