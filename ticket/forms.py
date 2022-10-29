from django import forms
from .models import *


class JoinForm(forms.ModelForm):
    # or forms.ModelForm
    email = forms.EmailField()
    name = forms.CharField(max_length=120)


class OrderForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Phone',
        'type': 'text',
        'name': 'phone',
        'id': 'phone',
        'class': 'form-control',
        # 'disabled': True
    }
    )
    )

    class Meta:
        model = Customer
        fields = '__all__'
