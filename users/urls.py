# users/urls.py
from django.urls import path
from . import views
from .views import UserDeleteView

urlpatterns = [
    # 'me/' 경로에 대한 처리
    path('me/', views.MeView.as_view(), name='user_me'),

    # '<int:pk>/' 경로에 대한 처리 (사용자 정보 가져오기)
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('account/', views.get_user_account, name='get_user_account'), #사용자별 계좌 잔고가 될 듯함
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
]
