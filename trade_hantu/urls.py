from django.urls import path
from . import views

urlpatterns = [
    path("oauth_token/", views.get_oauth_token, name="oauth_token"),
    path("issue_access_token/", views.issue_access_token, name="issue_token"),
    path("destroy_access_token/", views.destroy_access_token, name="destroy_token"),
    # path('get_current_stock_price/', views.get_current_stock_price, name='get_current_stock_price'),

]