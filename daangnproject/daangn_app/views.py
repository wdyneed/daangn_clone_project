from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import Post, PostImage, chatroom, ChatMessage, User, DisconnectInfo
from .forms import PostForm, LoginForm, UpdateNicknameForm
from django.contrib import messages
from django.db.models import Q, F, ExpressionWrapper, Exists, OuterRef, Subquery, DateTimeField
from .serializers import PostSerializer, PostImageSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from django.views.generic import FormView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from asgiref.sync import sync_to_async
from datetime import datetime


def main_view(request):
    """
    main화면(index페이지) 렌더링하는 함수
    """
    posts = Post.objects.all()
    return render(request, "daangn_app/main.html", {"posts": posts})


def chat_view(request):
    """
    채팅페이지 렌더링하는 함수
    """
    current_user_id = request.user.id
    # 현재 user랑 작성자 id 같은 것들 temp2에 저장
    # 구매자만 지금 채팅방이 보이기 때문에 구매자가 메세지를 보내면 판매자의 채팅 리스트에도 뜨게끔 하기 위한 변수
    temp2 = Post.objects.filter(author_id=current_user_id)
    # temp2 에서 post의 id 값만 뽑아서 post_ids에 저장
    post_ids = [post.id for post in temp2]

    # 채팅방 테이블의 post_id 값과 post_ids의 값이 같은 것들 필터링
    chat_rooms = chatroom.objects.filter(user_id=current_user_id)
    receive_chat_rooms = chatroom.objects.filter(post_id__in=post_ids)

    # 채팅방이 존재할 때
    if chat_rooms or receive_chat_rooms:
        return render(
            request,
            "daangn_app/chat.html",
            {"chat_rooms": chat_rooms, "receive_chat_rooms": receive_chat_rooms},
        )
    # 현재 아무런 채팅도 하지 않았을 때
    else:
        return render(request, "daangn_app/chat.html")


def filter_chat_rooms(request):
    """
    채팅방 리스트 필터링 함수
    읽지 않은 채팅방만 보여주는 함수입니다.
    """
    is_unread = request.GET.get("unread_checkbox") == "true"
    current_user_id = request.user.id
    temp2 = Post.objects.filter(author_id=current_user_id)
    post_ids = [post.id for post in temp2]
    chat_rooms = chatroom.objects.filter(user_id=current_user_id)
    receive_chat_rooms = chatroom.objects.filter(post_id__in=post_ids)
    excluded_ids = []
    for i in chat_rooms:
        if DisconnectInfo.objects.filter(chat_room_id=i.id).first():
            check = DisconnectInfo.objects.filter(chat_room_id=i.id).first()
            if i.created_at > check.disconnect_time:
                excluded_ids.append(check.chat_room.id)

    real_chat_rooms = chatroom.objects.filter(user_id=current_user_id).exclude(id__in=excluded_ids)
    r_data = []
    for r in real_chat_rooms:
        r_d = {
            "email": r.post_id.author.email,
            "wt_location": r.post_id.wt_location,
            "created_at": r.created_at,
            "title": r.post_id.title,
        }
        r_data.append(r_d)

    return JsonResponse({"chatRooms": r_d})


def create_chat_room(request):
    """
    채팅방 생성하는 함수
    """
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        current_user = request.user

        # 이미 생성된 채팅방이 있는지 확인
        chat_room = chatroom.objects.filter(post_id_id=post, user_id=current_user).first()

        if not chat_room:
            # 채팅방이 없으면 새로운 채팅방 생성
            chat_room = chatroom.objects.create(
                post_id_id=post.id, user_id=current_user.id, created_at=timezone.now()
            )
            post.chat_num += 1
            post.save()
        # 생성된 채팅방의 ID를 클라이언트에게 반환
        return JsonResponse({"chat_room_id": chat_room.id})


# 채팅방 정보 갖고오는 view
def get_contact_info(request):
    """
    채팅페이지 각 채팅방별 정보 갖고오는 함수
    """
    if request.method == "GET":
        chat_room_id = request.GET.get("chat_room_id")
        current_user = request.user.email
        # chat_room_id에 해당하는 채팅방을 가져옵니다.
        chat_room = get_object_or_404(chatroom, id=chat_room_id)
        chat_message = ChatMessage.objects.filter(chatroom_id=chat_room_id)
        # 가져온 채팅방에서 상대방 아이디 또는 다른 필요한 정보를 추출합니다.
        temp_info = chat_room.post_id.author.email  # 상대방 아이디 예시
        temp_info2 = chat_room.user.email
        # 현재 로그인한 사람과 같은 값이면 다른 값으로 변경 (ex: 로그인=A 채팅방 상대 =A 일시 B로 변경하는 코드)
        if current_user == temp_info:
            contact_info = temp_info2
        else:
            contact_info = temp_info
        title_info = chat_room.post_id.title
        price_info = chat_room.post_id.price
        messages_data = []
        for message in chat_message:
            message_data = {
                "content": message.content,
                "send_at": message.send_at,
                "sender": message.sender.id,  # 발신자의 username을 가져옴
            }
            messages_data.append(message_data)
        # 상대방 아이디 또는 다른 정보를 JSON 응답으로 반환합니다.
        return JsonResponse(
            {
                "contactInfo": contact_info,
                "titleInfo": title_info,
                "priceInfo": price_info,
                "messages": messages_data,
            }
        )


# 검색기능
def search_view(request):
    """
    검색기능 제공 함수
    """
    search_query = request.GET.get("search", "")
    posts = Post.objects.filter(
        Q(title__icontains=search_query) | Q(description__icontains=search_query)
    ).distinct()
    context = {"posts": posts, "search_query": search_query}

    return render(request, "daangn_app/search.html", context)


def trade_view(request):
    posts = Post.objects.all()
    return render(request, "daangn_app/trade.html", {"posts": posts})


def trade_post_view(request, post_id):
    """
    판매제품 상세 페이지 함수
    """
    post = get_object_or_404(Post, id=post_id)
    # 해당 게시물에 연결된 이미지 가져오기
    images = PostImage.objects.filter(post=post)
    if request.method == "POST":
        pass
    if "post_viewed_%s" % post_id not in request.session:
        post.view_count += 1
        post.save()
        request.session["post_viewed_%s" % post_id] = True
    return render(request, "daangn_app/trade_post.html", {"post": post, "images": images})


def author_detail_view(request, author):
    """
    판매자 모든 물품 보는 함수
    """
    posts = Post.objects.filter(author=author)
    post_user = User.objects.get(id=author)
    return render(
        request, "daangn_app/author_detail.html", {"posts": posts, "post_user": post_user}
    )


class PostImageForm(forms.PostForm):  # ModelForm을 상속합니다.
    class Meta:
        model = PostImage
        fields = ["image"]


def create_form_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        image_form = PostImageForm(request.FILES)  # 이미지를 업로드하기 위한 폼 생성

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
            for image in request.FILES.getlist("images"):
                PostImage.objects.create(post=post, image=image)

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


def create_post(request, post_id=None):
    # 게시물 수정 여부 확인
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
    else:
        post = None

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        print("request.method == POST")
        if form.is_valid():
            post = form.save(commit=False)
            post.date = timezone.now()
            post.save()

            print("게시물이 성공적으로 수정되었습니다.")
            return redirect("daangn_app:main")
        else:
            print("폼 유효성 검사 실패:", form.errors)
    else:
        print("else")
        form = PostForm(instance=post)

    context = {"form": form}
    return render(request, "daangn_app/write.html", context)


def edit_view(request, post_id):
    # 게시물 객체 가져오기
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        # POST 요청이면, 폼을 기존 게시물 데이터로 채워서 생성
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # 필요한 경우 추가 작업 수행
            post.save()
            return redirect("daangn_app:main")  # 수정 완료 후 메인 페이지로 이동
    else:
        # GET 요청이면, 폼을 기존 게시물 데이터로 초기화
        form = PostForm(
            instance=post,
            initial={
                "category": post.category,
                "wt_location": post.wt_location,
            },
        )

    # 폼과 게시물 객체를 템플릿에 전달
    context = {"form": form, "post": post}
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
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs["post_pk"])
        serializer.save(post=post)


def show_post_images(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    images = post.images.all()
    return render(request, "trade_post.html", {"post": post, "images": images})


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


# 별명, 사진 수정하기


class UpdateUserInfoView(View):
    template_name = "registration/myinfo.html"
    form_class = UpdateNicknameForm

    def get(self, request):
        user = request.user
        form = self.form_class(instance=user)
        return render(request, self.template_name, {"update_form": form})

    def post(self, request):
        user = request.user
        form = self.form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "별명과 프로필 이미지가 성공적으로 수정되었습니다.")
            return redirect("daangn_app:main")
        return render(request, self.template_name, {"update_form": form})


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


# 메세지를 DB에 저장하는 함수
def create_chat_message(sender, content, chatroom_id, send_at):
    chat_message = ChatMessage.objects.create(
        sender=sender, content=content, chatroom_id=chatroom_id, send_at=send_at
    )
    chat_message.save()


# 채팅방 시간 변경하는 함수
def change_chatroom_time(chatroom_id):
    chat_room = chatroom.objects.filter(id=chatroom_id).first()
    chat_room.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_room.save()
