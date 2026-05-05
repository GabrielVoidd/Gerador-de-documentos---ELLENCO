from django import forms
from django.forms.models import inlineformset_factory

from .models import Candidato, Vaga, ParteConcedente, Candidatura, Empresa, Arquivos


class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        exclude =  [
            'observacoes', 'restrito', 'stand_by', 'trabalhando', 'em_processo', 'aprovado', 'reprovado',
            'nao_compareceu', 'desistiu', 'encaminhado', 'criterio_exclusao'
        ]

    def __init__(self, *args, **kwargs):
        super(CandidatoForm, self).__init__(*args, **kwargs)
        # Injeta a classe do Bootstrap em todos os campos gerados
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

        if 'data_nascimento' in self.fields:
            self.fields['data_nascimento'].widget.input_type = 'text'
            self.fields['data_nascimento'].widget.attrs['placeholder'] = 'DD/MM/AAAA'

        if 'celular' in self.fields:
            self.fields['celular'].widget.attrs.update({
                'placeholder': 'Como deve ser preenchido: 11912345678'
            })

        if 'celular2' in self.fields:
            self.fields['celular2'].widget.attrs.update({
                'placeholder': 'Esse número deve ser diferente do primeiro celular'
            })

    class Media:
        js = ('js/admin_custom.js', 'js/jquery.mask.min.js', 'js/mascaras_admin.js', 'js/mascara_cpf_admin.js',
              'js/mascara_rg_admin.js', 'js/viacep_admin.js', 'js/mascara_nascimento.js')


class CandidatoStatusForm(forms.ModelForm):
    class Meta:
        model = Candidato
        # Apenas os campos gerenciais que o R&S usa!
        fields = [
            'observacoes', 'restrito', 'stand_by', 'trabalhando',
            'em_processo', 'aprovado', 'reprovado', 'nao_compareceu',
            'desistiu', 'encaminhado'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                                 'placeholder': 'Anotações da entrevista, perfil do candidato...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica o estilo do Bootstrap em todos os checkboxes dinamicamente
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'


class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        # Removemos o status e datas, o Django preenche sozinho!
        fields = [
            'empresa', 'titulo', 'descricao', 'requisitos',
            'tipo_vaga', 'quantidade_vagas', 'salario_bolsa',
            'beneficios', 'horario', 'local_trabalho', 'observacoes', 'sexo'
        ]

        # Colocando as classes do Bootstrap para ficar bonito
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Estagiário de Marketing'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requisitos': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Cursando 2º semestre...'}),
            'tipo_vaga': forms.Select(attrs={'class': 'form-select'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_vagas': forms.NumberInput(attrs={'class': 'form-control'}),
            'salario_bolsa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'beneficios': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'horario': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: Segunda a Sexta, 09h às 16h'}),
            'local_trabalho': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: Híbrido - Centro, Guarulhos'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class VagaEditForm(VagaForm):
    class Meta(VagaForm.Meta):
        # Pega todos os campos antigos e soma o campo 'status'
        fields = VagaForm.Meta.fields + ['status']

        # Copia o visual dos campos antigos
        widgets = VagaForm.Meta.widgets

        # Adiciona o visual para o dropdown de status com destaque
        widgets['status'] = forms.Select(attrs={'class': 'form-select border-warning fw-bold'})


class ParteConcedenteForm(forms.ModelForm):
    class Meta:
        model = ParteConcedente
        fields = [
            'cnpj', 'razao_social', 'nome', 'ramo_atividade',
            'cep', 'endereco', 'bairro', 'cidade', 'estado',
            'telefone', 'email', 'representante_legal', 'local_trabalho'
        ]

        widgets = {
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia (Opcional)'}),
            'ramo_atividade': forms.TextInput(attrs={'class': 'form-control'}),

            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SP'}),
            'local_trabalho': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Se diferente do endereço (Opcional)'}),

            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 90000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rh@empresa.com.br'}),
            'representante_legal': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nome de quem assina os contratos'}),
        }


class CandidaturaForm(forms.ModelForm):
    class Meta:
        model = Candidatura
        fields = ['vaga', 'status']
        widgets = {
            'vaga': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O PULO DO GATO: Filtra o campo para mostrar APENAS vagas Abertas ('A')
        self.fields['vaga'].queryset = Vaga.objects.filter(status='A').order_by('-data_abertura')


class CandidaturaPorVagaForm(forms.ModelForm):
    class Meta:
        model = Candidatura
        fields = ['candidato', 'status']  # Pede o candidato, ignora a vaga

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona as classes do Bootstrap para ficar bonito
        self.fields['candidato'].widget.attrs.update({'class': 'form-select select2-candidato'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})


class CandidaturaUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidatura
        # Tira o campo 'vaga', deixa só o 'status' para edição
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select border-warning fw-bold'}),
        }


# 1. O formulário principal (que salva os 6 documentos fixos do Candidato)
class CandidatoDocumentosForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = [
            'anexar_curriculo', 'anexar_rg', 'anexar_cpf',
            'anexar_carteira_trabalho', 'anexar_declaracao', 'anexar_reservista'
        ]
        widgets = {
            'anexar_curriculo': forms.FileInput(attrs={'class': 'form-control'}),
            'anexar_rg': forms.FileInput(attrs={'class': 'form-control'}),
            'anexar_cpf': forms.FileInput(attrs={'class': 'form-control'}),
            'anexar_carteira_trabalho': forms.FileInput(attrs={'class': 'form-control'}),
            'anexar_declaracao': forms.FileInput(attrs={'class': 'form-control'}),
            'anexar_reservista': forms.FileInput(attrs={'class': 'form-control'}),
        }


# 2. O "Inline" das Folhas de Entrevista (Tabela: Arquivos)
# Ele liga o "Candidato" (Pai) com os "Arquivos" (Filho)
ArquivosFormSet = inlineformset_factory(
    Candidato,   # Modelo Pai
    Arquivos,    # Modelo Filho
    fields=['arquivo'],
    extra=1,     # Cria 1 linha vazia por padrão na tela
    can_delete=True,
    widgets={
        'arquivo': forms.FileInput(attrs={'class': 'form-control form-control-sm'})
    }
)


# 3. O "Inline" do Histórico de Empresas (Tabela: Empresa)
# Ele liga o "Candidato" (Pai) com as "Empresas" (Filho)
EmpresasFormSet = inlineformset_factory(
    Candidato,   # Modelo Pai
    Empresa,     # Modelo Filho
    fields=['nome', 'observacoes', 'arquivo'],
    extra=1,     # Cria 1 linha vazia por padrão na tela
    can_delete=True,
    widgets={
        'nome': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nome da Empresa'}),
        'observacoes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 1, 'placeholder': 'Observações da entrevista...'}),
        'arquivo': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
    }
)
