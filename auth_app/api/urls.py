from django.urls import path

from auth_app.api.views import EmailCheckView, LoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view()),
    path('login/', LoginView.as_view()),
    path('email-check/', EmailCheckView.as_view()),
]
