from django.urls import path
from .views import login_view, landing_view

app_name = 'web'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('', landing_view, name='landing'),
]
