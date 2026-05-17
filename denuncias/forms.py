from django import forms
from .models import Denuncia

class DenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['titulo', 'categoria', 'descricao', 'cep', 'endereco', 'numero', 'bairro', 'cidade', 'estado', 'foto', 'anonimo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Buraco profundo na pista principal'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Descreva detalhadamente o problema urbano observando riscos...',
                'rows': 4
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_cep',
                'placeholder': '00000-000',
                'maxlength': '9'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_endereco',
                'placeholder': 'Rua, Avenida, etc.'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_numero',
                'placeholder': 'Nº'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_bairro',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_cidade',
                'placeholder': 'Cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-input',
                'id': 'id_estado',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-file-input',
                'id': 'id_foto',
                'accept': 'image/*'
            }),
            'anonimo': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }


class GestaoForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['status', 'resposta_gestor']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resposta_gestor': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Escreva uma nota sobre a resolução ou andamento da ocorrência...',
            }),
        }
