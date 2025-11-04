from rest_framework import serializers
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato, \
TipoEvento, Lancamento, Recibo


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


class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEvento
        fields = ['id', 'descricao', 'tipo']


class LancamentoSerializer(serializers.ModelSerializer):
    tipo_evento = TipoEventoSerializer(read_only=True)
    # Campo usado para escrita
    tipo_evento_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoEvento.objects.all(),source='tipo_evento', write_only=True
    )

    recibo_id = serializers.PrimaryKeyRelatedField(
        queryset=Recibo.objects.all(), source='recibo', write_only=True
    )

    class Meta:
        model = Lancamento
        fields = [
            'id', 'recibo_id', 'tipo_evento_id', 'tipo_evento', 'valor'
        ]


class ReciboSerializer(serializers.ModelSerializer):
    # many=True porque é uma lista
    # read_only=True porque os lançamentos são criados/deletados separadamente, não como parte da criação do Recibo
    lancamentos = LancamentoSerializer(many=True, read_only=True)

    # Expor os campos do @property, o cálculo fica a cargo do modelo
    total_creditos = serializers.ReadOnlyField()
    total_debitos = serializers.ReadOnlyField()
    valor_liquido = serializers.ReadOnlyField()

    # Não vai aparecer no GET, pois os campos do snapshot já existem
    contrato = serializers.PrimaryKeyRelatedField(
        queryset=Contrato.objects.all(), write_only=True
    )

    class Meta:
        model = Recibo
        fields = [
            'id', 'contrato',
            # Campos do snapshot, read_only por conta da ViewSet
            'estagiario_nome', 'valor_bolsa', 'data_inicio', 'data_fim', 'beneficio_horario',
            # Dddos do período
            'dias_trabalhados', 'dias_falta',
            # Propriedades calculadas, apenas leitura
            'total_creditos', 'total_debitos', 'valor_liquido',
            # Lista aninhada
            'lancamenos'
            ]

        # Os campos do snapshot são read_only, o front não enviará esses dados
        read_only_fields = [
            'estagiario_nome', 'valor_bolsa', 'data_inicio', 'data_fim', 'beneficio_horario', 'total_creditos',
            'total_debitos', 'valor_liquido', 'lancamentos'
        ]
