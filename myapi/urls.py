"""
URL configuration for myapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from users import views
from rest_framework_simplejwt.views import TokenObtainPairView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('doodook/', include('doodook.urls')),
    path('users/', views.SignupView.as_view(), name='signup'),  # POST (회원가입입)
    path('sessions/', views.Login, name='login'),  # POST (로그인)
    path('users/<int:id>/activation', views.UserActivateView.as_view(), name='activation'),  # GET (인증증)

    # path("signup/", views.SignupView.as_view()), ->기존 signup url
    # path('login/', views.Login),  # 특수 문자가 없는 올바른 문법 ->기존 login url

    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),

    # path('activate/<str:uid>/<str:token>',views.UserActivateView.as_view(), name ='activate'),->기존 인증 url
    path('users/', include('users.urls')),  # 'users' 앱의 URL을 포함
    path("<int:pk>/", views.user_detail),
    path("me/", views.MeView.as_view()),

    path("trade_hantu/", include("trade_hantu.urls")),
    path('trading/', include('trading.urls')),
    

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('stocks/', include('stocks.urls')),  # stocks 앱의 URL 포함
    path('mbti/', include('MBTI.urls')),


    path('api/stock/', include('stock_search.urls')),  # stock_search 앱 URL 등록
  
    path('chatbot/', include('chatbot.urls')),
  
    path('api/', include('guides.urls')),

    path('api/asset/', include('asset.urls')),

    path('progress/', include('progress_guides.urls')),
]
