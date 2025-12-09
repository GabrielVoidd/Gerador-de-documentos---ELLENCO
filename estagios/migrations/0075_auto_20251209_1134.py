from django.db import migrations


def separar_alergias(apps, schema_editor):
    # Pega o model histórico
    Candidato = apps.get_model('estagios', 'Candidato')

    for candidato in Candidato.objects.all():
        texto_antigo = candidato.alergia

        if not texto_antigo:
            candidato.tem_alergia = 'N'
            candidato.nome_alergia = ''
        else:
            texto_lower = texto_antigo.strip().lower()
            termos_negativos = ['não', 'nao', 'n', 'nenhum', 'nada', 'NAO', 'Nao', 'NÃO', 'Não']

            if texto_lower in termos_negativos:
                candidato.tem_alergia = 'N'
                candidato.nome_alergia = ''
            else:
                candidato.tem_alergia = 'S'
                candidato.nome_alergia = texto_antigo

        candidato.save()


class Migration(migrations.Migration):

    dependencies = [
        ('estagios', '0074_candidato_nome_alergia_candidato_tem_alergia'),
    ]

    operations = [
        migrations.RunPython(separar_alergias),
    ]
