from .apps import UsersConfig
from django.urls import path
from django.contrib.auth.views import LogoutView
from .services import email_verification
from .views import RegistrationView, AuthorizationView, ProfileView, ProfileUpdateView, \
    ProfileDeletingView, ProfilePasswordRecoveryView, ProfilePasswordResetView, ProfileChangingPasswordView, \
    ProfilesListView


app_name = UsersConfig.name

urlpatterns = [
    path('authorization/', AuthorizationView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('profile/email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('users/', ProfilesListView.as_view(), name='users'),
    path('profile/<int:pk>/editing/', ProfileUpdateView.as_view(), name='editing_profile'),
    path('profile/<int:pk>/deleting/', ProfileDeletingView.as_view(), name='deleting_profile'),
    path("password-recovery/", ProfilePasswordRecoveryView.as_view(), name="password_recovery"),
    path("password-reset/", ProfilePasswordResetView.as_view(), name="password_reset"),
    path("password-change/", ProfileChangingPasswordView.as_view(), name="password_change"),
]
