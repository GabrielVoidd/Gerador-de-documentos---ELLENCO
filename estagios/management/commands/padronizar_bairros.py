from django.core.management.base import BaseCommand
from estagios.models import Candidato

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando a padronização...")

        candidatos = Candidato.objects.all()
        contador = 0

        for candidato in candidatos:
            mudou = False
            bairro_original = candidato.bairro

            bairro_limpo = candidato.bairro.strip().upper()

            if bairro_limpo.startswith('VL '):
                bairro_limpo = bairro_limpo.replace('VL ', 'VILA ', 1)
            elif bairro_limpo.startswith('JD '):
                bairro_limpo = bairro_limpo.replace('JD ', 'JARDIM ', 1)
            elif bairro_limpo.startswith('PQ '):
                bairro_limpo = bairro_limpo.replace('PQ ', 'PARQUE ', 1)
            elif bairro_limpo.startswith('ST '):
                bairro_limpo = bairro_limpo.replace('ST ', 'SANTO ', 1)
            elif bairro_limpo.startswith('STA '):
                bairro_limpo = bairro_limpo.replace('STA ', 'SANTA ', 1)
            elif bairro_limpo.startswith('CID '):
                bairro_limpo = bairro_limpo.replace('CID ', 'CIDADE ', 1)
            elif bairro_limpo.startswith('Itap '):
                bairro_limpo = bairro_limpo.replace('Itap ', 'Itapegica', 1)
            elif bairro_limpo.startswith('jd. '):
                bairro_limpo = bairro_limpo.replace('jd. ', 'JARDIM ', 1)
            elif bairro_limpo.startswith('JD. '):
                bairro_limpo = bairro_limpo.replace('JD. ', 'JARDIM ', 1)
            elif bairro_limpo.startswith('pq '):
                bairro_limpo = bairro_limpo.replace('pq ', 'PARQUE ', 1)

            if bairro_limpo.endswith(' III'):
                bairro_limpo = bairro_limpo.replace(' III', ' 3')
            elif bairro_limpo.endswith(' II'):
                bairro_limpo = bairro_limpo.replace(' II', ' 2')
            elif bairro_limpo.endswith(' I'):
                bairro_limpo = bairro_limpo.replace(' I', ' 1')

            if bairro_original != bairro_limpo:
                candidato.bairro = bairro_limpo
                candidato.save(update_fields=['bairro'])
                mudou = True
                contador += 1

        self.stdout.write(self.style.SUCCESS(f'Sucesso! {contador} bairros foram corrigidos.'))