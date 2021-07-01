from django import forms
from django.core.validators import RegexValidator


class OrderForm(forms.Form):
    widget_attrs = {'class': 'form-control', 'placeholder': 'Placeholder'}
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be in the '+999999999' format")
    first_name = forms.CharField(label="Name",
                                 widget=forms.widgets.TextInput(
                                     attrs={**widget_attrs, **{'id': 'fieldFirstName'}}))

    last_name = forms.CharField(label="Surname",
                                widget=forms.widgets.TextInput(
                                    attrs={**widget_attrs, **{'id': 'fieldLastName'}}))

    phone = forms.CharField(label="Phone number",
                            validators=[phone_regex], max_length=17,
                            widget=forms.widgets.TextInput(
                                attrs={**widget_attrs, **{'id': 'fieldLastName'}}))

    address = forms.CharField(label="Address",
                              widget=forms.widgets.TextInput(
                                  attrs={**widget_attrs, **{'id': 'fieldAddress'}}))
