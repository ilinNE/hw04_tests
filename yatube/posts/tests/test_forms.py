from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.not_author = User.objects.create_user(username='passenger')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        self.post = Post.objects.create(
            text='Исходный текст',
            author=self.user,
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        """Валидная форма создает пост"""
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )

        new_post = Post.objects.select_related('group').order_by('-id')[0]
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id, }),
            data=form_data,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])

    def test_unauthorized_user_create_post(self):
        posts_count = Post.objects.count()
        """Неавторизованый пользователь не может создать пост"""
        form_data = {
            'text': 'Жалкая попытка',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_unauthorized_edit_post(self):
        """Неавторизованый пользователь не может редактировать пост"""
        source_text = self.post.text
        sorce_group = self.post.group
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, source_text)
        self.assertEqual(edited_post.group, sorce_group)

    def test_not_author_edit_post(self):
        """Не автор поста не может редактировать пост"""
        source_text = self.post.text
        sorce_group = self.post.group
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        self.not_author_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, source_text)
        self.assertEqual(edited_post.group, sorce_group)
