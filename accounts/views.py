from django.shortcuts import render
from django.views import View
# Create your views here.
class UserRegistrationView(View):
    def get(self, request):
        # Render the registration form template
        pass

    def post(self, request):
        pass  # Handle the form submission and create a new user
       