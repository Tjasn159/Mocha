# reference : https://dev.to/yahaya_hk/usercreation-form-with-multiple-fields-in-django-ek9#:~:text=Note%20that%20the%20default%20UserCreationForm,do%20not%20originally%20come%20included.

from django import forms 
from authors.models import Author
from django.contrib.auth.models import User

class AuthorForm(forms.ModelForm):
    display_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Author
        fields = ("display_name" ,"bio","global_id", "host", "github", "password")

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['display_name'],
            password=self.cleaned_data['password']
        )
        author = super().save(commit=False)
        author.user = user
        if commit:
            author.save()
        return author
    
