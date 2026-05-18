from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .models import Chamado
from .forms import ChamadoForm

# 1. TELA DE CRIAÇÃO (Para todos os setores)
class ChamadoCreateView(LoginRequiredMixin, CreateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'chamados/novo_chamado.html'

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        messages.success(self.request, "Chamado aberto com sucesso! A TI irá analisar em breve.")
        return super().form_valid(form)

    def get_success_url(self):
        # Captura o setor atual da URL e passa adiante no redirecionamento
        return reverse('meus_chamados', kwargs={'setor': self.kwargs.get('setor', 'rs')})

# 2. TELA DO USUÁRIO (Setores acompanhando os próprios pedidos)
class MeusChamadosListView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = 'chamados/meus_chamados.html'
    context_object_name = 'chamados'

    def get_queryset(self):
        return Chamado.objects.filter(solicitante=self.request.user).order_by('-criado_em')

# 3. A TUA TELA (A Fila de Trabalho do Dev)
class FilaChamadosListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Chamado
    template_name = 'chamados/fila_trabalho.html'
    context_object_name = 'chamados_gerais'

    def test_func(self):
        # BLOQUEIO ABSOLUTO: Apenas o superuser pode aceder a esta view
        return self.request.user.is_superuser

    def get_queryset(self):
        return Chamado.objects.all().order_by('status', '-criado_em')