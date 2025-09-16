from django import forms

from restaurants.models import InventoryItem, MenuItem


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


class AddStockItemForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Item Name"}))
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={"class": "form-control"}))


class DecreaseStockItemForm(forms.Form):
    item_id = forms.CharField(widget=forms.HiddenInput())
    amount = forms.IntegerField(min_value=1, label="Decrease by", widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount"}))
