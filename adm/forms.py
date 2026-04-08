from django import forms
from estagios.models import Contrato


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = [
            'estagiario', 'parte_concedente', 'agente_integrador',
            'data_inicio', 'data_termino_prevista', 'valor_bolsa',
            'setor', 'supervisor_nome', 'numero_apolice_seguro',
            'jornada_estagio', 'atividades'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_termino_prevista': forms.DateInput(attrs={'type': 'date'}),
            'jornada_estagio': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Ex: Segunda a Sexta, das 09h às 15h, com 1h de intervalo'}),
            'atividades': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Descreva as atividades que o estagiário irá realizar...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Opcional: Adicionando classes específicas para os selects com pesquisa (Select2), se você usar no futuro
        self.fields['estagiario'].widget.attrs['class'] = 'form-select'
        self.fields['parte_concedente'].widget.attrs['class'] = 'form-select'
        self.fields['agente_integrador'].widget.attrs['class'] = 'form-select'