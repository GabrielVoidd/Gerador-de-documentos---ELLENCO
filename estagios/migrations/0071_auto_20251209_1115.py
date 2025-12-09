from django.db import migrations


def separar_medicamentos(apps, schema_editor):
    # Pega o model histórico
    Candidato = apps.get_model('estagios', 'Candidato')

    for candidato in Candidato.objects.all():
        texto_antigo = candidato.medicamento_constante

        if not texto_antigo:
            candidato.usa_medicamento = 'N'
            candidato.nome_medicamento = ''
        else:
            texto_lower = texto_antigo.strip().lower()
            termos_negativos = ['não', 'nao', 'n', 'nenhum', 'nada', 'NAO', 'Nao', 'NÃO', 'Não']

            if texto_lower in termos_negativos:
                candidato.usa_medicamento = 'N'
                candidato.nome_medicamento = ''
            else:
                candidato.usa_medicamento = 'S'
                candidato.nome_medicamento = texto_antigo

        candidato.save()


class Migration(migrations.Migration):

    dependencies = [
        ('estagios', '0070_candidato_nome_medicamento_candidato_usa_medicamento_and_more'),
    ]

    operations = [
        migrations.RunPython(separar_medicamentos),
    ]
