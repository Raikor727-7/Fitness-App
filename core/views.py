from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
import openpyxl
from django.core.files.storage import default_storage
import os
from django.db.models import Avg

from .models import (
    Aluno, Avaliacao, IET, Mesociclo, Sessao, 
    Exercicio, ExercicioSessao, SetRealizado, TreinoEndurance
)
from .forms import (
    AlunoForm, AvaliacaoForm, IETForm, MesocicloForm,
    ExercicioSessaoForm, SetRealizadoForm, TreinoEnduranceForm
)
from .calculations import calcular_treino_automatico, calcular_volume_semanal
from django.core.paginator import Paginator

@login_required
def dashboard(request):
    """Dashboard principal com gráficos e resumos"""
    context = {
        'total_alunos': Aluno.objects.count(),
        'treinos_hoje': SetRealizado.objects.filter(data=timezone.now().date()).count(),
        'avaliacoes_mes': Avaliacao.objects.filter(data__month=timezone.now().month).count(),
        'alunos_recentes': Aluno.objects.order_by('-data_cadastro')[:5],
    }
    return render(request, 'dashboard.html', context)

@login_required
def lista_alunos(request):
    """Lista todos os alunos"""
    alunos = Aluno.objects.all().order_by('nome')
    return render(request, 'alunos/lista.html', {'alunos': alunos})

@login_required
def criar_aluno(request):
    """Cadastra um novo aluno"""
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f'Aluno {aluno.nome} cadastrado com sucesso!')
            return redirect('detalhe_aluno', pk=aluno.pk)
    else:
        form = AlunoForm()
    
    # Adicionar volta_url para o template
    return render(request, 'alunos/form.html', {
        'form': form, 
        'titulo': 'Novo Aluno',
        'volta_url': 'lista_alunos'  # Voltar para lista de alunos
    })

@login_required
def editar_aluno(request, pk):
    """Edita dados do aluno"""
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('detalhe_aluno', pk=aluno.pk)
    else:
        form = AlunoForm(instance=aluno)
    
    return render(request, 'alunos/form.html', {
        'form': form, 
        'titulo': 'Editar Aluno',
        'volta_url': 'detalhe_aluno',
        'volta_id': aluno.pk
    })

@login_required
def detalhe_aluno(request, pk):
    """Exibe detalhes do aluno com histórico"""
    aluno = get_object_or_404(Aluno, pk=pk)
    avaliacoes = aluno.avaliacoes.all().order_by('-data')[:10]
    testes_iet = aluno.testes_iet.all().order_by('-data')[:5]
    mesociclos = aluno.mesociclos.all().order_by('-data_inicio')  # Mostrar todos, não só ativos
    
    context = {
        'aluno': aluno,
        'avaliacoes': avaliacoes,
        'testes_iet': testes_iet,
        'mesociclos': mesociclos,
    }
    return render(request, 'alunos/detalhe.html', context)

@login_required
def excluir_aluno(request, pk):
    """Exclui um aluno"""
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        nome = aluno.nome
        aluno.delete()
        messages.success(request, f'Aluno {nome} excluído com sucesso!')
        return redirect('lista_alunos')
    return render(request, 'alunos/confirmar_exclusao.html', {'aluno': aluno})

@login_required
def criar_avaliacao(request, aluno_id):
    """Cria uma nova avaliação para o aluno"""
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.aluno = aluno
            avaliacao.save()
            messages.success(request, 'Avaliação cadastrada com sucesso!')
            return redirect('detalhe_aluno', pk=aluno.pk)
    else:
        form = AvaliacaoForm()
    
    context = {
        'form': form, 
        'aluno': aluno, 
        'titulo': 'Nova Avaliação',
        'icone': 'clipboard-data'
    }
    return render(request, 'avaliacoes/form.html', context)

@login_required
def editar_avaliacao(request, pk):
    """Edita uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avaliação atualizada com sucesso!')
            return redirect('detalhe_aluno', pk=avaliacao.aluno.pk)
    else:
        form = AvaliacaoForm(instance=avaliacao)
    return render(request, 'avaliacoes/form.html', {
        'form': form,
        'aluno': avaliacao.aluno,
        'titulo': 'Editar Avaliação'
    })

@login_required
def excluir_avaliacao(request, pk):
    """Exclui uma avaliação"""
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    aluno_id = avaliacao.aluno.id
    if request.method == 'POST':
        avaliacao.delete()
        messages.success(request, 'Avaliação excluída com sucesso!')
        return redirect('detalhe_aluno', pk=aluno_id)
    return render(request, 'avaliacoes/confirmar_exclusao.html', {'avaliacao': avaliacao})

@login_required
def criar_iet(request, aluno_id):
    """Cria um novo teste IET para o aluno"""
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    if request.method == 'POST':
        form = IETForm(request.POST)
        if form.is_valid():
            iet = form.save(commit=False)
            iet.aluno = aluno
            iet.save()
            messages.success(request, 'Teste IET cadastrado com sucesso!')
            return redirect('detalhe_aluno', pk=aluno.pk)
    else:
        form = IETForm()
    
    context = {
        'form': form, 
        'aluno': aluno, 
        'titulo': 'Novo Teste IET',
        'icone': 'graph-up'
    }
    return render(request, 'iet/form.html', context)

@login_required
def editar_iet(request, pk):
    """Edita um teste IET"""
    iet = get_object_or_404(IET, pk=pk)
    if request.method == 'POST':
        form = IETForm(request.POST, instance=iet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teste IET atualizado com sucesso!')
            return redirect('detalhe_aluno', pk=iet.aluno.pk)
    else:
        form = IETForm(instance=iet)
    
    context = {
        'form': form,
        'aluno': iet.aluno,
        'titulo': 'Editar Teste IET',
        'icone': 'graph-up'
    }
    return render(request, 'iet/form.html', context)

@login_required
def excluir_iet(request, pk):
    """Exclui um teste IET"""
    iet = get_object_or_404(IET, pk=pk)
    aluno_id = iet.aluno.id
    if request.method == 'POST':
        iet.delete()
        messages.success(request, 'Teste IET excluído com sucesso!')
        return redirect('detalhe_aluno', pk=aluno_id)
    return render(request, 'iet/confirmar_exclusao.html', {'iet': iet})

@login_required
def criar_mesociclo(request, aluno_id):
    """Cria um novo mesociclo e gera os treinos automaticamente"""
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    if request.method == 'POST':
        form = MesocicloForm(request.POST)
        if form.is_valid():
            mesociclo = form.save(commit=False)
            mesociclo.aluno = aluno
            mesociclo.ativo = True  # Garantir que está ativo
            mesociclo.save()
            
            # Desativar mesociclos anteriores
            Mesociclo.objects.filter(aluno=aluno, ativo=True).exclude(pk=mesociclo.pk).update(ativo=False)
            
            # Gerar treinos automaticamente
            from .calculations import calcular_treino_automatico
            calcular_treino_automatico(mesociclo)
            
            messages.success(request, 'Mesociclo criado e treinos gerados automaticamente!')
            return redirect('detalhe_mesociclo', pk=mesociclo.pk)
    else:
        form = MesocicloForm()
    
    context = {
        'form': form,
        'aluno': aluno,
        'titulo': 'Novo Mesociclo',
        'icone': 'calendar-week'
    }
    return render(request, 'mesociclos/form.html', context)

@login_required
def editar_mesociclo(request, pk):
    """Edita um mesociclo"""
    mesociclo = get_object_or_404(Mesociclo, pk=pk)
    if request.method == 'POST':
        form = MesocicloForm(request.POST, instance=mesociclo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesociclo atualizado com sucesso!')
            return redirect('detalhe_mesociclo', pk=mesociclo.pk)
    else:
        form = MesocicloForm(instance=mesociclo)
    
    context = {
        'form': form,
        'aluno': mesociclo.aluno,
        'titulo': 'Editar Mesociclo',
        'icone': 'calendar-week'
    }
    return render(request, 'mesociclos/form.html', context)

@login_required
def detalhe_mesociclo(request, pk):
    """Exibe detalhes do mesociclo com todas as sessões"""
    mesociclo = get_object_or_404(Mesociclo, pk=pk)
    sessoes = mesociclo.sessoes.all().order_by('ordem')
    todos_exercicios = Exercicio.objects.filter(ativo=True).order_by('grupo_muscular', 'nome')
    
    context = {
        'mesociclo': mesociclo,
        'sessoes': sessoes,
        'todos_exercicios': todos_exercicios,
    }
    return render(request, 'mesociclos/detalhe.html', context)

@login_required
def detalhe_sessao(request, pk):
    """Exibe detalhes de uma sessão"""
    sessao = get_object_or_404(Sessao, pk=pk)
    exercicios = sessao.exercicios_sessao.all().order_by('ordem')
    return render(request, 'sessoes/detalhe.html', {
        'sessao': sessao,
        'exercicios': exercicios
    })

@login_required
def adicionar_exercicio_sessao(request, sessao_id):
    """Adiciona um exercício a uma sessão"""
    sessao = get_object_or_404(Sessao, pk=sessao_id)
    
    if request.method == 'POST':
        form = ExercicioSessaoForm(request.POST)
        if form.is_valid():
            exercicio_sessao = form.save(commit=False)
            exercicio_sessao.sessao = sessao
            exercicio_sessao.save()
            messages.success(request, 'Exercício adicionado com sucesso!')
            return redirect('detalhe_mesociclo', pk=sessao.mesociclo.id)
    else:
        form = ExercicioSessaoForm(initial={'ordem': sessao.exercicios_sessao.count() + 1})
    
    return render(request, 'sessoes/adicionar_exercicio.html', {
        'form': form,
        'sessao': sessao
    })

@login_required
def remover_exercicio_sessao(request, pk):
    """Remove um exercício de uma sessão"""
    exercicio_sessao = get_object_or_404(ExercicioSessao, pk=pk)
    mesociclo_id = exercicio_sessao.sessao.mesociclo.id
    if request.method == 'POST':
        exercicio_sessao.delete()
        messages.success(request, 'Exercício removido com sucesso!')
        return redirect('detalhe_mesociclo', pk=mesociclo_id)
    return render(request, 'sessoes/confirmar_remocao.html', {'exercicio_sessao': exercicio_sessao})

@login_required
def treino_dia(request):
    """Tela de registro de treino do dia"""
    hoje = timezone.now().date()
    dia_semana = hoje.isoweekday()  # 1=Segunda, 7=Domingo
    
    aluno_id = request.GET.get('aluno_id')
    if not aluno_id:
        alunos = Aluno.objects.all()
        return render(request, 'treino/selecionar_aluno.html', {'alunos': alunos})
    
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    mesociclo_ativo = aluno.mesociclos.filter(ativo=True).first()
    
    if not mesociclo_ativo:
        messages.warning(request, 'Aluno não possui um mesociclo ativo.')
        return redirect('detalhe_aluno', pk=aluno.pk)
    
    # Calcular semana atual do mesociclo
    semanas_passadas = (hoje - mesociclo_ativo.data_inicio).days // 7
    semana_atual = semanas_passadas + 1
    
    # Limitar à semanas planejadas
    if semana_atual > mesociclo_ativo.semanas_planejadas:
        messages.info(request, 'Mesociclo finalizado. Crie um novo mesociclo.')
        return redirect('detalhe_aluno', pk=aluno.pk)
    
    sessoes = list(mesociclo_ativo.sessoes.all().order_by('ordem'))
    num_sessoes = len(sessoes)
    sessao_do_dia = None
    
    # Mapeamento para diferentes frequências
    if num_sessoes == 2:  # 2x por semana
        mapa = {1: 0, 4: 1}  # Segunda e Quinta
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    elif num_sessoes == 3:  # 3x por semana
        mapa = {1: 0, 3: 1, 5: 2}  # Segunda, Quarta, Sexta
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    elif num_sessoes == 4:  # 4x por semana
        mapa = {1: 0, 2: 1, 4: 2, 5: 3}  # Seg, Ter, Qui, Sex
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    elif num_sessoes == 5:  # 5x por semana
        mapa = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}  # Segunda a Sexta
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    elif num_sessoes == 6:  # 6x por semana
        mapa = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}  # Segunda a Sábado
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    elif num_sessoes == 7:  # 7x por semana
        mapa = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}  # Todos os dias
        if dia_semana in mapa and mapa[dia_semana] < num_sessoes:
            sessao_do_dia = sessoes[mapa[dia_semana]]
    
    if not sessao_do_dia:
        messages.info(request, 'Hoje não há treino programado.')
        return redirect('detalhe_aluno', pk=aluno.pk)
    
    exercicios_sessao = sessao_do_dia.exercicios_sessao.all().order_by('ordem')
    
    # Otimizar: calcular carga média com uma única query
    for ex_sessao in exercicios_sessao:
        # Usar annotate para calcular carga média
        carga_media = SetRealizado.objects.filter(
            exercicio_sessao=ex_sessao,
            realizado=True
        ).aggregate(avg_carga=Avg('carga_kg'))['avg_carga']
        
        ex_sessao.carga_media = round(carga_media, 1) if carga_media else 0
        
        # Buscar últimos registros (limitado)
        ultimos_registros = SetRealizado.objects.filter(
            exercicio_sessao=ex_sessao
        ).order_by('-data')[:3]
        ex_sessao.ultimas_cargas = ultimos_registros
    
    context = {
        'aluno': aluno,
        'sessao': sessao_do_dia,
        'exercicios': exercicios_sessao,
        'hoje': hoje,
        'semana': semana_atual,
        'total_semanas': mesociclo_ativo.semanas_planejadas,
    }
    
    return render(request, 'treino/dia.html', context)

@login_required
def salvar_serie(request):
    """Salva uma série realizada via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            set_realizado = SetRealizado.objects.create(
                exercicio_sessao_id=data['exercicio_sessao_id'],
                semana=data['semana'],
                data=data['data'],
                numero_serie=data['numero_serie'],
                carga_kg=data.get('carga_kg'),
                realizado=data.get('realizado', True),
                observacoes=data.get('observacoes', '')
            )
            
            return JsonResponse({
                'success': True,
                'id': set_realizado.id,
                'carga_media': set_realizado.carga_media,
                'volume': set_realizado.volume
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def salvar_treino_endurance(request):
    """Salva um treino de endurance"""
    if request.method == 'POST':
        form = TreinoEnduranceForm(request.POST)
        if form.is_valid():
            treino = form.save(commit=False)
            treino.aluno_id = request.POST.get('aluno_id')
            treino.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def lista_endurance(request, aluno_id):
    """Lista treinos de endurance do aluno"""
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    treinos = aluno.treinos_endurance.all().order_by('-semana', '-dia_semana')
    return render(request, 'endurance/lista.html', {
        'aluno': aluno,
        'treinos': treinos
    })

@login_required
def criar_treino_endurance(request):
    """Cria um novo treino de endurance"""
    if request.method == 'POST':
        form = TreinoEnduranceForm(request.POST)
        if form.is_valid():
            treino = form.save(commit=False)
            treino.aluno_id = request.POST.get('aluno_id')
            treino.save()
            messages.success(request, 'Treino de endurance cadastrado com sucesso!')
            return redirect('lista_endurance', aluno_id=treino.aluno.id)
    else:
        form = TreinoEnduranceForm()
    return render(request, 'endurance/form.html', {'form': form})

@login_required
def dados_graficos(request, aluno_id):
    """Retorna dados para os gráficos do dashboard do aluno"""
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # Dados de avaliações - manter todas as listas alinhadas
    avaliacoes = aluno.avaliacoes.all().order_by('data')
    dados_avaliacoes = {
        'datas': [],
        'pesos': [],
        'percentuais': [],
        'imcs': []
    }
    
    for a in avaliacoes:
        dados_avaliacoes['datas'].append(a.data.strftime('%d/%m/%Y'))
        dados_avaliacoes['pesos'].append(float(a.massa_corporal) if a.massa_corporal else None)
        dados_avaliacoes['percentuais'].append(a.percentual_gordura if a.percentual_gordura is not None else None)
        dados_avaliacoes['imcs'].append(a.imc if a.imc is not None else None)
    
    # Dados de IET - manter listas alinhadas
    iets = aluno.testes_iet.all().order_by('data')
    dados_iet = {
        'datas': [],
        'vo2_max': []
    }
    
    for i in iets:
        dados_iet['datas'].append(i.data.strftime('%d/%m/%Y'))
        dados_iet['vo2_max'].append(i.vo2_max if i.vo2_max is not None else None)
    
    # Dados de volume semanal
    volume_semanal = calcular_volume_semanal(aluno)
    
    return JsonResponse({
        'avaliacoes': dados_avaliacoes,
        'iet': dados_iet,
        'volume_semanal': volume_semanal
    })

@login_required
def dados_graficos_geral(request):
    """Retorna dados agregados de todos os alunos para o dashboard"""
    alunos = Aluno.objects.all()
    
    # Dados agregados
    dados_agregados = {
        'labels': [],
        'pesos_medios': [],
        'percentuais_medios': [],
        'vo2_medios': []
    }
    
    # Encontrar o maior número de avaliações
    max_avaliacoes = 0
    for aluno in alunos:
        max_avaliacoes = max(max_avaliacoes, aluno.avaliacoes.count())
    
    # Para cada posição (mês), calcular média
    for i in range(max_avaliacoes):
        soma_peso = 0
        soma_percentual = 0
        count_peso = 0
        count_percentual = 0
        data_exemplo = None
        
        for aluno in alunos:
            avaliacoes = aluno.avaliacoes.all().order_by('data')
            if i < len(avaliacoes):
                aval = avaliacoes[i]
                if aval.massa_corporal:
                    soma_peso += float(aval.massa_corporal)
                    count_peso += 1
                if aval.percentual_gordura:
                    soma_percentual += aval.percentual_gordura
                    count_percentual += 1
                if not data_exemplo:
                    data_exemplo = aval.data.strftime('%d/%m/%Y')
        
        if data_exemplo:
            dados_agregados['labels'].append(data_exemplo)
            dados_agregados['pesos_medios'].append(
                round(soma_peso / count_peso, 1) if count_peso > 0 else None
            )
            dados_agregados['percentuais_medios'].append(
                round(soma_percentual / count_percentual, 1) if count_percentual > 0 else None
            )
    
    return JsonResponse(dados_agregados)

@login_required
def buscar_exercicios(request):
    """Busca exercícios por nome"""
    query = request.GET.get('q', '')
    if query:
        exercicios = Exercicio.objects.filter(nome__icontains=query, ativo=True)[:20]
        data = [{'id': e.id, 'nome': e.nome, 'grupo': e.get_grupo_muscular_display()} for e in exercicios]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_treinos_semana(request, mesociclo_id):
    """Retorna os treinos da semana para um mesociclo"""
    mesociclo = get_object_or_404(Mesociclo, pk=mesociclo_id)
    semana = int(request.GET.get('semana', 1))
    
    sets = SetRealizado.objects.filter(
        exercicio_sessao__sessao__mesociclo=mesociclo,
        semana=semana
    )
    
    data = []
    for set_item in sets:
        data.append({
            'exercicio': set_item.exercicio_sessao.exercicio.nome,
            'serie': set_item.numero_serie,
            'carga': float(set_item.carga_kg) if set_item.carga_kg else None,
            'realizado': set_item.realizado
        })
    
    return JsonResponse(data, safe=False)

@login_required
def lista_exercicios(request):
    """Lista todos os exercícios do banco"""
    exercicios = Exercicio.objects.filter(ativo=True).order_by('grupo_muscular', 'nome')
    
    # Filtrar por busca
    query = request.GET.get('q')
    if query:
        exercicios = exercicios.filter(nome__icontains=query)
    
    # Filtrar por grupo
    grupo = request.GET.get('grupo')
    if grupo:
        exercicios = exercicios.filter(grupo_muscular=grupo)
    
    # Paginação
    paginator = Paginator(exercicios, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    grupos = Exercicio.GRUPOS_MUSCULARES
    
    return render(request, 'exercicios/lista.html', {
        'exercicios': page_obj,
        'grupos': grupos
    })

@login_required
def editar_exercicio_sessao(request, pk):
    """Edita um exercício da sessão"""
    exercicio_sessao = get_object_or_404(ExercicioSessao, pk=pk)
    if request.method == 'POST':
        form = ExercicioSessaoForm(request.POST, instance=exercicio_sessao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exercício atualizado com sucesso!')
            return redirect('detalhe_mesociclo', pk=exercicio_sessao.sessao.mesociclo.id)
    else:
        form = ExercicioSessaoForm(instance=exercicio_sessao)
    
    return render(request, 'sessoes/editar_exercicio.html', {
        'form': form,
        'exercicio_sessao': exercicio_sessao
    })

@login_required
def importar_exercicios(request):
    """Importa exercícios de um arquivo Excel"""
    if request.method == 'POST' and request.FILES.get('arquivo'):
        arquivo = request.FILES['arquivo']
        
        # Verificar extensão
        if not arquivo.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Formato de arquivo inválido. Use .xlsx ou .xls')
            return redirect('importar_exercicios')
        
        try:
            # Carregar workbook
            wb = openpyxl.load_workbook(arquivo)
            ws = wb.active
            
            # Mapeamento de grupos musculares válidos
            grupos_validos = dict(Exercicio.GRUPOS_MUSCULARES)
            
            contador = 0
            erros = []
            
            # Pular cabeçalho (primeira linha)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row or not row[0]:
                    continue
                
                nome = str(row[0]).strip()
                grupo = str(row[1]).strip().upper() if row[1] else 'OUTROS'
                descricao = str(row[2]).strip() if len(row) > 2 and row[2] else ''
                
                # Validar grupo
                if grupo not in grupos_validos:
                    grupo = 'OUTROS'
                
                # Criar ou atualizar exercício
                exercicio, created = Exercicio.objects.update_or_create(
                    nome=nome,
                    defaults={
                        'grupo_muscular': grupo,
                        'descricao': descricao,
                        'ativo': True
                    }
                )
                
                if created:
                    contador += 1
            
            if contador > 0:
                messages.success(request, f'{contador} exercícios importados com sucesso!')
            else:
                messages.info(request, 'Nenhum novo exercício encontrado para importar.')
                
        except Exception as e:
            messages.error(request, f'Erro ao importar: {str(e)}')
        
        return redirect('lista_exercicios')
    
    return render(request, 'exercicios/importar.html')

@login_required
def api_exercicio_sessao_detalhe(request, pk):
    """Retorna detalhes de um ExercicioSessao para edição"""
    try:
        exercicio_sessao = get_object_or_404(ExercicioSessao, pk=pk)
        data = {
            'id': exercicio_sessao.id,
            'sessao': exercicio_sessao.sessao.id,
            'exercicio': exercicio_sessao.exercicio.id,
            'ordem': exercicio_sessao.ordem,
            'series': exercicio_sessao.series,
            'reps_por_serie': exercicio_sessao.reps_por_serie,
            'pausa_segundos': exercicio_sessao.pausa_segundos,
            'observacoes': exercicio_sessao.observacoes,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def api_exercicio_sessao_salvar(request):
    """Salva um ExercicioSessao (cria ou atualiza)"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            exercicio_sessao_id = data.get('exercicio_sessao_id')
            sessao_id = data.get('sessao_id')
            exercicio_id = data.get('exercicio_id')
            ordem = data.get('ordem')
            series = data.get('series')
            reps_por_serie = data.get('reps_por_serie')
            pausa_segundos = data.get('pausa_segundos')
            observacoes = data.get('observacoes', '')
            
            if not all([sessao_id, exercicio_id, ordem, series, reps_por_serie, pausa_segundos]):
                return JsonResponse({'success': False, 'error': 'Campos obrigatórios faltando'})
            
            try:
                if isinstance(reps_por_serie, str):
                    reps_list = json.loads(reps_por_serie)
                else:
                    reps_list = reps_por_serie
                if not isinstance(reps_list, list):
                    raise ValueError
            except:
                return JsonResponse({'success': False, 'error': 'Formato de repetições inválido'})
            
            if exercicio_sessao_id and exercicio_sessao_id != '':
                exercicio_sessao = get_object_or_404(ExercicioSessao, pk=exercicio_sessao_id)
                exercicio_sessao.exercicio_id = exercicio_id
                exercicio_sessao.ordem = int(ordem)
                exercicio_sessao.series = int(series)
                exercicio_sessao.reps_por_serie = reps_list
                exercicio_sessao.pausa_segundos = int(pausa_segundos)
                exercicio_sessao.observacoes = observacoes
                exercicio_sessao.save()
            else:
                if ExercicioSessao.objects.filter(sessao_id=sessao_id, exercicio_id=exercicio_id).exists():
                    return JsonResponse({'success': False, 'error': 'Este exercício já está nesta sessão'})
                
                exercicio_sessao = ExercicioSessao.objects.create(
                    sessao_id=sessao_id,
                    exercicio_id=exercicio_id,
                    ordem=int(ordem),
                    series=int(series),
                    reps_por_serie=reps_list,
                    pausa_segundos=int(pausa_segundos),
                    observacoes=observacoes
                )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def api_exercicio_sessao_remover(request, pk):
    """Remove um ExercicioSessao"""
    if request.method == 'POST':
        try:
            exercicio_sessao = get_object_or_404(ExercicioSessao, pk=pk)
            exercicio_sessao.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def api_exercicio_detalhe(request, pk):
    """Retorna detalhes de um exercício via API"""
    try:
        exercicio = get_object_or_404(Exercicio, pk=pk)
        data = {
            'id': exercicio.id,
            'nome': exercicio.nome,
            'grupo_muscular': exercicio.get_grupo_muscular_display(),
            'descricao': exercicio.descricao,
            'video_url': exercicio.video_url,
            'imagem_url': exercicio.imagem_url,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)