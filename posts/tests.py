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
        self.assertEqual(Post.objects.count(), 1)
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
        self.assertEqual(Post.objects.count(), 1)
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
        self.assertEqual(Post.objects.count(), 0)


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


class TestSubFunctions(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah122",
            email="connor122.s@skynet.com",
            password="12345678"
        )
        self.user2 = User.objects.create_user(
            username="connor122",
            email="connor122.s@skynet.com",
            password="123456789"
        )
        self.user3 = User.objects.create_user(
            username="connor666",
            email="connor666.s@skynet.com",
            password="1234567890"
        )
        self.text_6 = "text six"

    def test_auth_sub(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "profile_follow",
                kwargs={"username": self.user2}
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse(
                "profile_unfollow",
                kwargs={"username": self.user2}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_sub_posts(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse(
                "profile_follow",
                kwargs={"username": self.user2}
            )
        )
        self.client.force_login(self.user2)
        self.client.post(
            reverse("new"),
            {"text": self.text_6}
        )
        response = self.client.get(reverse("follow_index"))
        self.assertContains(
            response,
            "text",
            count=None,
            status_code=200,
            msg_prefix='',
            html=False
        )
        self.client.force_login(self.user3)
        response = self.client.get(reverse("follow_index"))
        self.assertNotContains(
            response,
            self.text_6,
            status_code=200,
            msg_prefix='',
            html=False
        )


class TestComments(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sar122",
            email="connor1262.s@skynet.com",
            password="12345678152"
        )
        self.user2 = User.objects.create_user(
            username="s122",
            email="c122.s@skynet.com",
            password="123456789648"
        )
        self.text_7 = "text seven"
        self.post = Post.objects.create(text=self.text_7, author=self.user)

    def test_auth_can_comment(self):
        response = self.client.post(
            reverse(
                "add_comment",
                kwargs={"username": self.user, "post_id": self.post.pk}
            )
        )
        self.assertTemplateNotUsed(response=response, template_name="comments.html", msg_prefix='')
        self.client.force_login(self.user2)
        self.client.post(
            reverse(
                "add_comment",
                kwargs={"username": self.user, "post_id": self.post.pk}
                ),
            {"text": self.text_7}
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "post",
                kwargs={"username": self.user, "post_id": self.post.pk}
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
