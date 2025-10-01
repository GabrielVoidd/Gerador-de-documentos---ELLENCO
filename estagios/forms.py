from django import forms
from .models import Contrato, Rescisao


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = '__all__'

        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_termino_prevista': forms.DateInput(attrs={'type': 'date'}),
        }
