from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("listing/<int:auction_id>", views.listing, name="listing"),
    path("listing/<int:auction_id>/watchlist", views.watchlist, name="update_watchlist"),
    path("listing/<int:auction_id>/close", views.close_bid, name="close_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path('bidded_listing', views.bidded_listing, name="bidded_listing"),
    path("listing/<int:auction_id>/comment", views.comment, name="comment"),
    path("categories", views.category, name="category"),
    path("categories/<int:category_id>", views.category, name="category_view"),
]
