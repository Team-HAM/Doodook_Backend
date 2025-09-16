from django.urls import path
from .views import AddToWatchlistView, RemoveFromWatchlistView, ListWatchlistView

urlpatterns = [
    path('add/', AddToWatchlistView.as_view(), name='add-to-watchlist'),
    path('remove/', RemoveFromWatchlistView.as_view(), name='remove-from-watchlist'),
    path('list/', ListWatchlistView.as_view(), name='list-watchlist'),
]
