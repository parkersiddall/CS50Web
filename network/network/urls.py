
from django.urls import path

from . import views

urlpatterns = [
    path("following", views.following, name="following"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API routes
    path("edit", views.edit, name="edit"),
    path("unlike", views.unlike, name="unlike"),
    path("like", views.like, name="like"),
]
