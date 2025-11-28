from django.urls import path
from . import views
from .feeds import LatestPostsFeed, AtomSiteNewsFeed

app_name = 'blog'

urlpatterns = [
    # Головна сторінка з усіма публікаціями
    path('', views.post_list, name='post_list'),
    # Детальний перегляд публікації
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', 
         views.post_detail, 
         name='post_detail'),
    # Поділитися публікацією
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # Додати коментар
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    # Сторінка з публікаціями за тегом
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # RSS стрічка (основний фід)
    path('feed/', LatestPostsFeed(), name='post_feed'),
    # Додаткові формати фідів
    path('feed/rss/', LatestPostsFeed(), name='post_rss_feed'),
    path('feed/atom/', AtomSiteNewsFeed(), name='post_atom_feed'),
]
