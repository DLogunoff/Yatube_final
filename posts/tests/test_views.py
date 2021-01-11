import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
import datetime as dt

from posts.models import Post, Group, Follow


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create_user(username='test')
        cls.user1 = get_user_model().objects.create_user(username='test1')
        cls.image_bytes = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.test_image = SimpleUploadedFile(
            name='test_image.gif',
            content=cls.image_bytes,
            content_type='image/gif'
        )
        cls.group1 = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название1',
            description='Тут не должно быть поста',
            slug='no-posts-here'
        )
        """До введения проверки паджинатора, группу имела только 13ая запись
        и в test_show_correct_context_index был указана .post13. Всё работало
        отлично. После введения проверки паджинатора проверки перестали
        проходить. Помогло изменение в test_show_correct_context_index
        на .post1. Это связано с тем, что я использую setUpClass?
        """
        cls.post1 = Post.objects.create(
            text='а',
            author=cls.user,
            image=cls.test_image,
            group=cls.group1,
        )
        cls.post2 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post3 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post4 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post5 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post6 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post7 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post8 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post9 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post10 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post11 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post12 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.post13 = Post.objects.create(
            text='а',
            author=cls.user,
            group=cls.group1,
            image=cls.test_image,
        )
        cls.form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        cls.templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group', kwargs={'slug': 'test-slug'}),
            'posts/new_post.html': reverse('posts:new_post'),
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech'),
        }
        cls.access_by_name = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }
        cls.today = dt.date.today().strftime('%d-%m-%y')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_pages_uses_correct_templates(self):
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_pages_accessible_by_name(self):
        for reverse_name, expected in self.access_by_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name).status_code
                self.assertEqual(response, expected)

    def test_show_correct_context_create_post(self):
        response = self.authorized_client.get(reverse('posts:new_post'))
        for value, expected in PostViewsTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_correct_context_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        expected_context = PostViewsTest.post1
        post_author = response.context.get('page')[0].author
        post_pub_date = response.context.get('page')[0].pub_date.strftime(
            '%d-%m-%y')
        post_image = response.context.get('page')[0].image
        post_group = response.context.get('page')[0].group
        post_text = response.context.get('page')[0].text
        self.assertEqual(post_author, expected_context.author)
        self.assertEqual(post_text, expected_context.text)
        self.assertIn('media/posts/test_image', post_image.url)
        self.assertEqual(post_group, expected_context.group)
        self.assertEqual(post_pub_date, PostViewsTest.today)

    def test_show_correct_context_group(self):
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'test-slug'})
        )
        expected_context = PostViewsTest.post1
        group_name = response.context.get('group').title
        group_description = response.context.get('group').description
        group_slug = response.context.get('group').slug
        post_author = response.context.get('page')[0].author
        post_pub_date = response.context.get('page')[0].pub_date.strftime(
            '%d-%m-%y')
        post_image = response.context.get('page')[0].image
        post_group = response.context.get('page')[0].group
        post_text = response.context.get('page')[0].text
        self.assertEqual(post_author, expected_context.author)
        self.assertEqual(post_text, expected_context.text)
        self.assertIn('media/posts/test_image', post_image.url)
        self.assertEqual(post_group, expected_context.group)
        self.assertEqual(post_pub_date, PostViewsTest.today)
        self.assertEqual(group_name, expected_context.group.title)
        self.assertEqual(group_description, expected_context.group.description)
        self.assertEqual(group_slug, expected_context.group.slug)

    def test_post_only_in_one_group(self):
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'no-posts-here'})
        )
        self.assertIsNone(response.context.get('post'))

    def test_show_correct_context_edit_post(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={
                        'username': 'test',
                        'post_id': PostViewsTest.post1.id
                    }
                    ))
        for value, expected in PostViewsTest.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_correct_context_profile(self):
        expected_context = PostViewsTest.post1
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={
                    'username': expected_context.author.username
                })
        )
        post_author = response.context.get('post').author
        post_image = response.context.get('page')[0].image
        post_number = response.context.get('count')
        post_pub_date = response.context.get('page')[0].pub_date.strftime(
            '%d-%m-%y')
        post_text = response.context.get('page')[0].text
        self.assertIn('media/posts/test_image', post_image.url)
        self.assertEqual(post_author, expected_context.author)
        self.assertEqual(post_text, expected_context.text)
        self.assertEqual(post_pub_date, PostViewsTest.today)
        self.assertEqual(post_number, Post.objects.count())

    """Имеет ли смысл проверка страницы отдельного поста, если в верхнем 
    тесте мы и так всё проверили?
    """

    def test_show_correct_context_post(self):
        expected_context = PostViewsTest.post1
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={
                'username': expected_context.author.username,
                'post_id': expected_context.id
            }
                    ))
        post_author = response.context.get('post').author
        post_image = response.context.get('post').image
        post_number = response.context.get('count')
        post_pub_date = response.context.get('post').pub_date.strftime(
            '%d-%m-%y')
        post_text = response.context.get('post').text
        self.assertIn('media/posts/test_image', post_image.url)
        self.assertEqual(post_author, expected_context.author)
        self.assertEqual(post_text, expected_context.text)
        self.assertEqual(post_pub_date, PostViewsTest.today)
        self.assertEqual(post_number, Post.objects.count())

    def test_authorized_can_subscribe_unsubscribe(self):
        post = PostViewsTest.post1
        count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': 'test1',
            }
                    ))
        self.assertEqual(Follow.objects.count(), count + 1)
        test_follow = Follow.objects.filter(user=self.user, author=self.user1)
        test_follow.delete()
        self.assertEqual(Follow.objects.count(), count)

    def test_subcribe_feed(self):
        test_post = Post.objects.create(author=self.user1, text='aaaa')
        test_follow = Follow.objects.create(user=self.user, author=self.user1)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post_text = response.context.get('post').text
        self.assertEqual(post_text, test_post.text)
        post_author = response.context.get('post').author
        self.assertEqual(post_author, test_post.author)
