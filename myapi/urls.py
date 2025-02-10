from django.urls import path, include
from django.contrib import admin
from users import views as user_views  # ✅ users 관련 뷰를 따로 관리
from trading import views as trading_views  # ✅ trading 관련 뷰 추가

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doodook/', include('doodook.urls')),

    # ✅ users 관련 URL
    path('users/', include('users.urls')),  # users 앱에서 urls.py를 관리하도록 변경
    path('sessions', user_views.Login, name='login'),
    path('users/<int:id>/activation', user_views.UserActivateView.as_view(), name='activation'),

    path('', user_views.home, name='home'),
    path('logout/', user_views.logout_view, name='logout'),
    path("<int:pk>/", user_views.user_detail),
    path("me/", user_views.MeView.as_view()),

    # ✅ trading 관련 URL
    path('trading/', include('trading.urls')),  # trading 앱에서 urls.py를 관리하도록 변경

    # ✅charting 관련 URL
    path("charting/", include("charting.urls")),  # 🚀 일봉 차트 API 추가
]
