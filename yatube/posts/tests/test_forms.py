from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        Post.objects.create(
            text='Исходный текст',
            author=self.user,
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        """Валидная форма создает пост"""
        form_data = {
            'text': 'sdfsdfd',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=('testuser',))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        form_data = {
            'text': 'Измененный текст',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
        )
        post = Post.objects.get(pk=1)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=('1',))
        )
        self.assertEqual(post.text, 'Измененный текст')
