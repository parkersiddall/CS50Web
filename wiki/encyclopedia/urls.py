from django.urls import path


from . import views

urlpatterns = [
    path("random", views.get_random_entry, name="random"),  # path run pull up a random entry
    path("edit/<str:entry>", views.edit, name="edit"),  # path to modify content on the page
    path("new_entry", views.new_entry, name="new_entry"),  # path to the new entry page
    path("search", views.search, name="search"), # path to display search results given a keyword
    path("", views.index, name="index"),
    path("<str:title>", views.title, name="entry") # path to display an entry page given the title

]
