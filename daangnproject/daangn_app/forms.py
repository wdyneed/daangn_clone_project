from django import forms
from .models import Post, PostImage


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = [
            "title",
            "price",
            "description",
            "location",
            "category",
            "wt_location",
            "updated",
        ]
