from django import forms
from .models import Chamado


class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['tipo', 'descricao', 'justificativa']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select-form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva '
                                                           'detalhadamente o que você precisa ou qual erro aconteceu'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Explique por que isso é importante para o andamento do seu setor'}),
        }
