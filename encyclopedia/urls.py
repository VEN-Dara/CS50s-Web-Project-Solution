from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry_url"),
    path("search/", views.search, name="search_url"),
    path("new/", views.new, name="new_url"),
    path("edit/<str:title_entry>", views.edit, name="edit_url"),
    path("save_edit/", views.save_edit, name="save_edit_url"),
    path("random_page/", views.random_page, name = "random_page_url"),
]
