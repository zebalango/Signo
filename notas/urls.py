from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    #Preliminares do Sistema!
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.cadastro, name='register'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('cursos/', views.cursos, name='cursos'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('buscar/', views.buscar, name='buscar'),
    #Visualizar notas
    path('notas/<int:aluno_id>/media/', views.boletim_aluno, name='media'),
    path('adionarnotas/', views.adicionar_nota, name='addnota'),
    path('curso/<int:curso_id>/disciplinas/', views.disciplinas_curso, name='disciplinas_curso'),
    #///////////////////////////////////////////////////////////////////////////////////////////////////////
    #Configuração das rotas do Curso e DIsciplinas.
    path('disciplina/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplina/excluir/<int:pk>/', views.excluir_disciplina, name='excluir_disciplina'),
    #Configuração das rotas do Aluno
    path('aluno/<int:aluno_id>/', views.aluno_notas, name='aluno_notas'),
    path('aluno', views.cadastrar_aluno, name='cadastrar'),
    path('aluno/<int:aluno_id>/frequencia/', views.frequencia_aluno, name='frequencia_aluno'),
    path('anos/', views.anos_letivos, name='anos_letivos'),
    #Configuração das rotas de notas
    path('notas/', views.listar_notas, name='notas'),
    path('nova/', views.nova_nota, name='nova_nota'),
    path('editar/<int:pk>/', views.editar_nota, name='editar_nota'),
    path('excluir/<int:pk>/', views.excluir_nota, name='excluir_nota'),
    path('views/notas/<int:aluno_id>/', views.lista_notas, name='lista_notas'), 
    
    path('relatorio/notas/<int:aluno_id>/', views.gerar_relatorio_notas, name='relatorio_notas'),
    path('relatorios/', views.gerar_relatorio, name='gerar_relatorio'),
    
    #Configuração das rotas dos professores
    path('professores/', views.professores, name='professores'),
    
    #Gerar a media
    path('relatorio/media/<int:aluno_id>/', views.gerar_relatorio_media, name='relatorio_media'),
    
    path('aluno/<int:aluno_id>/', views.relatorio_aluno, name='relatorio_aluno'),
    #Visualizar notas
    path('curso/<int:curso_id>/alunos/', views.alunos_do_curso, name='alunos_do_curso'),
    path('filtro/alunos/', views.filtrar_alunos_por_curso, name='filtro_alunos'),
    path('termos/', views.termos , name='termos_politicas'),
    path('alunosporcurso/', views.alunos_por_curso, name='alunos_por_curso'),
]

 