from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        for i in range(13):
            Post.objects.create(
                text='Тестовый текст c текстом',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Паджинатор на первой странице работает корректно"""
        adress_list = {
            'posts:index': '',
            'posts:group_list': {'slug': 'test-group'},
            'posts:profile': {'username': 'tester'}
        }
        for adress, value in adress_list.items():
            with self.subTest(adress=adress):
                response = self.client.get(reverse(adress, kwargs=value))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        """Паджинатор на второй странице работает корректно"""
        adress_list = {
            'posts:index': '',
            'posts:group_list': {'slug': 'test-group'},
            'posts:profile': {'username': 'tester'}
        }
        for adress, value in adress_list.items():
            with self.subTest(adress=adress):
                response = self.client.get(
                    reverse(adress, kwargs=value) + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)
