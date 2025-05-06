from django import forms
from .models import Aluno,Disciplina, Nota

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'matricula','data_nascimento','curso']

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['aluno','disciplina', 'nota']

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome','curso','carga_horaria','professor'] 