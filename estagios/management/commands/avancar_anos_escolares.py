from django.core.management.base import BaseCommand
from estagios.models import Candidato


class Command(BaseCommand):
    help = 'Avança automaticamente o ano/semestre dos candidatos que não estejam com a opção de Ensino Médio Concluído selecionada'

    def handle(self, *args, **kwargs):
        candidatos = Candidato.objects.filter(escolaridade__in=[
            Candidato.Escolaridades.ENSINO_MEDIO,
            Candidato.Escolaridades.ENSINO_MEDIO_INCOMPLETO,
            Candidato.Escolaridades.ENSINO_MEDIO_TECNICO
        ])

        atualizados_para_segundo = 0
        atualizados_para_terceiro = 0
        concluidos = 0

        for candidato in candidatos:
            if candidato.ano_semestre == Candidato.AnosSemestres.PRIMEIRO_ANO:
                candidato.ano_semestre = Candidato.AnosSemestres.SEGUNDO_ANO
                candidato.save(update_fields=['ano_semestre'])
                atualizados_para_segundo += 1

            elif candidato.ano_semestre == Candidato.AnosSemestres.SEGUNDO_ANO:
                candidato.ano_semestre = Candidato.AnosSemestres.TERCEIRO_ANO
                candidato.save(update_fields=['ano_semestre'])
                atualizados_para_segundo += 1

            elif candidato.ano_semestre in [Candidato.AnosSemestres.TERCEIRO_ANO, Candidato.AnosSemestres.QUARTO_ANO]:
                candidato.escolaridade = Candidato.Escolaridades.ENSINO_MEDIO_COMPLETO
                candidato.ano_semestre = None
                candidato.save(update_fields=['escolaridade', 'ano_semestre'])
                concluidos += 1

        self.stdout.write(self.style.SUCCESS('Rotina de atualização concluída com sucesso!'))
        self.stdout.write(f'- Promovidos para o 2º Ano: {atualizados_para_segundo}')
        self.stdout.write(f'- Promovidos para o 3º Ano: {atualizados_para_terceiro}')
        self.stdout.write(f'- Concluíram o Ensino Médio: {concluidos}')
