from django import forms
from .models import Candidato, Vaga


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

    class Media:
        js = ('js/admin_custom.js', 'js/jquery.mask.min.js', 'js/mascaras_admin.js', 'js/mascara_cpf_admin.js',
              'js/mascara_rg_admin.js', 'js/viacep_admin.js')


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
            'beneficios', 'horario', 'local_trabalho'
        ]

        # Colocando as classes do Bootstrap para ficar bonito
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Estagiário de Marketing'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requisitos': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Cursando 2º semestre...'}),
            'tipo_vaga': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_vagas': forms.NumberInput(attrs={'class': 'form-control'}),
            'salario_bolsa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'beneficios': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'horario': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: Segunda a Sexta, 09h às 16h'}),
            'local_trabalho': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: Híbrido - Centro, Guarulhos'}),
        }
