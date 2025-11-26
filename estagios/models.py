from django.db import models
from django.utils import timezone
from datetime import date
from rest_framework.exceptions import ValidationError
from unidecode import unidecode
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
import re
from unicodedata import normalize


# null para o banco, blank para forms e admin

class InstituicaoEnsino(models.Model):
    razao_social = models.CharField(max_length=250)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=250)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    representante_legal = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Instituição de Ensino'
        verbose_name_plural = 'Instituições de Ensino'

    def __str__(self):
        return self.razao_social


class ParteConcedente(models.Model):
    class Documentos(models.TextChoices):
        CPF = 'C', 'CPF'
        RG = 'R', 'RG'

    razao_social = models.CharField(max_length=250)
    endereco = models.CharField(max_length=250)
    bairro = models.CharField(max_length=100)
    local_trabalho = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2)
    cnpj = models.CharField(max_length=18, unique=True)
    representante_legal = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()
    ramo_atividade = models.CharField(max_length=200, null=True, verbose_name='Ramo de atividade')

    class Meta:
        verbose_name = 'Parte Concedente'
        verbose_name_plural = 'Partes Concedentes'

    def __str__(self):
        return self.razao_social


class DetalhesParteConcedente(models.Model):
    parte_concedente = models.ForeignKey(ParteConcedente, on_delete=models.PROTECT, related_name='detalhes')
    dia_pagamento_estagiario = models.IntegerField(null=True, blank=True)
    dia_cobranca_agencia = models.IntegerField(null=True, blank=True)
    dia_fechamento = models.IntegerField(null=True, blank=True)
    mensalidade_contrato = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    taxa_cliente = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)


class ContratoSocial(models.Model):
    # Informações adicionais da Parte Concedente para a criação do contrato social
    parte_concedente = models.ForeignKey(ParteConcedente, on_delete=models.PROTECT, related_name='adicionais')
    nome_dono = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nome do(a) dono(a)')
    documentos_dono = models.CharField(verbose_name='CPF do(a) dono(a)', null=True, unique=True, blank=True)
    nome_socio = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nome do(a) sócio(a)')
    documentos_socio = models.FileField(verbose_name='CPF do(a) sócio(a)', null=True, unique=True, blank=True)
    nome_resp_rh = models.CharField(max_length=100, verbose_name='Nome do(a) responsável do RH')
    numero_resp_rh = models.CharField(max_length=11, help_text='Número do telefone com DDD e sem traços',
         verbose_name='Número do(a) responsável do RH')
    email_resp_rh = models.EmailField(verbose_name='Email do(a) responsável do RH')
    nome_resp_estagio = models.CharField(max_length=100, verbose_name='Nome do(a) responsável do estágio')
    data_cadastro = models.DateField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Contrato Social'
        verbose_name_plural = 'Contratos Sociais'

    def __str__(self):
        return f'Contrato_Social_{self.parte_concedente.razao_social}'


class Aditivo(models.Model):
    contrato_social = models.ForeignKey(ContratoSocial, on_delete=models.PROTECT, related_name='contrato_social')
    data_cadastro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aditivo'
        verbose_name_plural = 'Aditivos'

    def __str__(self):
        return f'Aditivo_{self.contrato_social.parte_concedente.razao_social}'


class Candidato(models.Model):
    class EstadosCivis(models.TextChoices):
        SOLTEIRO = 'S', 'Solteiro(a)'
        CASADO = 'C', 'Casado(a)'
        DIVORCIADO = 'D', 'Divorciado(a)'
        VIUVO = 'V', 'Viúvo(a)'

    class Escolaridades(models.TextChoices):
        ENSINO_MEDIO = 'EM', 'Ensino Médio'
        ENSINO_MEDIO_TECNICO = 'EMT', 'Ensino Médio Técnico'
        ENSINO_SUPERIOR = 'ES', 'Ensino Superior'
        EDUCACAO_JOVEM_ADULTO = 'EJA', 'Educação de Jovens e Adultos'

    class Periodos(models.TextChoices):
        MANHA = 'M', 'Manhã'
        TARDE = 'T', 'Tarde'
        NOITE = 'N', 'Noite'
        INTEGRAL = 'I', 'Integral'
        EAD = 'E', 'EAD'

    class ValeTransporte(models.TextChoices):
        TOP = 'T', 'Top'
        CIDADAO = 'C', 'Cidadão'
        ESTUDANTE = 'E', 'Estudante'
        NAO_TEM = 'NT', 'Não tem'

    class Trabalhos(models.TextChoices):
        COM_REGISTRO = 'CR', 'Sim, com registro'
        SEM_REGISTRO = 'SR', 'Sim, sem registro'
        NAO = 'N', 'Não'

    class Microsoft_365(models.TextChoices):
        SEM_CONHECIMENTO = 'SC', 'Sem conhecimento'
        BASICO = 'B', 'Básico'
        INTERMEDIARIO = 'I', 'Intermediário'
        AVANCADO = 'A', 'Avançado'

    class Habilitacoes(models.TextChoices):
        NP = 'NP', 'Não possui'
        A = 'A', 'Categoria A'
        B = 'B', 'Categoria B'
        C = 'C', 'Categoria C'
        D = 'D', 'Categoria D'
        E = 'E', 'Categoria E'
        AB = 'AB', 'Categorias A e B'

    class PCD(models.TextChoices):
        SIM = 'S', 'Sim'
        NAO = 'N', 'Não'
        PREFIRO_NAO_RESPONDER = 'PNR', 'Prefiro não responder'

    # --- DADOS PESSOAIS ---
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=50)
    rg = models.CharField(max_length=9, unique=True, blank=True, verbose_name='RG')
    anexar_rg = models.FileField(
        verbose_name='Anexar RG',
        upload_to='documentos_candidatos/rg/%Y%/%m/%d/', null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF')
    anexar_cpf = models.FileField(
        verbose_name='Anexar CPF',
        upload_to='documentos_candidatos/cpf/%Y%/%m/%d/', null=True, blank=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    estado_civil = models.CharField(max_length=1, choices=EstadosCivis.choices)
    tem_filhos = models.BooleanField(help_text='Tem filhos?', default=False)
    filhos_detalhes = models.CharField(help_text='Quais as idades?', max_length=150, null=True, blank=True)
    celular = models.CharField(max_length=11, unique=True, help_text='11911112222')
    celular2 = models.CharField(max_length=11, unique=True, help_text='Opcional', null=True, blank=True)
    email = models.EmailField()
    rede_social = models.CharField(max_length=100, null=True, blank=True, help_text='Instagram ou Facebook')
    cep = models.CharField(max_length=9, null=True, blank=True, help_text='00000-000', verbose_name='CEP')
    endereco = models.CharField(max_length=200, verbose_name='Endereço')
    numero = models.CharField(max_length=10, verbose_name='Número')
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2)

    # --- INFORMAÇÕES ADICIONAIS ---
    habilitacao = models.CharField(max_length=2, choices=Habilitacoes.choices, verbose_name='Habilitação')
    fumante = models.BooleanField(help_text='É fumante?', default=False)
    religiao = models.CharField(
        max_length=100, null=True, blank=True, help_text='Possui alguma religião? Se sim, qual?', verbose_name='Religião')
    anexar_reservista = models.FileField(
        verbose_name='Anexar Reservista',
        upload_to='documentos_candidatos/reservistas/%Y%/%m/%d/', null=True, blank=True)
    conheceu_agencia = models.CharField(max_length=100, verbose_name='Como conheceu a agência?')

    # --- FORMAÇÃO ACADÊMICA ---
    escolaridade = models.CharField(max_length=3, choices=Escolaridades.choices)
    curso = models.CharField(max_length=70, help_text='Nome do curso', null=True, blank=True)
    periodo = models.CharField(max_length=1, choices=Periodos.choices, verbose_name='Período')
    serie_semestre = models.CharField(max_length=50, help_text='2° semestre / 3°ano', verbose_name='Série ou Semestre')
    data_termino = models.DateField(verbose_name='Quando o curso / escola acaba?', null=True, blank=True)
    instituicao_ensino = models.ForeignKey(InstituicaoEnsino, on_delete=models.PROTECT)
    nome_da_instituicao = models.CharField(max_length=150, null=True, blank=True, help_text='Caso não esteja na lista')
    app_escolar = models.CharField(max_length=50, blank=True,
                                   help_text='Não / Nome do aplicativo da escola/faculdade caso tenha',
                                   verbose_name='Aplicativo da escola/faculdade')
    vale_transporte = models.CharField(max_length=2, choices=ValeTransporte.choices, default='E')
    curso_extracurricular = models.CharField(max_length=200, help_text='Sim, de informática das 08h as 10h / Não')
    anexar_declaracao = models.FileField(null=True, blank=True, upload_to='documentos_candidatos/declaracao/%Y%/%m/%d/')

    # --- INFORMAÇÕES PROFISSIONAIS ---
    trabalho = models.CharField(max_length=2, choices=Trabalhos.choices)
    anexar_carteira_trabalho = models.FileField(
        verbose_name='Anexar Carteira de Trabalho',
        upload_to='documentos_candidatos/carteiras_trabalho/%Y%/%m/%d/', null=True, blank=True)
    disponibilidade_final_semana = models.BooleanField(help_text='Pode trabalhar de final de semana?', default=False)
    microsoft_365 = models.CharField(
        max_length=2, choices=Microsoft_365.choices, help_text='Nível de conhecimento do pacote office')
    experiencia_profissional = models.TextField(
        help_text='Exemplo: Empresa X, 08/23-03/25, atividades que desempenhava', null=True, blank=True)
    area_interesse = models.CharField(max_length=100, help_text='Qual a sua área de interesse?', verbose_name='Área de interesse')
    vaga_pretendida = models.CharField(max_length=100, help_text='Para qual vaga você deseja ser encaminhado(a)?',
                                       editable=False)
    pretensao_salarial = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    anexar_curriculo = models.FileField(null=True, blank=True, upload_to='documentos_candidatos/curriculo/%Y/%m/%d/')

    # --- INFORMAÇÕES MÉDICAS ---
    medicamento_constante = models.CharField(max_length=100, help_text='Faz uso de algum medicamento constante?')
    alergia = models.CharField(max_length=100, help_text='Tem alergia a algum medicamento? Se sim, qual?')
    problema_saude = models.CharField(max_length=100, help_text='Tem algum problema de saúde?')
    pcd = models.CharField(max_length=3, help_text='Você é uma pessoa com deficiência (PCD)?', choices=PCD.choices)
    pcd_detalhes = models.CharField(max_length=150, help_text='Se sim, qual(is)?', null=True, blank=True)

    # --- INFORMAÇÕES DOS RESPONSÁVEIS ---
    nome_responsavel_legal = models.CharField(max_length=70, null=True, blank=True, help_text='Pai, mãe ou guardião(ã)')
    telefone_responsavel_legal = models.CharField(max_length=11, null=True, blank=True)
    email_responsavel_legal = models.EmailField(null=True, blank=True)
    idade_responsavel_legal = models.PositiveSmallIntegerField(null=True, blank=True)
    profissao_responsavel_legal = models.CharField(max_length=100, null=True, blank=True)
    nome_responsavel_legal2 = models.CharField(max_length=70, null=True, blank=True)
    telefone_responsavel_legal2 = models.CharField(max_length=11, null=True, blank=True)
    email_responsavel_legal2 = models.EmailField(null=True, blank=True)
    idade_responsavel_legal2 = models.PositiveSmallIntegerField(null=True, blank=True)
    profissao_responsavel_legal2 = models.CharField(max_length=100, null=True, blank=True)

    # --- INFORMAÇÕES PARA O(A) RECRUTADOR (A) ---
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateField(auto_now_add=True, null=True, blank=True)
    restrito = models.BooleanField(default=False)

    def clean(self):
        super().clean()

        if self.celular and self.celular2 and self.celular == self.celular2:
            raise ValidationError({'celular2': 'O segundo número de celular não pode ser igual ao primeiro'})

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
                    (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))

    @property
    def filho_detalhes_formatado(self):
        if not self.filhos_detalhes:
            return 'Nenhuma observação'
        return self.filhos_detalhes

    @property
    def religiao_formatada(self):
        if not self.religiao:
            return 'Nenhuma observação'
        return self.religiao

    @property
    def celular2_formatado(self):
        if not self.celular2:
            return '-'
        return self.celular2

    @property
    def pcd_detalhes_formatado(self):
        if not self.pcd_detalhes:
            return 'Nenhuma observação'
        return self.pcd_detalhes

    def nome_responsavel_formatado(self):
        if not self.nome_responsavel_legal:
            return '-'
        return self.nome_responsavel_legal

    def nome_responsavel2_formatado(self):
        if not self.nome_responsavel_legal2:
            return '-'
        return self.nome_responsavel_legal2

    def telefone_responsavel_formatado(self):
        if not self.telefone_responsavel_legal:
            return '-'
        return self.telefone_responsavel_legal

    def telefone_responsavel2_formatado(self):
        if not self.telefone_responsavel_legal2:
            return '-'
        return self.telefone_responsavel_legal2

    def email_responsavel_formatado(self):
        if not self.email_responsavel_legal:
            return '-'
        return self.email_responsavel_legal

    def email_responsavel2_formatado(self):
        if not self.email_responsavel_legal2:
            return '-'
        return self.email_responsavel_legal2

    def save(self, *args, **kwargs):
        if self.nome:
            texto= self.nome.upper()
            # NFKD separa a letra do acento, e o encode remove o acento solto
            texto = normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
            self.nome = re.sub(r'[^A-Z]', '', texto)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'

    def __str__(self):
        return self.nome


class CartaEncaminhamento(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='cartas')
    arquivo = models.FileField(upload_to='cartas_encaminhamento/', null=True, blank=True)
    data_emissao = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.arquivo.name

    class Meta:
        verbose_name = "Carta de Encaminhamento"
        verbose_name_plural = "Cartas de Encaminhamento"


class Arquivos(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='arquivos')
    arquivo = models.FileField(upload_to='arquivos/', null=True, blank=True)
    data_emissao = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.arquivo.name

    class Meta:
        verbose_name = 'Arquivo'
        verbose_name_plural = 'Arquivos'


class Empresa(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='empresas')
    nome = models.CharField(max_length=120, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'


class DetalhesEmpresa(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='detalhes')
    arquivos = models.FileField(upload_to='empresas/', null=True, blank=True)

    class Meta:
        verbose_name = 'Detalhes Empresa'
        verbose_name_plural = 'Detalhes Empresas'


class Estagiario(models.Model):
    # primary_key=True assegura que existirá somente um registro de Estagiário para Candidato
    candidato = models.OneToOneField(Candidato, on_delete=models.CASCADE, null=True)
    instituicao_ensino = models.ForeignKey(InstituicaoEnsino, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Estagiário'
        verbose_name_plural = 'Estagiários'

    def __str__(self):
        if self.candidato:
            return self.candidato.nome
        return 'Sem candidato(a)'


class AgenteIntegrador(models.Model):
    razao_social = models.CharField(max_length=250)
    endereco = models.CharField(max_length=250)
    bairro = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cnpj = models.CharField(max_length=18, unique=True)
    representante_legal = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Agente Integrador'
        verbose_name_plural = 'Agentes Integradores'

    def __str__(self):
        return self.razao_social


class Contrato(models.Model):
    numero_contrato = models.CharField(max_length=50, unique=True, blank=True, editable=False)
    estagiario = models.ForeignKey(Estagiario, on_delete=models.PROTECT)
    parte_concedente = models.ForeignKey(ParteConcedente, on_delete=models.PROTECT)
    agente_integrador = models.ForeignKey(AgenteIntegrador, on_delete=models.PROTECT)
    data_inicio = models.DateField()
    data_termino_prevista = models.DateField()
    horario_estagio = models.CharField(max_length=100)
    atividades = models.TextField()
    setor = models.CharField(max_length=100)
    supervisor_nome = models.CharField(max_length=100)
    numero_apolice_seguro = models.CharField(max_length=50, default='363787')
    jornada_estagio = models.CharField(max_length=150, null=True, blank=True,
                                       help_text='de segunda a domingo com uma folga na semana e 15 minutos de pausa')
    valor_bolsa = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    data_criacao = models.DateField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            novo = self.pk is None
            super().save(*args, **kwargs)

            if novo:
                ano_atual = self.data_inicio.year if self.data_inicio else timezone.now().year
                self.numero_contrato = f'CT-{ano_atual}-{self.id:04d}'
                super().save(update_fields=['numero_contrato'])

        except Exception as e:
            print(e)
            raise

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f'Contrato {self.numero_contrato} - {self.estagiario.candidato.nome}'


class MotivoRescisao(models.Model):
    motivo = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.motivo

    class Meta:
        verbose_name = 'Motivo da rescisão'
        verbose_name_plural = 'Motivos da rescisão'


class Rescisao(models.Model):
    contrato = models.OneToOneField(Contrato, on_delete=models.PROTECT)
    data_rescisao = models.DateField()
    motivo = models.ForeignKey(MotivoRescisao, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Rescisão'
        verbose_name_plural = 'Rescisões'

    def __str__(self):
        return f'Rescisão do Contrato {self.contrato.numero_contrato}'


class TipoEvento(models.Model):
    class TipoTransacao(models.TextChoices):
        CREDITO = 'CREDITO', 'Crédito'
        DEBITO = 'DEBITO', 'Débito'

    descricao = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=10, choices=TipoTransacao.choices)

    def __str__(self):
        return f'{self.descricao} ({self.tipo})'


class Recibo(models.Model):
    # --- RASTREABILIDADE ---
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True)

    # --- DADOS DO SNAPSHOT (COPIADOS DO CONTRATO) ---
    estagiario_nome = models.CharField(max_length=100)
    parte_concedente_nome = models.CharField(max_length=100)
    valor_bolsa = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    # --- DADOS DO RECIBO EM SI ---
    data_referencia = models.DateField(help_text='Deve ser o 1º dia do mês de referência')
    dias_referencia = models.IntegerField(default=30)
    dias_trabalhados = models.IntegerField()
    dias_falta = models.IntegerField(default=0)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    beneficio_horario = models.TextField(blank=True)

    # --- CÁLCULOS DOS TOTAIS ---
    @property
    def total_creditos(self):
        return self.lancamentos.filter(tipo_evento__tipo='CREDITO').aggregate(total=models.Sum('valor'))['total'] or Decimal(0.00)

    @property
    def total_debitos(self):
        return self.lancamentos.filter(tipo_evento__tipo='DEBITO').aggregate(total=models.Sum('valor'))['total'] or Decimal(0.00)

    @property
    def valor_proporcional(self):
        if not self.valor_bolsa or not self.dias_referencia or self.dias_referencia == 0:
            return Decimal('0.00')

        dias_trabalhados_dec = Decimal(self.dias_trabalhados) if self.dias_trabalhados else Decimal('0')
        dias_referencia_dec = Decimal(self.dias_referencia)

        proporcao = dias_trabalhados_dec / dias_referencia_dec
        base = (self.valor_bolsa * proporcao).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return base

    @property
    def valor_liquido(self):
        if not self.valor_bolsa or not self.dias_referencia:
            return Decimal('0.00')

        proporcao = Decimal(self.dias_trabalhados) / Decimal(self.dias_referencia)
        base = (self.valor_bolsa * proporcao).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = base + self.total_creditos - self.total_debitos
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        # --- POPULANDO O SHAPSHOT ---
        # Se os campos estiverem vazios (ao criar), copia do contrato
        if self.contrato and not self.valor_bolsa:
            self.estagiario_nome = self.contrato.estagiario.candidato.nome
            self.parte_concedente_nome = self.contrato.parte_concedente.razao_social
            self.valor_bolsa = self.contrato.valor_bolsa
            self.data_inicio = self.contrato.data_inicio
            self.data_fim = self.contrato.data_termino_prevista

        # Caso não seja especificada uma data de referência, será usado o primeiro dia do mês anterior
        if not self.data_referencia:
            hoje = date.today()
            primeiro_dia_mes_anterior = (hoje.replace(day=1) - relativedelta(months=1))
            self.data_referencia = primeiro_dia_mes_anterior

        # Cálculo automático caso os dias trabalhados não forem especificados
        if not self.dias_trabalhados and self.dias_referencia:
            self.dias_trabalhados = self.dias_referencia - self.dias_falta

        if not self.valor:
            self.valor = self.calcular_valor_final()

        # Atualiza dias_trabalhados antes de salvar
        self.dias_trabalhados = max(0, self.dias_referencia - self.dias_falta)

        # Chama o metodo 'save' original para salvar no banco
        super().save(*args, **kwargs)

    def __str__(self):
        mes_ano = self.data_referencia.strftime('%m/%Y') if self.data_referencia else 'sem data'
        return f'Recibo de {self.estagiario_nome} - {mes_ano}'


class ReciboRescisao(models.Model):
    # --- RASTREABILIDADE ---
    contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT, null=True, blank=True)

    # --- DADOS DO SNAPSHOT ---
    estagiario_nome = models.CharField(max_length=100)
    parte_concedente_nome = models.CharField(max_length=100)
    valor_bolsa = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    # --- MOTIVO DA RESCISÃO ---
    motivo_rescisao = models.ForeignKey(MotivoRescisao, on_delete=models.PROTECT, null=True, blank=True)

    # --- DATAS IMPORTANTES ---
    data_rescisao = models.DateField()
    data_pagamento = models.DateField()

    # --- CÁLCULOS BASE ---
    dias_trabalhados_mes = models.IntegerField(default=0, help_text='Dias trabalhados no mês da rescisão')
    dias_recesso_devidos = models.IntegerField(default=0, help_text='Dias de recesso devidos')

    class Meta:
        verbose_name = 'Recibo de Rescisão'
        verbose_name_plural = 'Recibos de Rescisão'

    def __str__(self):
        data_str = self.data_rescisao.strftime("%d/%m/%Y") if self.data_rescisao else "Data N/A"
        return f'Rescisão Estágio - {self.estagiario_nome} - {data_str}'

    # --- MÉTODOS DE CÁLCULO DE DIAS ---

    def calcular_dias_trabalhados_mes(self):
        """Calcula dias trabalhados no mês da rescisão"""
        if not self.data_rescisao:
            return 0

        # Se a rescisão for no último dia do mês, considera-se mês cheio (30 dias ou dias reais)
        # Lógica simplificada: dia da rescisão
        ultimo_dia_mes = (self.data_rescisao.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        if self.data_rescisao == ultimo_dia_mes:
            return 30  # Padronização comercial comum, mas ajuste conforme sua regra (ex: 31)
        else:
            return self.data_rescisao.day

    def calcular_dias_recesso_proporcional(self):
        """Calcula os dias de recesso proporcionais baseados no tempo de contrato"""
        if not self.data_inicio or not self.data_rescisao:
            return 0

        delta = relativedelta(self.data_rescisao, self.data_inicio)
        meses_trabalhados = delta.years * 12 + delta.months

        if delta.days > 14:  # Regra comum: fração superior a 14 dias conta como mês
            meses_trabalhados += 1
        elif delta.days > 0:
            meses_trabalhados += delta.days / 30.0

        # 30 dias de recesso a cada 12 meses
        dias_recesso = (meses_trabalhados / 12) * 30
        return round(dias_recesso)

    # --- MÉTODOS DE VALORES E SINCRONIZAÇÃO (O "ROBÔ") ---

    def calcular_valores_automaticos(self):
        """Calcula valores monetários (apenas memória)"""
        valor_bolsa = self.valor_bolsa or Decimal('0.00')

        # Usa valor do campo se existir, senão calcula
        dias_trab = self.dias_trabalhados_mes if self.dias_trabalhados_mes else self.calcular_dias_trabalhados_mes()
        dias_rec = self.dias_recesso_devidos if self.dias_recesso_devidos else self.calcular_dias_recesso_proporcional()

        saldo_salario = Decimal('0.00')
        valor_recesso = Decimal('0.00')

        if valor_bolsa > 0:
            valor_dia = valor_bolsa / Decimal('30')
            saldo_salario = (valor_dia * Decimal(dias_trab)).quantize(Decimal('0.01'))
            valor_recesso = (valor_dia * Decimal(dias_rec)).quantize(Decimal('0.01'))

        return {
            'saldo_salario': saldo_salario,
            'recesso': valor_recesso,
            'dias_trabalhados': dias_trab,
            'dias_recesso': dias_rec
        }

    def sincronizar_lancamentos_automaticos(self):
        """O Robô: Cria/Atualiza os registros na tabela de lançamentos"""
        valores = self.calcular_valores_automaticos()

        # Garante que os Tipos de Evento existem
        tipo_saldo, _ = TipoEvento.objects.get_or_create(
            descricao='Saldo de Bolsa',
            defaults={'tipo': TipoEvento.TipoTransacao.CREDITO}
        )
        tipo_recesso, _ = TipoEvento.objects.get_or_create(
            descricao='Recesso Indenizado',
            defaults={'tipo': TipoEvento.TipoTransacao.CREDITO}
        )

        # Atualiza ou Cria os Lançamentos Filhos
        self.lancamentos_rescisao.update_or_create(
            tipo_evento=tipo_saldo,
            defaults={'valor': valores['saldo_salario']}
        )
        self.lancamentos_rescisao.update_or_create(
            tipo_evento=tipo_recesso,
            defaults={'valor': valores['recesso']}
        )

    # --- PROPERTIES E TOTAIS ---

    @property
    def total_creditos(self):
        # Como o "Robô" já colocou o Saldo e o Recesso no banco,
        # este aggregate JÁ INCLUI TUDO (Base + Extras).
        return self.lancamentos_rescisao.filter(
            tipo_evento__tipo=TipoEvento.TipoTransacao.CREDITO
        ).aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')

    @property
    def total_debitos(self):
        return self.lancamentos_rescisao.filter(
            tipo_evento__tipo=TipoEvento.TipoTransacao.DEBITO
        ).aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')

    @property
    def saldo_liquido(self):
        # ATENÇÃO: Simplificado para evitar duplicação
        # Total Créditos (já tem salário e recesso) - Total Débitos
        return (self.total_creditos - self.total_debitos).quantize(Decimal('0.01'))

    # Properties auxiliares para acesso rápido aos valores calculados (opcional)
    @property
    def saldo_salario_valor(self):
        return self.calcular_valores_automaticos()['saldo_salario']

    @property
    def recesso_valor(self):
        return self.calcular_valores_automaticos()['recesso']

    # --- SAVE OVERRIDE ---

    def save(self, *args, **kwargs):
        # 1. Snapshot (Cópia dos dados do contrato)
        if self.contrato and not self.estagiario_nome:
            self.estagiario_nome = self.contrato.estagiario.candidato.nome
            self.parte_concedente_nome = self.contrato.parte_concedente.razao_social
            self.valor_bolsa = self.contrato.valor_bolsa
            self.data_inicio = self.contrato.data_inicio

        # 2. Preenche Dias Automaticamente (se vazio)
        if not self.dias_trabalhados_mes:
            self.dias_trabalhados_mes = self.calcular_dias_trabalhados_mes()

        if not self.dias_recesso_devidos:
            self.dias_recesso_devidos = self.calcular_dias_recesso_proporcional()

        # 3. Salva o Pai (Recibo) para garantir que temos um ID
        super().save(*args, **kwargs)

        # 4. Chama o Robô para criar os filhos (Lançamentos)
        self.sincronizar_lancamentos_automaticos()


class Lancamento(models.Model):
    recibo = models.ForeignKey(Recibo, on_delete=models.CASCADE, related_name='lancamentos')
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.tipo_evento.descricao} - R${self.valor}'


class LancamentoRescisao(models.Model):
    recibo_rescisao = models.ForeignKey(ReciboRescisao, on_delete=models.CASCADE, related_name='lancamentos_rescisao', null=True)
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Lançamento de rescisão'
        verbose_name_plural = 'Lançamentos de rescisão'

    def __str__(self):
        return f'{self.tipo_evento.descricao} - R${self.valor}'
