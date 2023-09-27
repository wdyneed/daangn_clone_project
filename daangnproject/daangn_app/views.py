from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Post, User, PostImage, chatroom, ChatMessage
from .forms import PostForm, LoginForm
from django.contrib import messages
from django.db.models import Q
from .serializers import PostSerializer, PostImageSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from django.views.generic import FormView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone


def main_view(request):
    posts = Post.objects.all()
    return render(request, "daangn_app/main.html", {"posts": posts})


def chat_view(request):
    chat_rooms = chatroom.objects.all()

    if chat_rooms:
        return render(request, "daangn_app/chat.html", {"chat_rooms": chat_rooms})


def create_chat_room(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        current_user = request.user

        # 이미 생성된 채팅방이 있는지 확인
        chat_room = chatroom.objects.filter(
            post_id_id=post, user_id=current_user
        ).first()

        if not chat_room:
            # 채팅방이 없으면 새로운 채팅방 생성
            chat_room = chatroom.objects.create(
                post_id_id=post.id, user_id=current_user.id
            )
        # 생성된 채팅방의 ID를 클라이언트에게 반환
        return JsonResponse({"chat_room_id": chat_room.id})


def search_view(request):
    search_query = request.GET.get("search", "")
    posts = Post.objects.filter(
        Q(title__icontains=search_query) | Q(description__icontains=search_query)
    ).distinct()
    context = {"posts": posts, "search_query": search_query}

    return render(request, "daangn_app/search.html", context)


def trade_view(request):
    posts = Post.objects.all()
    return render(request, "daangn_app/trade.html", {"posts": posts})


# 판매 제품 상세 페이지
def trade_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        pass
    if "post_viewed_%s" % post_id not in request.session:
        post.view_count += 1
        post.save()
        request.session["post_viewed_%s" % post_id] = True
    return render(request, "daangn_app/trade_post.html", {"post": post})


# 판매자 모든 물품 보는 view
def author_detail_view(request, author):
    posts = get_object_or_404(Post, author=author)
    user = get_object_or_404(UserInfo, user_id=author)
    return render(
        request, "daangn_app/author_detail.html", {"posts": posts, "user": user}
    )


class PostImageForm(forms.PostForm):  # ModelForm을 상속합니다.
    class Meta:
        model = PostImage
        fields = ["image"]


def create_form_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        image_form = PostImageForm(request.POST, request.FILES)  # 이미지를 업로드하기 위한 폼 생성

        if form.is_valid() and image_form.is_valid():  # 폼 및 이미지 폼 모두 유효한지 확인
            title = form.cleaned_data["title"]
            price = form.cleaned_data["price"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            wt_location = form.cleaned_data["wt_location"]

            if request.user.is_authenticated:
                author = request.user
            else:
                author = None

            # 새로운 Post 인스턴스를 생성하고 저장합니다.
            post = Post(
                title=title,
                price=price,
                description=description,
                category=category,
                wt_location=wt_location,
                author=author,
                updated=timezone.now(),
            )
            post.save()

            # 이미지를 업로드하고 연결합니다.
            image = image_form.save(commit=False)
            image.post = post
            image.save()

            return redirect("daangn_app:main")
        else:
            # 폼 데이터가 유효하지 않은 경우
            # 폼에서 발생한 오류 메시지 출력
            print(form.errors)
            print(image_form.errors)
    else:
        form = PostForm()
        image_form = PostImageForm()  # 빈 이미지 폼 생성

    context = {"form": form, "image_form": image_form}  # 이미지 폼을 템플릿에 전달
    return render(request, "daangn_app/trade.html", context)


def create_or_edit_post(request, post_id=None):
    if post_id:
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            post = None
    else:
        post = None

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()

            # 이미지를 업로드하고 PostImage 모델에 저장
            images = request.FILES.getlist("images")  # HTML 폼에서 업로드한 이미지 리스트
            for image in images:
                PostImage.objects.create(post=post, image=image)

            return redirect("daangn_app:main")
    else:
        form = PostForm(instance=post)

    context = {"form": form}
    return render(request, "daangn_app/write.html", context)


def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 이제 사용자 정보를 비교할 때 post.author를 사용합니다.
    if request.user.email == post.author.email:
        if request.method == "POST":
            post.delete()
            messages.success(request, "게시물이 성공적으로 삭제되었습니다.")
            return redirect("daangn_app:trade")
    else:
        messages.error(request, "게시물 삭제 권한이 없습니다.")
        return redirect("daangn_app:trade")

    return render(request, "daangn_app/trade.html", {"post": post})


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostImageViewSet(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs["post_pk"])
        serializer.save(post=post)


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = forms.RegisterForm
    success_url = "/login/"

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)

        if hasattr(user, "verify_email") and callable(getattr(user, "verify_email")):
            user.verify_email()

        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
    except models.User.DoesNotExist:
        pass
    return render(request, "registration/login.html")


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        context = {"form": form}
        return render(request, "registration/login.html", context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")  # Redirect to the main page
            else:
                # 로그인 실패 메시지를 추가하고 다시 로그인 페이지를 렌더링
                messages.error(request, "로그인에 실패했습니다. 올바른 이메일과 비밀번호를 입력하세요.")

        context = {"form": form}
        return render(request, "registration/login.html", context)


def log_out(request):
    logout(request)
    return redirect(reverse("daangn_app:login"))


def location_view(request):
    user_info = User.objects.get(email=request.user)
    if user_info.location:
        context = {
            "region": user_info.location,
            "certified": user_info.location_certified,
        }
        return render(request, "daangn_app/location.html", context)
    else:
        return render(request, "daangn_app/location.html")


def location_edit_view(request):
    region = request.POST["region-setting"]
    user_info = User.objects.get(email=request.user)
    user_info.location = region
    user_info.location_certified = False
    user_info.save()
    context = {
        "region": region,
        "certified": False,
    }
    return redirect(reverse("daangn_app:location"))


def location_certification_view(request):
    User_pk_id = User.objects.get(email=request.user).id
    user_info = User.objects.get(email=request.user)
    user_info.location_certified = True
    user_info.save()
    context = {
        "region": user_info.location,
        "certified": True,
    }
    return redirect(reverse("daangn_app:location"))
