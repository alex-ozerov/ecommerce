from django import forms


class CommentForm(forms.Form):
    widget_attrs = {'class': 'form-control', 'placeholder': 'Placeholder'}

    subject = forms.CharField(label="Subject", label_suffix='',
                              widget=forms.widgets.TextInput(
                                  attrs={**widget_attrs, 'id': 'fieldSubject'}))

    rate = forms.ChoiceField(label="Rate", required=True, label_suffix=':',
                             choices=[(num, '☆' + str(num)) for num in range(1, 6)],
                             widget=forms.Select(
                                 attrs={'id': 'fieldRate', 'class': 'form-select'}))

    comment = forms.CharField(label="Comment", label_suffix='',
                              widget=forms.widgets.Textarea(
                                  attrs={**widget_attrs, 'id': 'fieldComment',
                                         'style': 'height: 100px'}))


