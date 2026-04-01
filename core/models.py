from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import math

class BaseUser(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)

    class Meta:
        abstract = True


class Aluno(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    observacoes = models.TextField(blank=True, null=True)
    objetivos = models.TextField(blank=True, null=True)
    medicamentos = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome
    
    @property
    def idade(self):
        if self.data_nascimento:
            today = timezone.now().date()
            return today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None
    
    @property
    def mesociclo_ativo(self):
        """Retorna o mesociclo ativo do aluno"""
        return self.mesociclos.filter(ativo=True).first()
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class Avaliacao(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='avaliacoes')
    data = models.DateField()
    horario = models.TimeField()
    massa_corporal = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Massa Corporal (kg)')
    altura = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Altura (m)')
    
    # Circunferências (em cm)
    circunferencia_torax = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_braco_direito = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_braco_esquerdo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_cintura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_quadril = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_coxa_direita = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_coxa_esquerda = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_panturrilha_direita = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_panturrilha_esquerda = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Dobras cutâneas (em mm)
    dobra_peitoral = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_axilar_media = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_tricipital = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_subescapular = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_abdominal = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_suprailiaca = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_coxa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-data']
    
    def __str__(self):
        return f"Avaliação de {self.aluno.nome} - {self.data}"
    
    @property
    def imc(self):
        """Calcula o IMC"""
        if self.massa_corporal and self.altura and self.altura > 0:
            imc = float(self.massa_corporal) / (float(self.altura) ** 2)
            return round(imc, 2)
        return None

    @property
    def percentual_gordura(self):
        """
        Calcula o percentual de gordura usando a fórmula de Pollock para 3 dobras
        """
        if not self.aluno or not self.aluno.idade:
            return None
            
        if self.aluno.sexo == 'M':
            # Fórmula para homens: Peitoral, Abdominal, Coxa
            dobras = []
            if self.dobra_peitoral and self.dobra_peitoral > 0:
                dobras.append(float(self.dobra_peitoral))
            if self.dobra_abdominal and self.dobra_abdominal > 0:
                dobras.append(float(self.dobra_abdominal))
            if self.dobra_coxa and self.dobra_coxa > 0:
                dobras.append(float(self.dobra_coxa))
                
            if len(dobras) == 3:
                soma = sum(dobras)
                densidade = 1.10938 - (0.0008267 * soma) + (0.0000016 * (soma ** 2)) - (0.0002574 * self.aluno.idade)
                if densidade > 0:
                    percentual = (495 / densidade) - 450
                    # Retorna mesmo se fora do intervalo, mas com aviso no template
                    return round(percentual, 2)
                    
        elif self.aluno.sexo == 'F':
            # Fórmula para mulheres: Tricipital, Suprailiaca, Coxa
            dobras = []
            if self.dobra_tricipital and self.dobra_tricipital > 0:
                dobras.append(float(self.dobra_tricipital))
            if self.dobra_suprailiaca and self.dobra_suprailiaca > 0:
                dobras.append(float(self.dobra_suprailiaca))
            if self.dobra_coxa and self.dobra_coxa > 0:
                dobras.append(float(self.dobra_coxa))
                
            if len(dobras) == 3:
                soma = sum(dobras)
                densidade = 1.099421 - (0.0009929 * soma) + (0.0000023 * (soma ** 2)) - (0.0001392 * self.aluno.idade)
                if densidade > 0:
                    percentual = (495 / densidade) - 450
                    return round(percentual, 2)
                    
        return None
    
    def save(self, *args, **kwargs):
        # Salva a avaliação normalmente
        super().save(*args, **kwargs)


class IET(models.Model):
    """
    Teste Incremental em Esteira
    """
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='testes_iet')
    data = models.DateField()
    velocidade_inicial = models.DecimalField(max_digits=4, decimal_places=2, help_text='Velocidade inicial em km/h')
    velocidade_maxima = models.DecimalField(max_digits=4, decimal_places=2, help_text='Velocidade máxima atingida em km/h')
    duracao_teste = models.DurationField(help_text='Duração total do teste')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'IET - Teste Incremental em Esteira'
        verbose_name_plural = 'IET - Testes Incrementais em Esteira'
        ordering = ['-data']
    
    def __str__(self):
        return f"IET de {self.aluno.nome} - {self.data}"
    
    @property
    def vo2_max(self):
        """
        Calcula o VO2 máximo usando a fórmula de Mayhew (1977)
        Fórmula: VO2max = 1.444 * duracao_minutos + 14.99
        """
        if self.duracao_teste:
            duracao_min = self.duracao_teste.total_seconds() / 60
            vo2 = 1.444 * duracao_min + 14.99
            return round(vo2, 2)
        return None


class Exercicio(models.Model):
    """
    Banco de exercícios
    """
    GRUPOS_MUSCULARES = [
        ('PEITO', 'Peito'),
        ('COSTAS', 'Costas'),
        ('PERNAS', 'Pernas'),
        ('OMBROS', 'Ombros'),
        ('BRACOS', 'Braços'),
        ('ABDOMEN', 'Abdômen'),
        ('CARDIO', 'Cardio'),
        ('OUTROS', 'Outros'),
    ]
    
    nome = models.CharField(max_length=200, unique=True)
    grupo_muscular = models.CharField(max_length=50, choices=GRUPOS_MUSCULARES)
    descricao = models.TextField(blank=True, null=True)
    imagem_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Exercício'
        verbose_name_plural = 'Exercícios'
        ordering = ['grupo_muscular', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_grupo_muscular_display()}"


class Mesociclo(models.Model):
    """
    Mesociclo de treinamento
    """
    TIPO_CHOICES = [
        (2, '2x por semana'),
        (3, '3x por semana'),
        (4, '4x por semana'),
        (5, '5x por semana'),
        (6, '6x por semana'),
        (7, '7x por semana'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='mesociclos')
    tipo = models.IntegerField(choices=TIPO_CHOICES, help_text='Frequência semanal')
    data_inicio = models.DateField()
    semanas_planejadas = models.IntegerField(default=4, help_text='Número de semanas planejadas')
    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Mesociclo'
        verbose_name_plural = 'Mesociclos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"Mesociclo de {self.aluno.nome} - {self.data_inicio}"


class Sessao(models.Model):
    """
    Sessão de treino (ex: Sessão A, B, C)
    """
    mesociclo = models.ForeignKey(Mesociclo, on_delete=models.CASCADE, related_name='sessoes')
    nome = models.CharField(max_length=50, help_text='Ex: Sessão A, Sessão B')
    descricao = models.TextField(blank=True, null=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Sessão'
        verbose_name_plural = 'Sessões'
        ordering = ['mesociclo', 'ordem']
        unique_together = ['mesociclo', 'nome']
    
    def __str__(self):
        return f"{self.mesociclo.aluno.nome} - {self.nome}"


class ExercicioSessao(models.Model):
    """
    Relacionamento entre exercício e sessão
    """
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE, related_name='exercicios_sessao')
    sessao = models.ForeignKey(Sessao, on_delete=models.CASCADE, related_name='exercicios_sessao')
    ordem = models.IntegerField(default=0, help_text='Ordem de execução')
    series = models.IntegerField(default=3)
    reps_por_serie = models.JSONField(help_text='Array com repetições por série', default=list)
    pausa_segundos = models.IntegerField(default=60, help_text='Tempo de pausa entre séries em segundos')
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Exercício da Sessão'
        verbose_name_plural = 'Exercícios da Sessão'
        ordering = ['sessao', 'ordem']
        # unique_together removido - permite mesmo exercício múltiplas vezes na mesma sessão
    
    def __str__(self):
        return f"{self.sessao.nome} - {self.exercicio.nome}"

class SetRealizado(models.Model):
    """
    Registro de séries realizadas pelo aluno
    """
    exercicio_sessao = models.ForeignKey(ExercicioSessao, on_delete=models.CASCADE, related_name='sets_realizados')
    semana = models.IntegerField(help_text='Número da semana do mesociclo')
    data = models.DateField()
    numero_serie = models.IntegerField(help_text='Número da série (1, 2, 3...)')
    carga_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Carga utilizada em kg')
    realizado = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Série Realizada'
        verbose_name_plural = 'Séries Realizadas'
        ordering = ['exercicio_sessao', 'semana', 'data', 'numero_serie']
        unique_together = ['exercicio_sessao', 'semana', 'data', 'numero_serie']
    
    def __str__(self):
        status = "✓" if self.realizado else "✗"
        return f"{self.exercicio_sessao} - Semana {self.semana} - Série {self.numero_serie} {status}"
    
    @property
    def carga_media(self):
        """Calcula a carga média do exercício na semana"""
        from django.db.models import Avg
        return SetRealizado.objects.filter(
            exercicio_sessao=self.exercicio_sessao,
            semana=self.semana,
            realizado=True
        ).aggregate(Avg('carga_kg'))['carga_kg__avg']
    
    @property
    def volume(self):
        """Calcula o volume total (carga * repetições)"""
        if self.carga_kg and self.exercicio_sessao.reps_por_serie:
            reps = self.exercicio_sessao.reps_por_serie
            if self.numero_serie <= len(reps):
                return float(self.carga_kg) * reps[self.numero_serie - 1]
        return None


class TreinoEndurance(models.Model):
    """
    Treino de endurance (cardio)
    """
    TIPO_CHOICES = [
        ('CONTINUO', 'Contínuo'),
        ('INTERVALADO', 'Intervalado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='treinos_endurance')
    semana = models.IntegerField(help_text='Número da semana')
    dia_semana = models.IntegerField(choices=[(i, f'{i}ª feira') for i in range(1, 8)], help_text='1=Segunda, 7=Domingo')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Campos para treino contínuo
    velocidade_percentual_vmax = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Percentual da velocidade máxima')
    tempo_minutos = models.IntegerField(null=True, blank=True, help_text='Duração em minutos')
    
    # Campos para treino intervalado
    n_sprints = models.IntegerField(null=True, blank=True)
    tempo_sprint = models.IntegerField(null=True, blank=True, help_text='Tempo de cada sprint em segundos')
    tempo_pausa = models.IntegerField(null=True, blank=True, help_text='Tempo de pausa em segundos')
    
    realizado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Treino de Endurance'
        verbose_name_plural = 'Treinos de Endurance'
        ordering = ['aluno', 'semana', 'dia_semana']
    
    def __str__(self):
        return f"{self.aluno.nome} - Semana {self.semana} - {self.get_dia_semana_display()}"
    
    @property
    def distancia_total(self):
        """
        Calcula a distância total percorrida baseado no teste IET mais recente
        Este é um cálculo simplificado, você pode ajustar conforme sua necessidade
        """
        if self.tipo == 'CONTINUO' and self.velocidade_percentual_vmax and self.tempo_minutos:
            ultimo_iet = self.aluno.testes_iet.first()
            if ultimo_iet and ultimo_iet.vo2_max:
                # Fórmula simplificada: distância = velocidade_média * tempo
                velocidade = (float(self.velocidade_percentual_vmax) / 100) * ultimo_iet.velocidade_maxima
                horas = self.tempo_minutos / 60
                return round(velocidade * horas, 2)
        return None