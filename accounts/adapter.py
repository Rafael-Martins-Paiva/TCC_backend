from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        # Add any custom logic here after the user is saved
        return user
