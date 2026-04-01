from django import forms
from .models import (
    Aluno, Avaliacao, IET, Mesociclo, 
    ExercicioSessao, SetRealizado, TreinoEndurance
)

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'data_nascimento', 'sexo', 'observacoes', 'objetivos', 'medicamentos']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'objetivos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medicamentos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para todos os campos
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Textarea, forms.Select, forms.DateInput)):
                field.widget.attrs.update({'class': 'form-control'})

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        exclude = ['aluno']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
            'massa_corporal': forms.NumberInput(attrs={'step': '0.01'}),
            'altura': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_torax': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_braco_direito': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_braco_esquerdo': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_cintura': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_quadril': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_coxa_direita': forms.NumberInput(attrs={'step': '0.01'}),
            'circunferencia_coxa_esquerda': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_peitoral': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_axilar_media': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_tricipital': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_subescapular': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_abdominal': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_suprailiaca': forms.NumberInput(attrs={'step': '0.01'}),
            'dobra_coxa': forms.NumberInput(attrs={'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }


class IETForm(forms.ModelForm):
    class Meta:
        model = IET
        exclude = ['aluno']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'velocidade_inicial': forms.NumberInput(attrs={'step': '0.01'}),
            'velocidade_maxima': forms.NumberInput(attrs={'step': '0.01'}),
            'duracao_teste': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }


class MesocicloForm(forms.ModelForm):
    class Meta:
        model = Mesociclo
        exclude = ['aluno']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }


class ExercicioSessaoForm(forms.ModelForm):
    class Meta:
        model = ExercicioSessao
        fields = ['exercicio', 'ordem', 'series', 'reps_por_serie', 'pausa_segundos', 'observacoes']
        widgets = {
            'reps_por_serie': forms.TextInput(attrs={'placeholder': '[10, 8, 8, 6]'}),
        }
    
    def clean_reps_por_serie(self):
        data = self.cleaned_data['reps_por_serie']
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except:
                raise forms.ValidationError('Formato inválido. Use um array JSON como [10, 8, 8, 6]')
        return data


class SetRealizadoForm(forms.ModelForm):
    class Meta:
        model = SetRealizado
        fields = ['carga_kg', 'realizado', 'observacoes']
        widgets = {
            'carga_kg': forms.NumberInput(attrs={'step': '0.5'}),
            'observacoes': forms.TextInput(attrs={'placeholder': 'Ex: Falhou na última repetição'}),
        }


class TreinoEnduranceForm(forms.ModelForm):
    class Meta:
        model = TreinoEndurance
        exclude = ['aluno']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'velocidade_percentual_vmax': forms.NumberInput(attrs={'step': '1'}),
            'tempo_minutos': forms.NumberInput(attrs={'step': '1'}),
            'n_sprints': forms.NumberInput(attrs={'step': '1'}),
            'tempo_sprint': forms.NumberInput(attrs={'step': '1'}),
            'tempo_pausa': forms.NumberInput(attrs={'step': '1'}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }