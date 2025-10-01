from rest_framework import serializers
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato


class InstituicaoEnsinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituicaoEnsino
        fields = '__all__'


class ParteConcedenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParteConcedente
        fields = '__all__'


class EstagiarioSerializer(serializers.ModelSerializer):
    instituicao_ensino_display = serializers.CharField(source='instituicao_ensino.razao_social', read_only=True)

    class Meta:
        model = Estagiario
        fields = '__all__'
        # extra_kwargs = {'instituicao_ensino': {'read_only': True}}


class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
        depth = 1 # Mostra os dados completos de estagiário e empresa (parte concedente)


class ContratoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'


class RescisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rescisao
        fields = '__all__'
        depth = 1


class RescisaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rescisao
        fields = '__all__'


class AgenteIntegradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenteIntegrador
        fields = '__all__'


class CandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidato
        fields = '__all__'
