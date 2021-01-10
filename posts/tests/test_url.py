from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = get_user_model().objects.create_user(username='test_user1')
        cls.user2 = get_user_model().objects.create_user(username='test_user2')
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user1,
            group=cls.group
        )
        cls.guest_access = {
            reverse('posts:index'): 200,
            reverse('posts:group', kwargs={'slug': cls.group.slug}): 200,
            reverse('posts:profile',
                    kwargs={'username': cls.user1.username}): 200,
            reverse(
                'posts:post', kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }): 200,
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
            'not-exists/not_exists/': 404,
            reverse(
                'posts:add_comment',
                kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }): 302,
        }
        cls.redirects = {
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }): reverse(
                'posts:profile',
                kwargs={
                    'username': cls.user1.username
                }),
            reverse('posts:new_post'): '/auth/login/?next=/new/',
        }
        cls.author_access = {
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }): 200,
        }
        cls.authorized_access = {
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }): reverse(
                'posts:profile',
                kwargs={
                    'username': cls.user1.username
                }),

        }
        cls.templates_urls = {
            'index.html': reverse('posts:index'),
            'group.html': reverse(
                'posts:group',
                kwargs={'slug': cls.group.slug}
            ),
            'posts/new_post.html': reverse('posts:new_post'),
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech'),
        }
        cls.templates_urls_author = {
            'posts/new_post.html': reverse(
                'posts:post_edit',
                kwargs={
                    'username': cls.user1.username,
                    'post_id': cls.post.id
                }),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)  # автор
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)  # не автор

    def test_guest_client_access(self):
        for url, expected in PostURLTests.guest_access.items():
            response = self.guest_client.get(url).status_code
            with self.subTest(value=url):
                self.assertEqual(response, expected)

    def test_redirects(self):
        for url, expected in PostURLTests.redirects.items():
            response = self.guest_client.get(url, follow=True)
            with self.subTest(value=url):
                self.assertRedirects(response, expected)

    def test_author_access(self):
        """Задел на будущее, если на потребуется
         проверять еще что-то для автора
        """
        for url, expected in PostURLTests.author_access.items():
            response = self.authorized_client1.get(url).status_code
            with self.subTest(value=url):
                self.assertEqual(response, expected)

    def test_not_author_access(self):
        for url, redirect in PostURLTests.authorized_access.items():
            response = self.authorized_client2.get(url, follow=True)
            with self.subTest(value=url):
                self.assertRedirects(response, redirect)

    def test_correct_templates(self):
        for template, url in PostURLTests.templates_urls.items():
            with self.subTest():
                response = self.authorized_client2.get(url)
                self.assertTemplateUsed(response, template)

    def test_correct_templates_author(self):
        for template, url in PostURLTests.templates_urls_author.items():
            with self.subTest():
                response = self.authorized_client1.get(url)
                self.assertTemplateUsed(response, template)
