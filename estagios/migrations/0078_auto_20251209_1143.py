from django.db import migrations


def separar_problema_saude(apps, schema_editor):
    # Pega o model histórico
    Candidato = apps.get_model('estagios', 'Candidato')

    for candidato in Candidato.objects.all():
        texto_antigo = candidato.problema_saude

        if not texto_antigo:
            candidato.tem_problema_saude = 'N'
            candidato.nome_problema_saude = ''
        else:
            texto_lower = texto_antigo.strip().lower()
            termos_negativos = ['não', 'nao', 'n', 'nenhum', 'nada', 'NAO', 'Nao', 'NÃO', 'Não']

            if texto_lower in termos_negativos:
                candidato.tem_problema_saude = 'N'
                candidato.nome_problema_saude = ''
            else:
                candidato.tem_problema_saude = 'S'
                candidato.nome_problema_saude = texto_antigo

        candidato.save()


class Migration(migrations.Migration):

    dependencies = [
        ('estagios', '0077_candidato_nome_problema_saude_and_more'),
    ]

    operations = [
        migrations.RunPython(separar_problema_saude),
    ]
