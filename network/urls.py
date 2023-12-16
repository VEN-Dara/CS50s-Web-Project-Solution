
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("post/<str:post_type>", views.load_post, name="load_post"),
    path("profile/<str:username>", views.profile_info, name="profile_info"),
    re_path(r'^.*$', views.index, name='index'),
]
