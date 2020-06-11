from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Post


class TestPosts(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah",
            email="connor.s@skynet.com",
            password="12345"
        )
        self.text_1 = "text one"
        self.text_2 = "text two"
        self.text_4 = "text four"
        self.post = Post.objects.create(text=self.text_1, author=self.user)

    def test_edited_post_appeared(self):
        self.client.post(
            reverse(
                "post_edit",
                kwargs={"username": self.user, "post_id": self.post.pk},
            ),
            {"text": self.text_2},
        )
        response = self.client.get(
            reverse("profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(len(Post.objects.all()), 1)
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )

    def test_posts_display(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("new"),
            {"text": self.text_4}
        )
        response = self.client.get(
            reverse(
                "post",
                kwargs={"username": self.user, "post_id": self.post.pk},
            )
        )
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )
        response = self.client.get(reverse("index"))
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )
        response = self.client.get(
            reverse(
                "profile",
                kwargs={"username": self.user}
            )
        )
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )

    def test_group_posts(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("new"),
            {"text": self.text_4, "group": "cats"}
        )
        response = self.client.get(
            reverse(
                "group_posts",
                kwargs={"slug": "cats"}
            )
        )
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )


class TestPostsCreation(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah1",
            email="connor1.s@skynet.com",
            password="123456"
        )
        self.text_3 = "text three"

    def test_new_post(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("new"),
            {"text": self.text_3}
        )
        response = self.client.get(reverse("new"))
        self.assertEqual(len(Post.objects.all()), 1)
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )

    def test_unlogged_cant_post(self):
        self.client.post(
            reverse("new")
        )
        self.assertEqual(len(Post.objects.all()), 0)


class TestProfiles(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah12",
            email="connor12.s@skynet.com",
            password="1234567"
        )
        self.text_5 = "text_five"
        self.post_2 = Post.objects.create(text=self.text_5, author=self.user)

    def test_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("profile", kwargs={"username": self.user})
        )
        self.assertEqual(response.status_code, 200) 
        self.assertIn(self.user, User.objects.all())
        with self.assertRaises(Exception, msg="Такого пользователя не существует"):
            response = self.client.get( 
                reverse("profile", kwargs={"username": "sara"})
            )
