from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Маршрут для перегляду поста за датою та slug
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail,
         name='post_detail'),
]