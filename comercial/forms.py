from django.forms.models import inlineformset_factory

from estagios.models import ParteConcedente, ContratoSocial, ContratoAceite, DetalhesContratoAceite
from django import forms


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

            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11912345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rh@empresa.com.br'}),
            'representante_legal': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nome de quem assina os contratos'}),
        }


class ContratoSocialForm(forms.ModelForm):
    class Meta:
        model = ContratoSocial
        # Excluímos 'parte_concedente' porque vamos passar via View
        exclude = ['parte_concedente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ContratoAceiteForm(forms.ModelForm):
    class Meta:
        model = ContratoAceite
        fields = ['plano', 'taxa_honorarios', 'empresa_nome_documento', 'empresa_cnpj_documento', 'observacoes_adicionais']
        widgets = {
            'plano': forms.Select(attrs={'class': 'form-select'}),
            'taxa_honorarios': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 40% (quarenta por cento)'}),
            'empresa_nome_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa_cnpj_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes_adicionais': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# Fábrica para as Vagas do Aceite
DetalhesAceiteFormSet = inlineformset_factory(
    ContratoAceite, DetalhesContratoAceite,
    fields=['quantidade', 'vaga', 'salario'],
    extra=1, # Começa com uma linha de vaga vazia
    can_delete=True,
    widgets={
        'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        'vaga': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Estagiário de ADM'}),
        'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    }
)
