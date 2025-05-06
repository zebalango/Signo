
from calendar import c
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.http import HttpResponse, Http404 # type: ignore
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas # type: ignore
from django.db.models import Count
from .models import Aluno, Disciplina, Nota, Professor, Curso, AnoLectivo, Frequencia
from datetime import datetime
from django.shortcuts import render, redirect # type: ignore
from .forms import AlunoForm,DisciplinaForm, NotaForm
from django.contrib import messages # type: ignore
from django.contrib import auth # type: ignore
from django.contrib.messages import constants # type: ignore
from django.core.paginator import Paginator # type: ignore

# Continuar no Proximo dia ao Abrir o Codigo
def alunos_por_curso(request):
    cursos = Curso.objects.prefetch_related('alunos').all()
    return render(request, 'notas/alunos_por_curso.html', {'cursos': cursos})

def termos(request):
    return render (request, 'notas/termos_politica.html')

def buscar(request):
    query = request.GET.get('q')
    resultados = []
    if query:
        resultados = Aluno.objects.filter(classe=query)
    return render(request, 'notas/buscar_resultados.html', {'resultados': resultados, 'query': query})

def is_admin(user):
    return user.is_superuser
#@user_passes_test(is_admin)
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Coordenador').exists())
def admin_dashboard(request):
    total_alunos = Aluno.objects.count()
    total_professores = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_disciplinas = Disciplina.objects.count()
    total_notas = Nota.objects.count()
    ultimos_alunos = Aluno.objects.order_by('-id')[:2]
    # Gráfico: notas por disciplina
    notas_por_disciplina = Nota.objects.values('disciplina__nome').annotate(total=Count('id'))
    labels = [item['disciplina__nome'] for item in notas_por_disciplina]
    data = [item['total'] for item in notas_por_disciplina]
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_disciplinas': total_disciplinas,
        'total_notas': total_notas,
        'ultimos_alunos': ultimos_alunos,
        'labels': labels,
        'data': data, 
    }

    return render(request, 'admin_dashboard.html', context)

def boletim_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    notas_queryset = aluno.nota_set.select_related('disciplina').all()
    
    paginator = Paginator(notas_queryset, 2)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    media = aluno.media_notas()
    return render(request, 'notas/boletim.html', {'aluno': aluno,'notas': page_obj,'media': media})

def alunos_do_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    alunos = Aluno.objects.filter(curso=curso)
    return render(request, 'notas/alunos_do_curso.html', {
        'curso': curso,
        'alunos': alunos
    })

def filtrar_alunos_por_curso(request):
    cursos = Curso.objects.all()
    curso_selecionado = request.GET.get('curso')
    alunos = None

    if curso_selecionado:
        alunos = Aluno.objects.filter(curso_id=curso_selecionado)

    return render(request, 'notas/filtro_alunos.html', {
        'cursos': cursos,
        'alunos': alunos,
        'curso_selecionado': int(curso_selecionado) if curso_selecionado else None
    })

#Cadastrar Dados 
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redireciona para a página de login após o registro
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('home')
        messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
        return redirect('login')
def logout_view(request):
    logout(request)
    return redirect('login')  

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password1')
        confirmar_senha = request.POST.get('password2')
        if not password == confirmar_senha:
            return redirect('register')
        if len(password) < 6:
            return redirect('register')
        users = User.objects.filter(username=username)
        if users.exists():
            return redirect('login')
        User.objects.create_user(
            username=username,
            password=password
        )
        return redirect('login')
def cadastrar_aluno(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        matricula = request.POST.get('matricula')
        data_nascimento = request.POST.get('data')
        curso_id = request.POST.get('curso_id')
        curso = Curso.objects.get(id=curso_id) 
        aluno = Aluno.objects.create(nome=nome, matricula=matricula, data=data_nascimento) 
        return redirect('sucesso')  # Redireciona para uma página de sucesso
    cursos = Curso.objects.all()
    return render(request, 'cadastrar_aluno.html', {'cursos': cursos})
@login_required
def home(request):
    alunos = Aluno.objects.all()
    return render(request, 'home.html', {'alunos': alunos})

def aluno_notas(request, id):
    aluno = Aluno.objects.get(aluno_id=id)
    
    if aluno.user != request.user:
        raise Http404()
    if request.method == 'GET':
        notas = Nota.objects.filter(aluno=aluno)
        
    return render(request, 'notas/aluno_notas.html/{id}', {'aluno': aluno, 'notas': notas})

# Exibe todos os anos letivos
def anos_letivos(request):
    anos = AnoLectivo.objects.all()
    return render(request, 'notas/anos_letivos.html', {'anos': anos})
# Exibe as disciplinas de um curso///////////////////////////////////////////////////////////////////////////////
def disciplinas_curso(request, curso_id):
    disciplinas_queryset = Disciplina.objects.filter(curso_id=curso_id)
    paginator = Paginator(disciplinas_queryset, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'notas/lista_disciplinas.html/', {'disciplinas': page_obj,'curso': curso_id})

# Função para editar uma disciplina
@login_required
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            return redirect('cursos') 
    else:
        form = DisciplinaForm(instance=disciplina)
    return render(request, 'notas/form_disciplina.html', {'form': form})
# Função para excluir uma disciplina
def excluir_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    if request.method == 'POST':
        disciplina.delete()
        return redirect('disciplinas_curso')  # Redirecionar para a lista de disciplinas após a exclusão
    return render(request, 'notas/confirmar_exclusao_disciplina.html', {'disciplina': disciplina})
#/////////////////////////////////////FIM DISCIPLINAS///////////////////////////////////////////////////////////

# Exibe a frequência de um aluno em uma disciplina durante um ano letivo
def frequencia_aluno(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    frequencias = Frequencia.objects.filter(aluno=aluno)
    return render(request, 'notas/frequencia_aluno.html', {'aluno': aluno, 'frequencias': frequencias})
# Exibe cursos
@login_required
def cursos(request):
    cursos_queryset = Curso.objects.all().order_by('nome')
    paginator = Paginator(cursos_queryset, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'notas/cursos.html', {'cursos': page_obj })
# Exibe os professores
def professores(request):
    professores = Professor.objects.all()
    return render(request, 'notas/professores.html', {'professores': professores})

#Gera Relatorio em PDF
# relatorio individual
def relatorio_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_notas.pdf"'

    # Criando uma resposta de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_{aluno.nome}.pdf"'

    # Criando o objeto de canvas do ReportLab
    c = canvas.Canvas(response, pagesize=A4)

    # Cabeçalho - Logo, Nome da Escola, etc
    c.setFont('Helvetica', 12)
    c.drawString(30, 770, "Nome da Escola")
    c.drawString(30, 755, f"Relatório do Aluno: {aluno.nome}")
    c.drawString(30, 740, f"Curso: {aluno.curso}")
    c.drawString(30, 725, f"Data de Geração: {datetime.now().strftime('%d/%m/%Y')}")

    # Dados do Aluno
    c.setFont('Helvetica', 10)
    c.drawString(30, 700, f"Nome: {aluno.nome}")
    c.drawString(30, 685, f"Matrícula: {aluno.matricula}")
    c.drawString(30, 670, f"Data de Nascimento: {aluno.data_nascimento.strftime('%d/%m/%Y')}")
    c.drawString(30, 655, f"Curso: {aluno.curso}")

    # Rodapé - Pode incluir informações de rodapé como página ou direitos autorais
    c.setFont('Helvetica', 8)
    c.drawString(30, 20, "Rodapé - Direitos autorais © 2025 Escola X")
    c.drawString(500, 20, f"Página 1")

    # Salvando o PDF
    c.showPage()
    c.save()

    return response
@login_required
def gerar_relatorio(request):
    # Cria um arquivo de resposta em formato PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_notas.pdf"'

    # Cria um objeto canvas para gerar o PDF
    p = canvas.Canvas(response, pagesize=A4)
    
    # Definir fontes e posições
    p.setFont("Helvetica", 12)
    p.drawString(30, 760, "Nome da Escola")
    p.drawString(30, 745, f"Relatório do Aluno:")
    p.drawString(30, 730, f"Curso: ")
    p.drawString(30, 715, f"Data de Impressão: {datetime.now().strftime('%d/%m/%Y')}")
    p.setFont('Helvetica', 15)

    p.drawString(200, 671, "Relatório de Notas dos Alunos")

    # Pega todos os alunos e suas notas
    alunos = Aluno.objects.all()

    y_position = 610
    for aluno in alunos:
        p.drawString(200, y_position, f"Aluno: {aluno.nome} - Nº: {aluno.matricula}")
        y_position -= 15

        notas = Nota.objects.filter(aluno=aluno)
        for nota in notas:
            p.drawString(200, y_position, f"Disciplina: {nota.disciplina.nome} - Nota: {nota.nota}")
            y_position -= 15

        y_position -= 10  # Espaço entre os alunos

        if y_position < 100:  # Se estiver perto do fim da página, cria uma nova página
            p.showPage()
            p.setFont("Helvetica", 12)
            y_position = 730
    # Rodapé - Pode incluir informações de rodapé como página ou direitos autorais
    p.setFont('Helvetica', 10)
    p.drawString(30, 20, "SIGNO - Direitos autorais © 2025 | Programadores José Balango & Ctap | ITSB")
    p.drawString(500, 20, f"Página 1")
    # Finaliza o PDF
    p.showPage()
    p.save()
    return response

def gerar_relatorio_notas(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    notas = Nota.objects.filter(aluno=aluno)
    
    # Criar resposta HTTP com o cabeçalho para gerar o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_notas_{aluno.matricula}.pdf"'
    
    # Criar o objeto PDF
    c = canvas.Canvas(response, pagesize=A4)
    
    # Título
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f'Relatório de Notas - {aluno.nome}')
    
    # Adicionar a tabela de notas
    c.drawString(100, 730, "Disciplina")
    c.drawString(300, 730, "Nota")
    
    y_position = 710
    for nota in notas:
        c.drawString(100, y_position, nota.disciplina.nome)
        c.drawString(300, y_position, str(nota.nota))
        y_position -= 20
    
    # Finalizar o PDF
    c.showPage()
    c.save()
    
    return response
@login_required
def gerar_relatorio_media(request, aluno_id):
    aluno = Aluno.objects.get(id=aluno_id)
    notas = Nota.objects.filter(aluno=aluno)
    # Calcular a média das notas
    if notas:
        media = sum([nota.nota for nota in notas]) / len(notas)
    else:
        media = 0
    # Criar resposta HTTP com o cabeçalho para gerar o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_media_{aluno.matricula}.pdf"'
    
    # Criar o objeto PDF
    c = canvas.Canvas(response, pagesize=A4 )
    
    # Título
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f'Relatório de Média de Notas - {aluno.nome}')
    
    # Tabela de notas e média
    c.drawString(100, 730, "Disciplina")
    c.drawString(300, 730, "Nota")
    
    y_position = 710
    for nota in notas:
        c.drawString(100, y_position, nota.disciplina.nome)
        c.drawString(300, y_position, str(nota.nota))
        y_position -= 20
    
    # Mostrar a média final
    c.drawString(100, y_position - 30, f'Média Final: {media:.2f}')
    
    # Finalizar o PDF
    c.showPage()
    c.save()
    
    return response

def listar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'listar_alunos.html', {'alunos': alunos})

def adicionar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_alunos')
    else:
        form = AlunoForm()
    return render(request, 'cadastrar_aluno.html', {'form': form})

def listar_notas(request):
    notas_queryset = Nota.objects.all().order_by('id')  # ordena se quiser
    paginator = Paginator(notas_queryset, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notas/listar_notas.html', {
        'notas': page_obj
    })
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Coordenador').exists())
def adicionar_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('notas/listar_notas')
    else:
        form = NotaForm()
    return render(request, 'notas/adicionar_nota.html', {'form': form})

def lista_notas(request, aluno_id):
    aluno = get_object_or_404(Aluno, aluno_id=aluno_id)  # Busca o aluno com base no ID
    notas = Nota.objects.filter(aluno=aluno)  # Busca todas as notas associadas ao aluno
    return render(request, 'views/lista_notas.html', {'aluno': aluno, 'notas': notas})
@login_required
def editar_nota(request, pk):
    nota = get_object_or_404(Nota, pk=pk)
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('lista_notas')
    else:
        form = NotaForm(instance=nota)
    return render(request, 'notas/form_nota.html', {'form': form})
# View para criar uma nova nota
def nova_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_notas')
    else:
        form = NotaForm()
    return render(request, 'notas/form_nota.html', {'form': form})
# View para excluir uma nota
@login_required
def excluir_nota(request, pk):
    nota = get_object_or_404(Nota, pk=pk)
    if request.method == 'POST':
        nota.delete()
        return redirect('lista_notas')
    return render(request, 'notas/confirmar_exclusao.html', {'nota': nota})
