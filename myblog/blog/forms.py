from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, label='Ім\'я')
    email = forms.EmailField(label='Email')
    to = forms.EmailField(label='До')
    comments = forms.CharField(required=False, 
                             widget=forms.Textarea(attrs={'rows': 4}),
                             label='Коментар')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш коментар...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Ваше ім\'я'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email'}),
        }
        labels = {
            'name': 'Ім\'я',
            'email': 'Email',
            'body': 'Коментар'
        }
