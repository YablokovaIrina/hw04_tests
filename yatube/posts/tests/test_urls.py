from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.user1 = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Группа1',
            slug='group_one',
            description='Тестовая группа номер 1',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_pages_guest_access(self):
        url_names = [
            '/',
            '/group/group_one/',
            '/profile/TestAuthor/',
            f'/posts/{self.post.pk}/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_authorized_author_access(self):
        url_names = [
            '/',
            '/group/group_one/',
            '/profile/TestAuthor/',
            f'/posts/{self.post.pk}/',
            f'/posts/{self.post.pk}/edit/',
            '/create/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, 200)

    def test_list_url_redirect_guest(self):
        url_names_redirects = {
            f'/posts/{self.post.pk}/edit/': (
                f'/auth/login/?next=/posts/{self.post.pk}/edit/'
            ),
            '/create/': '/auth/login/?next=/create/',
        }
        for url, redirect_address in url_names_redirects.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect_address)

    def test_redirect_not_author(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/',
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_urls_authorized_client_author_corret_templates(self):
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/group_one/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_names_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
