from accounts import views
from django.urls import path

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user_registration'),
]