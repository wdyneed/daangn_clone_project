from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    PostImageViewSet,
    LoginView,
    RegisterView,
    UpdateUserInfoView,
)

app_name = "daangn_app"
router = DefaultRouter()
router.register(r"posts", PostViewSet)
router.register(
    r"post/(?P<post_pk>[0-9]+)/images", PostImageViewSet, basename="post-image"
)

urlpatterns = [
    path("", views.main_view, name="main"),
    path("search/", views.search_view, name="search"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("create/form/", views.create_form_view, name="create_form"),
    path("write/", views.create_post, name="write"),
    path("edit/<int:post_id>/", views.edit_view, name="edit"),
    path("trade/", views.trade_view, name="trade"),
    path("trade/<path:category>", views.trade_view_category, name="trade_category"),
    path("post/<int:post_id>/", views.trade_post_view, name="post"),
    path("chat/", views.chat_view, name="chat"),
    path("author_detail/<str:author>/", views.author_detail_view, name="author_detail"),
    path("api/", include(router.urls)),
    path("logout/", views.log_out, name="logout"),
    path("trade-post/<int:post_id>", views.trade_post_view, name="trade-post"),
    path("create_chat_room/", views.create_chat_room, name="create_chat_room"),
    path("chat/<int:post_id>", views.chat_view, name="chat"),
    path("chat/<int:chat_room_id>/", views.chat_view, name="chat_view"),
    path("trade-post/<int:pk>/", views.trade_post_view, name="trade_post"),
    path("trade-post/<int:pk>/delete/", views.delete_post_view, name="delete_post"),
    path("location/", views.location_view, name="location"),
    path("location_edit/", views.location_edit_view, name="location_edit"),
    path(
        "location_certification/",
        views.location_certification_view,
        name="location_certification",
    ),
    path("get_contact_info/", views.get_contact_info, name="get_contact_info"),
    path("myinfo/", UpdateUserInfoView.as_view(), name="update_user_info"),
    path("filter_chat_rooms/", views.filter_chat_rooms, name="filter_chat_rooms"),
    path("change_status/<int:post_id>/", views.change_status, name="change_status"),
    path("get_last_message/", views.get_last_message, name="get_last_message"),
    path(
        "api/post/<int:post_pk>/images/",
        PostImageViewSet.as_view({"post": "create"}),
        name="post-image",
    ),
    path("create_or_join_chatroom/", views.create_or_join_chatroom, name="create_or_join_chatroom"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
