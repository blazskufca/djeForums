from http import HTTPStatus
import datetime
import pytest
from django.test import Client
from django.utils.timezone import make_aware
from my_forum.models import Posts, Comments
from django.shortcuts import reverse


@pytest.fixture
def create_post_in_database():
    Posts(
        initial_post_date=make_aware(datetime.datetime.today()),
        title="test",
        user="demo",
        post_content="testing",
        last_modified_post_date=make_aware(datetime.datetime.today()),
    ).save()


@pytest.mark.django_db
def test_get_home_page():
    c = Client()
    response = c.get("")
    assert response.status_code == HTTPStatus.OK or 302


@pytest.mark.django_db
def test_search_functionality(create_post_in_database):
    c = Client()
    response = c.post("", data={"query": "test"}, follow=True)
    assert response.status_code == HTTPStatus.OK or 302
    assert "test" in str(response.content)
    assert "We found 1 hits matching your query" in str(response.content)


@pytest.mark.django_db
def test_if_post_is_in_db():
    c = Client()
    response = c.post(
        reverse("add-post"),
        data={"title": "test", "user": "Demo", "post_content": "Testing"},
    )
    assert response.status_code == HTTPStatus.OK or 302
    assert Posts.objects.all().count() == 1


@pytest.mark.django_db
def test_if_post_can_be_retrieved_from_database(create_post_in_database):
    c = Client()
    response = c.get(reverse("post_detail", kwargs={"slug": "test"}))
    assert response.status_code == HTTPStatus.OK or 302
    assert Posts.objects.all().count() == 1
    assert "test" in str(response.content)
    assert "demo" in str(response.content)


@pytest.mark.django_db
def test_if_comment_can_be_added(create_post_in_database):
    c = Client()
    response = c.post(
        reverse("post_detail", kwargs={"slug": "test"}),
        data={"user": "Test comment", "post_content": "A test of a comment"},
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK or 302
    assert Comments.objects.all().count() == 1
    assert "Test comment" in str(response.content)
    assert "A test of a comment" in str(response.content)


@pytest.mark.django_db
def test_if_up_voting_on_comments_works(create_post_in_database):
    c = Client()
    response = c.post(
        reverse("post_detail", kwargs={"slug": "test"}),
        data={"user": "Test comment", "post_content": "A test of a comment"},
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK or 302
    c.post(
        reverse("vote", kwargs={"pk": 1}),
        data={"upvote": 1},
        HTTP_REFERER=reverse("post_detail", kwargs={"slug": "test"}),
    )
    assert Comments.objects.all().count() == 1
    model = Comments.objects.get(pk=1)
    assert model.votes == 1


@pytest.mark.django_db
def test_if_up_down_voting_on_comments_works(create_post_in_database):
    c = Client()
    response = c.post(
        reverse("post_detail", kwargs={"slug": "test"}),
        data={"user": "Test comment", "post_content": "A test of a comment"},
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK or 302
    c.post(
        reverse("vote", kwargs={"pk": 1}),
        data={"downvote": 1},
        HTTP_REFERER=reverse("post_detail", kwargs={"slug": "test"}),
    )
    assert Comments.objects.all().count() == 1
    model = Comments.objects.get(pk=1)
    assert model.votes == -1


@pytest.mark.django_db
def test_if_str_dunder_method_on_Post_model_works(create_post_in_database):
    instance = Posts.objects.get(pk=1)
    assert '"test" by demo' == str(instance)


@pytest.mark.django_db
def test_if_str_dunder_method_on_Comment_model_works(create_post_in_database):
    c = Client()
    response = c.post(
        reverse("post_detail", kwargs={"slug": "test"}),
        data={"user": "Test comment", "post_content": "A test of a comment"},
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK or 302
    c.post(
        reverse("vote", kwargs={"pk": 1}),
        data={"upvote": 1},
        HTTP_REFERER=reverse("post_detail", kwargs={"slug": "test"}),
    )
    assert Comments.objects.all().count() == 1
    instance = Comments.objects.get(pk=1)
    assert str(instance) == "Test comment"


@pytest.mark.django_db
def test_if_comment_form_can_be_submitted_with_missing_data(create_post_in_database):
    c = Client()
    c.post(
        reverse("post_detail", kwargs={"slug": "test"}),
        data={"post_content": "A test of a comment"},
        follow=True,
    )
    assert Comments.objects.all().count() == 0


@pytest.mark.django_db
def test_if_Post_form_can_be_submitted_with_missing_data():
    c = Client()
    c.post(
        reverse("add-post"), data={"title": "", "user": "", "post_content": "Testing"}
    )
    assert Posts.objects.all().count() == 0
