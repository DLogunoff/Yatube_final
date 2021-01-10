from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.Danil = User.objects.create(username='Danil')
        cls.group = Group.objects.create(
            title='Название', slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            id=1, author=cls.Danil,
            text='тестовый текст, который больше пятнадцати символов',
            group=cls.group
        )
        cls.field_verboses = {
            'text': 'Текст',
            'group': 'Сообщество',
            'image': 'Прикрепить картинку',
        }
        cls.field_help_texts = {
            'text': 'Поделитесь своими мыслями',
            'group': 'Выберите сообщество (необязательно)',
            'image': 'Если мысли не передать словами (необязательно)'
        }

    def test_verbose_name(self):
        post = PostModelTest.post
        for value, expected in PostModelTest.field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = PostModelTest.post
        for value, expected in PostModelTest.field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_str_post(self):
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название', slug='test-slug',
            description='Тестовое описание'
        )

    def test_str_group(self):
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title)
