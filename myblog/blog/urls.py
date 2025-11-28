from django.urls import path
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from . import views
from .feeds import LatestPostsFeed, AtomSiteNewsFeed

app_name = 'blog'

urlpatterns = [
    # Головна сторінка з усіма публікаціями
    path('', views.post_list, name='post_list'),
    # Сторінка з публікаціями за тегом
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # Детальний перегляд публікації
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', 
         views.post_detail, 
         name='post_detail'),
    # Поділитися публікацією
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # Підписка на публікації
    path('subscribe/', views.subscribe, name='subscribe'),
    # RSS стрічка
    path('feed/rss/', LatestPostsFeed(), name='post_feed'),
    # Atom стрічка
    path('feed/atom/', AtomSiteNewsFeed(), name='post_atom_feed'),
]
