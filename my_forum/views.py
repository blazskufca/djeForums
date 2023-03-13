import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import make_aware
from django.db.models import Q
from . import models
from . import forms

# Create your views here.


def home(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        query = request.POST.get("query")
        return redirect("search", query=query)
    paginator = Paginator(
        models.Posts.objects.all().order_by("-last_modified_post_date"), 25
    )
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "my_forum/index.html", context)


def post_detail(request: WSGIRequest, slug: str) -> HttpResponse:
    if request.method == "GET":
        form = forms.CommentForm(initial={"user": request.session.get("username")})
        post = get_object_or_404(models.Posts, slug=slug)
        paginator = Paginator(post.comments.all().order_by("initial_post_date"), 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "post": post,
            "form": form,
            "page_obj": page_obj,
        }
    if request.method == "POST":
        form = forms.CommentForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            request.session["username"] = form.user
            form.post = models.Posts.objects.get(slug=slug)
            form.initial_post_date = make_aware(datetime.datetime.now())
            post = models.Posts.objects.get(slug=slug)
            post.last_modified_post_date = make_aware(datetime.datetime.now())
            post.save()
            form.save()
            return redirect("post_detail", slug)
        else:
            context = {
                "form": form,
            }
            return render(request, "my_forum/post_detail.html", context)

    return render(request, "my_forum/post_detail.html", context)


def make_post(request: WSGIRequest) -> HttpResponse:
    form = forms.PostForm(initial={"user": request.session.get("username")})
    context = {
        "form": form,
    }
    if request.method == "POST":
        form = forms.PostForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            request.session["username"] = form.user
            form.initial_post_date = make_aware(datetime.datetime.now())
            form.last_modified_post_date = make_aware(datetime.datetime.now())
            form.save()
            return redirect("index")
        else:
            context = {"form": form}
            return render(request, "my_forum/add post.html", context)

    return render(request, "my_forum/add post.html", context)


def search(request: WSGIRequest, query: str) -> HttpResponse:
    model_search = models.Posts.objects.filter(
        Q(title__icontains=query) | Q(user__icontains=query)
    )
    paginator = Paginator(model_search, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "result_num": model_search.count(),
    }
    return render(request, "my_forum/search.html", context)


def vote(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    if request.method == "POST":
        if request.session.get("commented") is None:
            request.session["commented"] = []
        comment = models.Comments.objects.get(pk=pk)
        if (
            request.POST.get("upvote") is not None
            and (request.POST.get("downvote") is None)
            and comment.pk not in request.session.get("commented")
        ):
            comment.votes += 1
            comment.save()
            request.session["commented"].append(comment.pk)
            request.session.modified = True
        elif (
            request.POST.get("upvote") is None
            and (request.POST.get("downvote") is not None)
            and comment.pk not in request.session.get("commented")
        ):
            comment.votes -= 1
            comment.save()
            request.session["commented"].append(comment.pk)
            request.session.modified = True
        return redirect(request.META.get("HTTP_REFERER"))
