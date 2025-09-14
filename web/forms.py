from django import forms


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "logInputTxt"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "logInputTxt"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "logInputTxt"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "logInputTxt"}))


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "logInputTxt"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "logInputTxt"}))


class PasswordResetForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "logInputTxt"}))


class RestaurantCreateForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "logInputTxt"}))
    website_content = forms.CharField(widget=forms.Textarea(attrs={"class": "logInputTxt"}), required=False)
