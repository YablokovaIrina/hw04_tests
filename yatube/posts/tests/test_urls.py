from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group, User

USERNAME = 'UserAuthor'
USERNAME_2 = 'User'
GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
POST_TEXT = 'Я все успею до жесткого дедлайна'

INDEX_URL = reverse('posts:index')
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': GROUP_SLUG})
LOGIN_URL = reverse('users:login')                      

POST_CREATE_REDIRECT = f'{LOGIN_URL}?next={POST_CREATE_URL}'

class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user2 = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.POST_EDIT_REDIRECT = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_pages_urls_at_desired_location_posts_for_users(self):
        urls_names = [
            [INDEX_URL, self.guest_client, 200],
            [GROUP_LIST_URL, self.guest_client, 200],
            [self.POST_DETAIL_URL, self.guest_client, 200],
            [POST_CREATE_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [PROFILE_URL, self.authorized_client, 200],
            [POST_CREATE_URL, self.authorized_client, 200],
            [self.POST_EDIT_URL, self.authorized_client, 302],
            [self.POST_EDIT_URL, self.authorized_client_author, 200],
            ['/unexisting_page/', self.guest_client, 404],   
        ]
        for url, client, code in urls_names:
            with self.subTest(url=url, client=client, code=code):
                self.assertEqual(client.get(url).status_code, code)

    def test_urls_redirects_posts(self):
        urls_redirect = [
            [POST_CREATE_URL, self.guest_client, POST_CREATE_REDIRECT],
            [self.POST_EDIT_URL, self.guest_client, self.POST_EDIT_REDIRECT],
            [self.POST_EDIT_URL, self.authorized_client, self.POST_DETAIL_URL],
        ]
        for url, client, redirect in urls_redirect:
            with self.subTest(url=url, client=client, redirect=redirect):
                self.assertRedirects(client.get(url), redirect)
                
    def test_urls_uses_correct_templates(self):
        template_url_names = [
            [INDEX_URL, self.guest_client, 'posts/index.html'],
            [PROFILE_URL, self.guest_client, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest_client, 'posts/post_detail.html'],
            [POST_CREATE_URL, self.authorized_client_author, 'posts/create_post.html'],
            [GROUP_LIST_URL, self.authorized_client_author, 'posts/group_list.html'],
            [self.POST_EDIT_URL, self.authorized_client_author, 'posts/create_post.html']
        ]
        for url, client, template in template_url_names:
            with self.subTest(url=url, client=client, template=template):
                self.assertTemplateUsed(client.get(url), template)
