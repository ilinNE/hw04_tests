from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author(self):
        """Проверка страницы Об авторе"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        """Проверка сраницы технологий"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'

        )
        cls.post = Post.objects.create(
            text='Тестовый текст c текстом',
            author=cls.author,
            group=cls.test_group

        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostsURLTests.author)

    def test_posts_urls_exists_at_desired_locations(self):
        """Проверяем общедоступные страницы"""
        adress_list = [
            '/',
            f'/group/{PostsURLTests.test_group.slug}/',
            f'/profile/{PostsURLTests.author.username}/',
            f'/posts/{PostsURLTests.post.pk}/'
        ]
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_create_url_for_authorized_user_exist(self):
        """Страница создания нового поста доступна
        для авторизованого пользовавтеля
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_post_url_for_author_exist(self):
        """Страница редактирования поста доступна для автора поста"""
        response = self.authorized_author_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_redirects_url(self):
        """С адресов с ограниченым доступом пользолватель
        без достурпа перенаправляется по правильным адресам
        """
        post_id = PostsURLTests.post.pk
        redirect_dict = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{post_id}/edit/': (
                f'/auth/login/?next=/posts/{post_id}/edit/'
            ),
        }
        for adress, redirect in redirect_dict.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_templates_exist(self):
        """По всем адресам находятся правильные шаблоны"""
        slug = PostsURLTests.test_group.slug
        username = PostsURLTests.author.username
        post_id = PostsURLTests.post.pk
        templates_dict = {
            '/': 'posts/index.html',
            f'/group/{slug}/': 'posts/group_list.html',
            f'/profile/{username}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_dict.items():
            with self.subTest(adress=adress):
                response = self.authorized_author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexsisted_page(self):
        """Несуществующая страница показывает код 404"""
        response = self.authorized_client.get('/unexcisted/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
