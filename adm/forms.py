from django import forms
from django.shortcuts import render

from estagios.models import Contrato, Rescisao, Recibo, Candidato, ParteConcedente


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


class RescisaoForm(forms.ModelForm):
    class Meta:
        model = Rescisao
        fields = ['contrato', 'data_rescisao', 'motivo']
        widgets = {
            'data_rescisao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['contrato'].widget.attrs['class'] = 'form-select'
        self.fields['motivo'].widget.attrs['class'] = 'form-select'

        # REGRA DE OURO: Só mostra no dropdown contratos que ainda estão ativos!
        self.fields['contrato'].queryset = Contrato.objects.filter(
            data_rescisao__isnull=True
        ).select_related('estagiario__candidato', 'parte_concedente')


class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = ['contrato', 'data_referencia', 'dias_falta']
        widgets = {
            'data_referencia': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['contrato'].widget.attrs['class'] = 'form-select'

        # Filtra apenas contratos ativos
        self.fields['contrato'].queryset = Contrato.objects.filter(
            data_rescisao__isnull=True
        ).select_related('estagiario__candidato', 'parte_concedente')


class CandidatoExpressoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = [
            'nome', 'cpf', 'rg', 'data_nascimento', 'sexo', 'estado_civil',
            'celular', 'email', 'cep', 'endereco', 'numero', 'bairro', 'cidade', 'estado',
            'instituicao_ensino', 'escolaridade', 'periodo', 'ano_semestre', 'serie_semestre'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoteRecibosForm(forms.Form):
    parte_concedente = forms.ModelChoiceField(
        queryset=ParteConcedente.objects.all(),
        label="Selecione a Empresa",
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )
    data_referencia = forms.DateField(
        label="Mês de Referência",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    dias_falta_padrao = forms.IntegerField(
        initial=0,
        label="Faltas (para todos)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
