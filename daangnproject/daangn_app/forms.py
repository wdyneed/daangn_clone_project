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
            "category",
            "wt_location",
        ]


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ["image"]


class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일")
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")

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
            "nickname",
            "email",
        )

    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")
    password1 = forms.CharField(widget=forms.PasswordInput, label="비밀번호 확인")

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password != password1:
            raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        else:
            return password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "성"
        self.fields["last_name"].label = "이름"
        self.fields["email"].label = "이메일"
        self.fields["nickname"].label = "사용할 별명"

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password)
        user.save()


# 내정보 수정기능 (테스트중)
class UpdateNicknameForm(forms.ModelForm):
    profile_image = forms.ImageField(label="변경할 이미지", required=False)

    class Meta:
        model = models.User
        fields = ["nickname", "profile_image"]
        labels = {"nickname": "별명"}

    def save(self, commit=True):
        user = super().save(commit=False)

        profile_image = self.cleaned_data.get("profile_image")
        if profile_image:
            user.user_img = profile_image

        if commit:
            user.save()
        return user
