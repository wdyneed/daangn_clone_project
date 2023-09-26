from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostImageViewSet, LoginView, RegisterView

app_name = "daangn_app"
router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'post/(?P<post_pk>[0-9]+)/images', PostImageViewSet, basename='post-image')

urlpatterns = [
    path("", views.main_view, name="main"),
    path("search/", views.search_view, name="search"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("create/form/", views.create_form_view, name="create_form"),
    path("write/", views.create_or_edit_post, name="write"),
    path("edit/<int:post_id>/", views.create_or_edit_post, name="edit"),
    path("trade/", views.trade_view, name="trade"),
    path('post/<int:post_id>/', views.trade_post_view, name='post'),
    path('chat/', views.chat_view, name='chat'),
    path('author_detail/<str:author>/', views.author_detail_view, name='author_detail'),
    path('api/', include(router.urls)),
    path("logout/", views.log_out, name="logout"),
    path('trade-post/<int:post_id>', views.trade_post_view, name='trade-post'),
    path('create_chat_room/', views.create_chat_room, name='create_chat_room'),
    path('chat/<int:room_id>', views.chat_view, name='chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
