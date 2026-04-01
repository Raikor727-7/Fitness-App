from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Alunos
    path('alunos/', views.lista_alunos, name='lista_alunos'),
    path('alunos/novo/', views.criar_aluno, name='criar_aluno'),
    path('alunos/<int:pk>/', views.detalhe_aluno, name='detalhe_aluno'),
    path('alunos/<int:pk>/editar/', views.editar_aluno, name='editar_aluno'),
    path('alunos/<int:pk>/excluir/', views.excluir_aluno, name='excluir_aluno'),
    
    # Avaliações
    path('alunos/<int:aluno_id>/avaliacoes/nova/', views.criar_avaliacao, name='criar_avaliacao'),
    path('avaliacoes/<int:pk>/editar/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliacoes/<int:pk>/excluir/', views.excluir_avaliacao, name='excluir_avaliacao'),
    
    # IET
    path('alunos/<int:aluno_id>/iet/novo/', views.criar_iet, name='criar_iet'),
    path('iet/<int:pk>/editar/', views.editar_iet, name='editar_iet'),
    path('iet/<int:pk>/excluir/', views.excluir_iet, name='excluir_iet'),
    
    # Mesociclos
    path('alunos/<int:aluno_id>/mesociclos/novo/', views.criar_mesociclo, name='criar_mesociclo'),
    path('mesociclos/<int:pk>/', views.detalhe_mesociclo, name='detalhe_mesociclo'),
    path('mesociclos/<int:pk>/editar/', views.editar_mesociclo, name='editar_mesociclo'),
    
    # Sessões de treino
    path('sessoes/<int:pk>/', views.detalhe_sessao, name='detalhe_sessao'),
    path('sessoes/<int:sessao_id>/exercicios/adicionar/', views.adicionar_exercicio_sessao, name='adicionar_exercicio_sessao'),
    path('exercicios-sessao/<int:pk>/remover/', views.remover_exercicio_sessao, name='remover_exercicio_sessao'),
    
    # Registro de treino
    path('treino/dia/', views.treino_dia, name='treino_dia'),
    path('treino/salvar-serie/', views.salvar_serie, name='salvar_serie'),
    path('treino/salvar-endurance/', views.salvar_treino_endurance, name='salvar_treino_endurance'),
    
    # Endurance
    path('alunos/<int:aluno_id>/endurance/', views.lista_endurance, name='lista_endurance'),
    path('endurance/novo/', views.criar_treino_endurance, name='criar_treino_endurance'),
    
    # API endpoints (para AJAX)
    path('api/graficos/<int:aluno_id>/', views.dados_graficos, name='dados_graficos'),
    path('api/buscar-exercicios/', views.buscar_exercicios, name='buscar_exercicios'),
    path('api/mesociclo/<int:mesociclo_id>/treinos/', views.get_treinos_semana, name='get_treinos_semana'),
    path('api/exercicio-sessao/<int:pk>/', views.api_exercicio_sessao_detalhe, name='api_exercicio_sessao_detalhe'),
    path('api/exercicio-sessao/salvar/', views.api_exercicio_sessao_salvar, name='api_exercicio_sessao_salvar'),
    path('api/exercicio-sessao/<int:pk>/remover/', views.api_exercicio_sessao_remover, name='api_exercicio_sessao_remover'),
    # Adicione esta linha na seção de API endpoints
    path('api/exercicio/<int:pk>/', views.api_exercicio_detalhe, name='api_exercicio_detalhe'),
    
    # Exercícios (admin)
    path('exercicios/', views.lista_exercicios, name='lista_exercicios'),
    path('exercicios/importar/', views.importar_exercicios, name='importar_exercicios'),
    path('exercicios-sessao/<int:pk>/editar/', views.editar_exercicio_sessao, name='editar_exercicio_sessao'),
    path('api/graficos/geral/', views.dados_graficos_geral, name='dados_graficos_geral'),
    
]