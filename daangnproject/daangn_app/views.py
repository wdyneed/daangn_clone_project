from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm


def main_view(request):
    return render(request, "daangn_app/main.html")


def search_view(request):
    return render(request, "daangn_app/search.html")


def login_view(request):
    return render(request, "registration/login.html")


def register_view(request):
    return render(request, "registration/register.html")


def trade_view(request):
    return render(request, "daangn_app/trade.html")


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
                images=request.FILES.get("images"),
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
