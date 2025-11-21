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


class EmailSubscribeForm(forms.Form):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введіть email',
            'class': 'form-control',
            'required': 'required'
        }),
        error_messages={
            'required': 'Будь ласка, введіть email',
            'invalid': 'Будь ласка, введіть коректний email'
        }
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # You can add additional validation here if needed
        # For example, check if email is already subscribed
        return email


class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Пошук...',
            'class': 'form-control',
            'aria-label': 'Search',
            'aria-describedby': 'button-search',
        }),
        required=False
    )
