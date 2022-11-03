from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


USERNAME = 'UserAuthor'
GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
GROUP_TITLE_NEW = 'Группа2'
GROUP_SLUG_NEW = 'test_slug_new'
GROUP_DESCRIPTION_NEW = 'Тестовая группа 2'
CREATE_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
POST_TEXT = 'Я все успею до жесткого дедлайна'
POST_TEXT_NEW = 'У меня получилось сдать все работы во время!'
REDIRECT_URL = f'{LOGIN_URL}?next={CREATE_POST_URL}'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username=USERNAME,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.group2 = Group.objects.create(
            title=GROUP_TITLE_NEW,
            slug=GROUP_SLUG_NEW,
            description=GROUP_DESCRIPTION_NEW,
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text=POST_TEXT,
            group=cls.group
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_authorized_client_create_post(self):
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            PROFILE_URL
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.get()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text=POST_TEXT,
            ).exists())

    def test_authorized_client_edit_post(self):
        post = Post.objects.create(
            text=POST_TEXT,
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': POST_TEXT_NEW,
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.POST_DETAIL_URL
        )
        self.assertEqual(response.status_code, 200)
        post = response.context['post']
        self.assertTrue(post.text, form_data['text'])
        self.assertTrue(post.author, self.post_author)
        self.assertTrue(post.group.id, form_data['group'])

    def test_guest_client_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
        }
        response = self.guest_client.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, REDIRECT_URL)
        self.assertEqual(Post.objects.count(), posts_count)
