from django.utils import timezone
from datetime import timedelta
from .models import Sessao, ExercicioSessao, Exercicio, SetRealizado
import json

def calcular_treino_automatico(mesociclo):
    """
    Gera automaticamente as sessões de treino baseado no tipo de mesociclo
    e nos exercícios padrão
    """
    sessoes_por_semana = mesociclo.tipo
    
    # Definir nomes das sessões baseado na frequência
    templates = {
        2: ['A', 'B'],
        3: ['A', 'B', 'C'],
        4: ['A', 'B', 'C', 'D'],
        5: ['A', 'B', 'C', 'D', 'E'],
        6: ['A', 'B', 'C', 'D', 'E', 'F'],
        7: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    }
    
    nomes_sessoes = templates.get(sessoes_por_semana, ['A', 'B', 'C'])
    
    # Criar as sessões
    sessoes = []
    for i, nome in enumerate(nomes_sessoes):
        sessao = Sessao.objects.create(
            mesociclo=mesociclo,
            nome=f"Sessão {nome}",
            ordem=i
        )
        sessoes.append(sessao)
    
    # Mapeamento de splits por frequência
    if sessoes_por_semana == 2:
        # 2x: Full Body A e B
        exercicios_fullbody = [
            'Agachamento', 'Supino reto', 'Puxada frontal',
            'Desenvolvimento', 'Rosca direta', 'Tríceps pulley', 'Panturrilha'
        ]
        for sessao in sessoes:
            adicionar_exercicios_padrao(sessao, exercicios_fullbody)
    
    elif sessoes_por_semana == 3:
        # Split ABC (Push, Pull, Legs)
        exercicios_push = ['Supino reto', 'Supino inclinado', 'Desenvolvimento', 'Tríceps pulley', 'Elevação lateral']
        exercicios_pull = ['Puxada frontal', 'Remada curvada', 'Remada baixa', 'Rosca direta', 'Rosca martelo']
        exercicios_legs = ['Agachamento', 'Leg press', 'Cadeira extensora', 'Mesa flexora', 'Panturrilha']
        
        adicionar_exercicios_padrao(sessoes[0], exercicios_push)
        adicionar_exercicios_padrao(sessoes[1], exercicios_pull)
        adicionar_exercicios_padrao(sessoes[2], exercicios_legs)
    
    elif sessoes_por_semana == 4:
        # Upper/Lower split (2x Upper, 2x Lower)
        exercicios_upper = ['Supino reto', 'Puxada frontal', 'Desenvolvimento', 'Rosca direta', 'Tríceps pulley']
        exercicios_lower = ['Agachamento', 'Leg press', 'Cadeira extensora', 'Mesa flexora', 'Panturrilha']
        
        adicionar_exercicios_padrao(sessoes[0], exercicios_upper)
        adicionar_exercicios_padrao(sessoes[1], exercicios_lower)
        adicionar_exercicios_padrao(sessoes[2], exercicios_upper)
        adicionar_exercicios_padrao(sessoes[3], exercicios_lower)
    
    elif sessoes_por_semana == 5:
        # Split 5 dias: Peito, Costas, Pernas, Ombros, Braços
        splits = {
            0: ['Supino reto', 'Supino inclinado', 'Crucifixo', 'Tríceps pulley'],
            1: ['Puxada frontal', 'Remada curvada', 'Remada baixa', 'Rosca direta'],
            2: ['Agachamento', 'Leg press', 'Cadeira extensora', 'Mesa flexora', 'Panturrilha'],
            3: ['Desenvolvimento', 'Elevação lateral', 'Encolhimento', 'Tríceps testa'],
            4: ['Rosca direta', 'Rosca martelo', 'Tríceps pulley', 'Tríceps corda']
        }
        for i, sessao in enumerate(sessoes):
            if i in splits:
                adicionar_exercicios_padrao(sessao, splits[i])
    
    elif sessoes_por_semana == 6:
        # Split 6 dias: Push, Pull, Legs, Push, Pull, Legs
        exercicios_push = ['Supino reto', 'Supino inclinado', 'Desenvolvimento', 'Tríceps pulley', 'Elevação lateral']
        exercicios_pull = ['Puxada frontal', 'Remada curvada', 'Remada baixa', 'Rosca direta', 'Rosca martelo']
        exercicios_legs = ['Agachamento', 'Leg press', 'Cadeira extensora', 'Mesa flexora', 'Panturrilha']
        
        adicionar_exercicios_padrao(sessoes[0], exercicios_push)
        adicionar_exercicios_padrao(sessoes[1], exercicios_pull)
        adicionar_exercicios_padrao(sessoes[2], exercicios_legs)
        adicionar_exercicios_padrao(sessoes[3], exercicios_push)
        adicionar_exercicios_padrao(sessoes[4], exercicios_pull)
        adicionar_exercicios_padrao(sessoes[5], exercicios_legs)
    
    elif sessoes_por_semana == 7:
        # 7 dias: Full body com variações
        exercicios_fullbody_a = ['Agachamento', 'Supino reto', 'Puxada frontal', 'Desenvolvimento']
        exercicios_fullbody_b = ['Leg press', 'Supino inclinado', 'Remada curvada', 'Elevação lateral']
        
        for i, sessao in enumerate(sessoes):
            if i % 2 == 0:
                adicionar_exercicios_padrao(sessao, exercicios_fullbody_a)
            else:
                adicionar_exercicios_padrao(sessao, exercicios_fullbody_b)


def adicionar_exercicios_padrao(sessao, nomes_exercicios):
    """Adiciona exercícios padrão a uma sessão"""
    for ordem, nome_exercicio in enumerate(nomes_exercicios, 1):
        try:
            exercicio = Exercicio.objects.get(nome__icontains=nome_exercicio)
        except Exercicio.DoesNotExist:
            # Se não encontrar, criar um exercício genérico
            exercicio = Exercicio.objects.create(
                nome=nome_exercicio,
                grupo_muscular='OUTROS',
                ativo=True
            )
        
        ExercicioSessao.objects.create(
            exercicio=exercicio,
            sessao=sessao,
            ordem=ordem,
            series=3,
            reps_por_serie=[10, 8, 8],
            pausa_segundos=60
        )

def calcular_volume_semanal(aluno, semanas=8):
    """Calcula o volume de carga por semana para um aluno"""
    from django.db.models import Sum
    from datetime import timedelta
    
    volume_por_semana = {}
    
    # Buscar sets realizados
    sets = SetRealizado.objects.filter(
        exercicio_sessao__sessao__mesociclo__aluno=aluno,
        realizado=True
    ).order_by('semana')
    
    # Agrupar por semana
    for set_item in sets:
        semana = set_item.semana
        if semana not in volume_por_semana:
            volume_por_semana[semana] = 0
        
        if set_item.volume:
            volume_por_semana[semana] += set_item.volume
    
    # Ordenar por semana
    return dict(sorted(volume_por_semana.items()))

def calcular_carga_media_exercicio(exercicio_sessao, semanas=4):
    """Calcula a carga média de um exercício nas últimas semanas"""
    sets = SetRealizado.objects.filter(
        exercicio_sessao=exercicio_sessao,
        realizado=True
    ).order_by('-semana')[:semanas * exercicio_sessao.series]
    
    if sets:
        total_carga = sum(s.carga_kg or 0 for s in sets)
        return total_carga / len(sets)
    return 0