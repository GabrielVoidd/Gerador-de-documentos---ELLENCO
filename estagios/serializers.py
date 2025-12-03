from rest_framework import serializers
from .models import InstituicaoEnsino, Estagiario, ParteConcedente, Contrato, Rescisao, AgenteIntegrador, Candidato, \
    TipoEvento, Lancamento, Recibo, ReciboRescisao, LancamentoRescisao, ContratoSocial, Aditivo, CriterioExclusao, \
    ContratoAceite


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


class LancamentoRescisaoSerializer(serializers.ModelSerializer):
    tipo_evento = TipoEventoSerializer(read_only=True)
    # Campo usado para escrita
    tipo_evento_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoEvento.objects.all(),source='tipo_evento', write_only=True
    )

    recibo_rescisao_id = serializers.PrimaryKeyRelatedField(
        queryset=ReciboRescisao.objects.all(), source='recibo_rescisao', write_only=True
    )

    class Meta:
        model = LancamentoRescisao
        fields = [
            'id', 'recibo_rescisao_id', 'tipo_evento_id', 'tipo_evento', 'valor'
        ]


class ReciboSerializer(serializers.ModelSerializer):
    # many=True porque é uma lista
    # read_only=True porque os lançamentos são criados/deletados separadamente, não como parte da criação do Recibo
    lancamentos = LancamentoSerializer(many=True, read_only=True)

    # Expor os campos do @property, o cálculo fica a cargo do modelo
    total_creditos = serializers.ReadOnlyField()
    total_debitos = serializers.ReadOnlyField()
    valor_liquido = serializers.ReadOnlyField()

    # Campo para exibir mês/ano formatado
    mes_referencia = serializers.SerializerMethodField()

    # Campos de relacionamento (somente leitura)
    estagiario_nome = serializers.SerializerMethodField()
    parte_concedente_nome = serializers.SerializerMethodField()

    contrato = serializers.PrimaryKeyRelatedField(
        queryset=Contrato.objects.all(), write_only=True
    )

    class Meta:
        model = Recibo
        fields = [
            'id', 'contrato',

            # Campos do snapshot (ou dinâmicos)
            'estagiario_nome', 'parte_concedente_nome', 'valor_bolsa', 'data_inicio', 'data_fim',

            # Dados do recibo
            'data_referencia', 'dias_referencia', 'dias_trabalhados', 'dias_falta', 'valor', 'beneficio_horario',

            # Campos calculados
            'total_creditos', 'total_debitos', 'total_liquidos', 'mes_referencia',

            # Lista aninhada
            'lancamentos',
        ]

        read_only_fields = [
            'estagiario_nome', 'parte_concedente_nome', 'valor_bolsa', 'data_inicio', 'data_fim', 'beneficio_horario',
            'valor', 'total_creditos', 'total_debitos', 'total_liquidos', 'lancamentos', 'mes_referencia'
        ]

        # --- MÉTODOS AUXILIARES DE EXIBIÇÃO ---

        def get_mes_referencia(self, obj):
            '''Retorna o mês/ano da referência formatada (MM/YYYY)'''
            return obj.data_referencia.strftime('%m/%Y') if obj.data_referencia else None

        def get_estagiario_nome(self, obj):
            '''Exibe o nome do estagiário - prioriza o snapshot, mas busca do contrato se disponível'''
            if obj.estagiario_nome:
                return obj.estagiario_nome
            if obj.contrato and hasattr(obj.contrato, 'estagiario'):
                return obj.contrato.estagiario.candidato.nome
            return None

        def get_parte_concedente_nome(self, obj):
            '''Exibe o nome da parte concedente - prioriza o snapshot, mas busca do contrato se disponível'''
            if obj.parte_concedente_nome:
                return obj.parte_concedente_nome
            if obj.contrato and hasattr(obj.contrato, 'parte_concedente'):
                return obj.contrato.parte_concedente.razao_social
            return None

        # Validações

        def validate_data_referencia(self, value):
            """Valida se a data de referência é o 1.º dia do mês"""
            if value.day != 1:
                raise serializers.ValidationError('A data de referência deve ser o primeiro dia do mês')
            return value


class ReciboRescisaoSerializer(serializers.ModelSerializer):
    lancamentos = LancamentoSerializer(many=True, read_only=True)
    contrato = serializers.PrimaryKeyRelatedField(
        queryset=Contrato.objects.all(), write_only=True
    )
    estagiario_nome = serializers.CharField(read_only=True, help_text='Nome do estagiário (preenchido automaticamente)')

    class Meta:
        model = ReciboRescisao
        fields = '__all__'
        read_only_fields = [
            'estagiario_nome',
            'parte_concedente_nome',
            'valor_bolsa',
            'data_inicio',
            'total_creditos',
            'total_debitos',
            'valor_liquido',
        ]

    def validate(self, attrs):
        """Validações customizadas"""
        data_rescisao = attrs('data_rescisao')
        data_pagamento = attrs('data_pagamento')

        if data_rescisao and data_pagamento:
            if data_pagamento < data_rescisao:
                raise serializers.ValidationError({
                    'data_pagamento': 'A data de pagamento não pode ser anterior à data de rescisão'
                })

        # Valida valores negativos
        decimal_fields = ['saldo_salario', 'recesso_remunerado', 'aviso_previo', 'adiantamento', 'outros_descontos']
        for field in decimal_fields:
            if field in attrs and attrs[field] < 0:
                raise serializers.ValidationError({
                    field: f'O valor de {field} não pode ser negativo'
                })

        return attrs

    # def get_sugestao_saldo_salario(self, obj):
    #     valores = obj.calcular_valores_automaticos()
    #     return valores['saldo_salario']
    #
    # def get_sugestao_recesso(self, obj):
    #     valores = obj.calcular_valores_automaticos()
    #     return valores['recesso']

    def create(self, validated_data):
        # Garante que o contrato está presente para copiar os dados
        contrato = validated_data('contrato')
        if contrato:
            instance = ReciboRescisao.objects.create(**validated_data)
            return instance
        else:
            raise serializers.ValidationError({
                'contrato': 'É necessário informar um contrato válido'
            })


class ContratoSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoSocial
        fields = '__all__'


class AditivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aditivo
        fields = '__all__'


class CriterioExclusaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriterioExclusao
        fields = '__all__'


class ContratoAceiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoAceite
        fields = '__all__'
