from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Post, UserInfo, PostImage
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

def main_view(request):
    return render(request, "daangn_app/main.html")

def chat_view(request):
    return render(request, "daangn_app/chat.html")

def search_view(request):
    search_query = request.GET.get('search', '')
    posts = Post.objects.filter(
        Q(title__icontains=search_query) | Q(description__icontains=search_query)
    ).distinct()
    context = {
        'posts' : posts,
        'search_query' : search_query
    }
    
    return render(request, "daangn_app/search.html", context)


def login_view(request):
    return render(request, "registration/login.html")


def register_view(request):
    return render(request, "registration/register.html")


def trade_view(request):
    return render(request, "daangn_app/trade.html")

# 판매 제품 상세 페이지
def trade_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        pass
    if 'post_viewed_%s' % post_id not in request.session:
        post.view_count += 1
        post.save()
        request.session['post_viewed_%s' % post_id] = True
    return render(request, 'daangn_app/trade_post.html', { post : 'post' })

# 판매자 모든 물품 보는 view
def author_detail_view(request, author):
    posts = get_object_or_404(Post, author=author)
    user = get_object_or_404(UserInfo, user_id=author)
    return render(request, "daangn_app/author_detail.html", {posts : 'posts', user:'user'})

def create_form_view(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            category = request.POST.get("category")
            wt_location = request.POST.get("wt_location")

            post = Post(
                title=form.cleaned_data["title"],
                price=form.cleaned_data["price"],
                description=form.cleaned_data["description"],
                location=form.cleaned_data["location"],
                category=category,
                wt_location=wt_location,
                #images=request.FILES.get("images"),
            )
            post.save()

            return redirect("daangn_app:main")
    else:
        form = PostForm()

    context = {"form": form}
    return render(request, "daangn_app/chat.html", context)


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
            return redirect("daangn_app:main")
    else:
        form = PostForm(instance=post)

    context = {"form": form}
    return render(request, "daangn_app/write.html", context)


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
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs['post_pk'])
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