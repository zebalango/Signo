from django.db import models

# Representa um ano letivo, como 2023-2024
class AnoLectivo(models.Model):
    ano_inicio = models.IntegerField()
    ano_fim = models.IntegerField()

    def __str__(self):
        return f"{self.ano_inicio}/{self.ano_fim}"

# Representa um curso na instituição
class Curso(models.Model):
    nome = models.CharField(max_length=100)
    duracao = models.IntegerField(help_text="Duração em Trimestres")
    ano_letivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name="cursos")

    def __str__(self):
        return self.nome
# Representa um professor
class Professor(models.Model):
    nome = models.CharField(max_length=100,)
    cpf = models.CharField(max_length=14,verbose_name="Nº", unique=True)  # CPF único do professor
    data_nascimento = models.DateField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nome
# Representa uma disciplina que faz parte de um curso
class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    carga_horaria = models.IntegerField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="disciplinas")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="disciplinas")

    def __str__(self):
        return f"{self.nome} - {self.professor.nome}"

# Representa a frequência de um aluno em uma disciplina durante um ano letivo
class Frequencia(models.Model):
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name="frequencias")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    ano_letivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE)
    presente = models.BooleanField(default=False)
    data = models.DateField()

    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} - {self.data} - {'Presente' if self.presente else 'Ausente'}"

# Representa um aluno
class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    data_nascimento = models.DateField()
    classe = models.IntegerField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="alunos")
    def __str__(self):
        return self.nome
    def media_notas(self):
        notas = self.nota_set.all()
        if notas.exists():
            return sum(n.nota for n in notas) / notas.count()
        return 0
    def situacao_geral(self):
        media = self.media_notas()
        return "Aprovado" if media >= 7.0 else "Reprovado"
class Nota(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    data_registro = models.DateField(auto_now_add=True)
    def __str__(self):
        return f'{self.aluno} - {self.disciplina} - {self.nota}'
    
    def situacao(self):
        return "Aprovado" if self.nota >= 7.0 else "Reprovado"
class Nivel(models.Model):
        nome = models.CharField(max_length=100)
        def __str__(self):
            return self.nome