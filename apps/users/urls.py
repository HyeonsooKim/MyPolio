from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserSignUpView, UserSignInView, UserSignOutView, UserWithdrawalView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path("sign-up/", UserSignUpView.as_view()),
    path("sign-in/", UserSignInView.as_view()),
    path("sign-out/", UserSignOutView.as_view()),    
    path("<int:pk>/withdraw/", UserWithdrawalView.as_view()),
]