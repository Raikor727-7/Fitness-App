from django.contrib import admin
from .models import (
    Aluno, Avaliacao, IET, Mesociclo, Sessao, 
    Exercicio, ExercicioSessao, SetRealizado, TreinoEndurance
)

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_nascimento', 'sexo', 'data_cadastro']
    list_filter = ['sexo', 'data_cadastro']
    search_fields = ['nome', 'email']
    readonly_fields = ['data_cadastro', 'data_atualizacao']

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'data', 'massa_corporal', 'altura', 'imc', 'percentual_gordura']
    list_filter = ['data', 'aluno']
    search_fields = ['aluno__nome']
    readonly_fields = ['imc', 'percentual_gordura']

@admin.register(IET)
class IETAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'data', 'velocidade_maxima', 'duracao_teste', 'vo2_max']
    list_filter = ['data', 'aluno']
    search_fields = ['aluno__nome']
    readonly_fields = ['vo2_max']

@admin.register(Mesociclo)
class MesocicloAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'data_inicio', 'tipo', 'semanas_planejadas', 'ativo']
    list_filter = ['ativo', 'data_inicio', 'tipo']
    search_fields = ['aluno__nome']

@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'mesociclo', 'ordem']
    list_filter = ['mesociclo']
    search_fields = ['nome', 'mesociclo__aluno__nome']

@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'grupo_muscular', 'ativo']
    list_filter = ['grupo_muscular', 'ativo']
    search_fields = ['nome']
    list_editable = ['ativo']

@admin.register(ExercicioSessao)
class ExercicioSessaoAdmin(admin.ModelAdmin):
    list_display = ['exercicio', 'sessao', 'ordem', 'series', 'pausa_segundos']
    list_filter = ['sessao__mesociclo', 'exercicio__grupo_muscular']
    search_fields = ['exercicio__nome', 'sessao__nome']

@admin.register(SetRealizado)
class SetRealizadoAdmin(admin.ModelAdmin):
    list_display = ['exercicio_sessao', 'semana', 'data', 'numero_serie', 'carga_kg', 'realizado']
    list_filter = ['realizado', 'data', 'semana']
    search_fields = ['exercicio_sessao__exercicio__nome', 'exercicio_sessao__sessao__aluno__nome']
    list_editable = ['carga_kg', 'realizado']
    readonly_fields = ['carga_media', 'volume']

@admin.register(TreinoEndurance)
class TreinoEnduranceAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'semana', 'dia_semana', 'tipo', 'realizado']
    list_filter = ['tipo', 'realizado', 'semana']
    search_fields = ['aluno__nome']