# # profiles/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path("by_username/", views.by_username, name="profiles-by-username"),
#     path("me/", views.me, name="profiles-me"),
#     path("follow/", views.follow_toggle),     # your follow toggle
#     path("suggested/", views.suggested),      # ← add this
    
# ]

# profiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("me/", views.me),
    path("by_username/", views.by_username),
    path("follow/", views.follow_toggle),
    path("suggested/", views.suggested),
    path("search/", views.search),
    path("followers/", views.followers_list),
path("following/", views.following_list),

]
