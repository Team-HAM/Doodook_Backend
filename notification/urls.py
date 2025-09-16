from django.urls import path
from . import views

urlpatterns =[
    path('',views.notification_list,name='notification-list'),
    path('<int:pk>/',views.notification_detail,name='notification-detail'),
    path('create/', views.create_notification, name='notification-create'),
]