from django import forms
from .models import Post, PostImage, User
from . import models


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "price",
            "description",
            "location",
            # "category",
            # "wt_location",
        ]

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return cleaned_data
            else:
                self.add_error("password", "비밀번호를 확인해주세요")
        except User.DoesNotExist:
            self.add_error("email", "등록된 메일 주소가 아닙니다")

        return cleaned_data


class RegisterForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password)
        user.save()