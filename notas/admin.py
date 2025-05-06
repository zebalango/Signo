from django.contrib import admin
from .models import Aluno, Disciplina, Nivel,Nota, Professor, Curso, AnoLectivo, Frequencia

admin.site.register(Aluno)
admin.site.register(Disciplina)
admin.site.register(Nota)
admin.site.register(Professor)
admin.site.register(Curso)
admin.site.register(AnoLectivo)
admin.site.register(Frequencia)
admin.site.register(Nivel)


