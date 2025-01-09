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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doodook/', include('doodook.urls')),
    path("signup/", views.SignupView.as_view()),
    path('login/', views.Login),  # 특수 문자가 없는 올바른 문법
    path('activate/<str:uid>/<str:token>',views.UserActivateView.as_view(), name ='activate'),
]
