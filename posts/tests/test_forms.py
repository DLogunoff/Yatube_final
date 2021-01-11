import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Comment


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.image_bytes = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.author_user = get_user_model().objects.create_user(username='test')
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.author_user,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='test1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_added_to_db(self):
        posts_count = Post.objects.count()
        upload = SimpleUploadedFile(
            name='test_image.gif',
            content=PostFormTests.image_bytes,
            content_type='image/gif',
        )
        form_data = {
            'text': 'самый тестовый текст',
            'image': upload,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True,
        )
        created_post = Post.objects.filter(
            text__exact='самый тестовый текст')[0]
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.text, 'самый тестовый текст')

    def test_post_edit(self):
        test_post = PostFormTests.post
        form_data = {'text': 'измененный текст'}
        response1 = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'username': test_post.author.username,
                'post_id': test_post.id
            }
        ),
            data=form_data,
            follow=True,
        )
        test_post.text = form_data['text']
        test_post.save()
        response2 = self.authorized_client.get(reverse(
            'posts:post',
            kwargs={
                'username': test_post.author.username,
                'post_id': test_post.id
            }
        ))
        edited_post_text = response2.context.get('post').text
        self.assertRedirects(response1, reverse(
            'posts:profile',
            kwargs={'username': test_post.author.username}
        ))
        self.assertEqual(test_post.text, edited_post_text)

    def test_add_comment(self):
        test_post = self.post
        count = Comment.objects.count()
        form_data = {'text': 'комментарий'}
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={
                'username': test_post.author.username,
                'post_id': test_post.id
            }
        ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), count + 1)
        comment_text = response.context.get('comments')[0].text
        self.assertEqual(comment_text, form_data['text'])
        comment_author = response.context.get('comments')[0].author
        self.assertEqual(comment_author, self.user)
