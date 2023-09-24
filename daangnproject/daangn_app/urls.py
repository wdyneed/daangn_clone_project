from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "daangn_app"

urlpatterns = [
    path("main/", views.main_view, name="main"),
    path("search/", views.search_view, name="search"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("create/form/", views.create_form_view, name="create_form"),
    path("write/", views.create_or_edit_post, name="write"),
    path("edit/<int:post_id>/", views.create_or_edit_post, name="edit"),
    path("trade/", views.trade_view, name="trade"),
    path('post/', views.trade_post_view, name='post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
