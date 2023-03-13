from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="index"),
    path("posts/<slug:slug>", views.post_detail, name="post_detail"),
    path("new-post", views.make_post, name="add-post"),
    path("search=<str:query>", views.search, name="search"),
    path("vote/<int:pk>", views.vote, name="vote"),
]
