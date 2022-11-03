from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE
from posts.models import Group, Post, User

GROUP_TITLE = 'Группа1'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'Тестовая группа 1'
POST_TEXT = 'Тестовый текст'
USERNAME = 'Username'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
POSTS_ON_OTHER_PAGE = 3
SECOND_PAGE = '?page=2'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
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
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.id, self.post.id)

    def test_show_correct_contex(self):
        urls = [
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 1)
                self.check_post_info(response.context['page_obj'][0])
        
    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.check_post_info(response.context['page_obj'][0])

    def test_groups_page_show_correct_context(self):
        response = self.authorized_client.get(
            GROUP_LIST_URL
        )
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(self.group.title, GROUP_TITLE)
        self.assertEqual(self.group.slug, GROUP_SLUG)
        self.assertEqual(self.group.description, GROUP_DESCRIPTION)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.check_post_info(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            PROFILE_URL
        )
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.check_post_info(response.context['page_obj'][0])

    def test_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            self.POST_DETAIL_URL)
        self.check_post_info(response.context['post'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=USERNAME,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.POSTS_NUM = POSTS_ON_PAGE + POSTS_ON_OTHER_PAGE
        Post.objects.bulk_create(
            Post(text=f'Post {i}', author=cls.user, group=cls.group)
            for i in range(cls.POSTS_NUM)
        )

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_on_pages(self):
        pages_and_records = {
            INDEX_URL: POSTS_ON_PAGE,
            INDEX_URL + SECOND_PAGE: self.POSTS_NUM - POSTS_ON_PAGE,
            GROUP_LIST_URL: POSTS_ON_PAGE,
            GROUP_LIST_URL + SECOND_PAGE: self.POSTS_NUM - POSTS_ON_PAGE,
            PROFILE_URL: POSTS_ON_PAGE,
            PROFILE_URL + SECOND_PAGE: self.POSTS_NUM - POSTS_ON_PAGE,
        }
        for page, records in pages_and_records.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(len(response.context['page_obj']), records)
