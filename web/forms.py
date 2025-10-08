from django import forms

from restaurants.models import InventoryItem, MenuItem, MenuItemMedia


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


class MenuItemForm(forms.ModelForm):
    ingredients = forms.CharField(required=False, help_text="Comma-separated list of ingredients")
    allergens = forms.CharField(required=False, help_text="Comma-separated list of allergens")

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'is_available', 'ingredients', 'allergens', 'cover']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cover': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.ingredients:
                self.initial['ingredients'] = ', '.join(self.instance.ingredients)
            if self.instance.allergens:
                self.initial['allergens'] = ', '.join(self.instance.allergens)

    def clean_ingredients(self):
        data = self.cleaned_data['ingredients']
        return [item.strip() for item in data.split(',') if item.strip()] if data else []

    def clean_allergens(self):
        data = self.cleaned_data['allergens']
        return [item.strip() for item in data.split(',') if item.strip()] if data else []


class MenuItemMediaForm(forms.ModelForm):
    class Meta:
        model = MenuItemMedia
        fields = ['file', 'media_type']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
        }
