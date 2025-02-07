from django.urls import path
from . import views  # users 앱의 views.py 가져오기

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),  # 회원가입
    path('login/', views.Login, name='login'),  # 로그인
    path('<int:id>/activation/', views.UserActivateView.as_view(), name='activation'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:pk>/', views.user_detail, name="user_detail"),
    path('me/', views.MeView.as_view(), name='me'),
]
