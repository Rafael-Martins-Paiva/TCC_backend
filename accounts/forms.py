from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        # Você pode adicionar lógica personalizada aqui se precisar salvar outros campos
        return user
