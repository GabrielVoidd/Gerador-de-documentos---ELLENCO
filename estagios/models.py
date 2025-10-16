from django.db import models
from django.utils import timezone
from datetime import date
from rest_framework.exceptions import ValidationError


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
        verbose_name = 'Parte Concedente'
        verbose_name_plural = 'Partes Concedentes'

    def __str__(self):
        return self.razao_social


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
    rg = models.CharField(max_length=9, unique=True)
    anexar_rg = models.FileField(
        verbose_name='Anexar RG',
        upload_to='documentos_candidatos/rg/%Y%/%m/%d/', null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True)
    anexar_cpf = models.FileField(
        verbose_name='Anexar CPF',
        upload_to='documentos_candidatos/cpf/%Y%/%m/%d/', null=True, blank=True)
    data_nascimento = models.DateField()
    estado_civil = models.CharField(max_length=1, choices=EstadosCivis.choices)
    tem_filhos = models.BooleanField(help_text='Tem filhos?', default=False)
    filhos_detalhes = models.CharField(help_text='Quais as idades?', max_length=150, null=True, blank=True)
    celular = models.CharField(max_length=11, unique=True, help_text='11911112222')
    celular2 = models.CharField(max_length=11, unique=True, help_text='Opcional', null=True, blank=True)
    email = models.EmailField()
    rede_social = models.CharField(max_length=100, null=True, blank=True, help_text='Instagram ou Facebook')
    cep = models.CharField(max_length=9, null=True, blank=True, help_text='00000-000')
    endereco = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2)

    # --- INFORMAÇÕES ADICIONAIS ---
    habilitacao = models.CharField(max_length=2, choices=Habilitacoes.choices)
    fumante = models.BooleanField(help_text='É fumante?', default=False)
    religiao = models.CharField(
        max_length=100, null=True, blank=True, help_text='Possui alguma religião? Se sim, qual?')
    conheceu_agencia = models.CharField(max_length=100, help_text='Como conheceu a agência?')

    # --- FORMAÇÃO ACADÊMICA ---
    escolaridade = models.CharField(max_length=3, choices=Escolaridades.choices)
    curso = models.CharField(max_length=70, help_text='Nome do curso', null=True, blank=True)
    periodo = models.CharField(max_length=1, choices=Periodos.choices)
    serie_semestre = models.CharField(max_length=50, help_text='2° semestre / 3°ano')
    data_termino = models.DateField(help_text='Quando o curso / escola acaba?', null=True, blank=True)
    instituicao_ensino = models.ForeignKey(InstituicaoEnsino, on_delete=models.PROTECT)
    vale_transporte = models.CharField(max_length=2, choices=ValeTransporte.choices, default='E')
    curso_extracurricular = models.CharField(max_length=200, help_text='Sim, de informática das 08h as 10h / Não')
    anexar_declaracao = models.FileField(null=True, blank=True, upload_to='documentos_candidatos/declaracao/%Y%/%m/%d/')

    # --- INFORMAÇÕES PROFISSIONAIS ---
    trabalho = models.CharField(max_length=2, choices=Trabalhos.choices)
    disponibilidade_final_semana = models.BooleanField(help_text='Pode trabalhar de final de semana?', default=False)
    microsoft_365 = models.CharField(
        max_length=2, choices=Microsoft_365.choices, help_text='Nível de conhecimento do pacote office')
    experiencia_profissional = models.TextField(
        help_text='Exemplo: Empresa X, 08/23-03/25, atividades que desempenhava', null=True, blank=True)
    area_interesse = models.CharField(max_length=100, help_text='Qual a sua área de interesse?')
    vaga_pretendida = models.CharField(max_length=100, help_text='Para qual vaga você deseja ser encaminhado(a)?')
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

    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'

    def __str__(self):
        return self.nome


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
    numero_apolice_seguro = models.CharField(max_length=50)
    jornada_estagio = models.CharField(max_length=150, null=True, blank=True,
                                       help_text='de segunda a domingo com uma folga na semana e 15 minutos de pausa')
    valor_bolsa = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # A lógica só funciona na criação de um novo contrato
        is_new = self._state.adding

        super().save(*args, **kwargs)

        # Se o número do contrato ainda não foi definido
        if is_new and not self.numero_contrato:
            ano_atual = self.data_inicio.year if self.data_inicio else timezone.now().year

            # Formata o número: CT=[ANO]-[ID com 4 dígitos, preenchido com zeros (0001 por diante)]
            numero_formatado = f'CT-{ano_atual}-{self.id:04d}'
            self.numero_contrato = numero_formatado

            # Salva novamente o objeto, mas atualizando somente o campo do número do contrato
            # kwargs['force_insert'] = False # Garante o salvamento
            super().save(update_fields=['numero_contrato'])

        # Se for uma atualização de um objeto já existe, salva normalmente
        # elif not is_new:
            # super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f'Contrato {self.numero_contrato} - {self.estagiario.nome}'


class Rescisao(models.Model):
    contrato = models.OneToOneField(Contrato, on_delete=models.PROTECT)
    data_rescisao = models.DateField()
    motivo = models.TextField()

    class Meta:
        verbose_name = 'Rescisão'
        verbose_name_plural = 'Rescisões'

    def __str__(self):
        return f'Rescisão do Contrato {self.contrato.numero_contrato}'
