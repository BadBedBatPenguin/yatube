from django.test import TestCase
from django.urls import reverse

GROUP_SLUG = 'test-slug'
USERNAME = 'TestUser'
POST_ID = 1


class PostsURLTests(TestCase):

    def test_routes(self):
        cases = [
            ['index', [], '/'],
            ['group_list', [GROUP_SLUG], f'/group/{GROUP_SLUG}/'],
            ['profile', [USERNAME], f'/profile/{USERNAME}/'],
            ['post_detail', [POST_ID], f'/posts/{POST_ID}/'],
            ['post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'],
            ['post_create', [], '/create/'],
            ['add_comment', [POST_ID], f'/posts/{POST_ID}/comment'],
            ['follow_index', [], '/follow/'],
            ['profile_follow', [USERNAME], f'/profile/{USERNAME}/follow/'],
            ['profile_unfollow', [USERNAME], f'/profile/{USERNAME}/unfollow/'],
        ]
        for route, prm, url in cases:
            with self.subTest(url=url):
                self.assertEqual(url, reverse(
                    f'posts:{route}',
                    args=prm
                ))
