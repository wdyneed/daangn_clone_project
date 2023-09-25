from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="글 제목")
    price = models.IntegerField(verbose_name="가격")
    description = models.TextField(verbose_name="설명")
    product_image = models.ImageField(null=True, upload_to="", blank = True)
    location = models.CharField(max_length=200, verbose_name="사는 곳")
    category = models.CharField(max_length=255)
    view_count = models.PositiveIntegerField(default=0, verbose_name="조회수")
    created_at = models.DateTimeField(verbose_name="업로드 날짜", auto_now_add=True)
    updated = models.CharField(verbose_name="끌올", default='N')
    wt_location = models.CharField(max_length=300, verbose_name="판매 원하는 장소")
    status = models.CharField(max_length=100, default="판매중", verbose_name="판매 상태")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자", default='')
    
class UserInfo(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    user_img = models.ImageField(upload_to="user_img")

    
class chatroom(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ChatMessage(models.Model):
    chatroom_id = models.ForeignKey(chatroom, on_delete=models.CASCADE)
    content = models.TextField()
    sender = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    send_at = models.DateTimeField(auto_now_add=True)
    chat_img = models.ImageField(upload_to="chat")
    