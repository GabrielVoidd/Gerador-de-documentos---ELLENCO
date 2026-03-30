from django import forms
from .models import Candidato

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