from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag 

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
  """Test the publicly available tags API"""

  def setUp(self):
    self.client = APIClient()
  
  def test_login_required(self):
    """test that login is required for tag retrieval"""
    res = self.client.get(TAGS_URL)
    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
  """Test the authorized user tags API"""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
      'test@cyrx.org', 'password42'
    )
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_retrieve_tags(self):
    """Test tags retrieval"""
    Tag.objects.create(user=self.user, name='Meat')
    Tag.objects.create(user=self.user, name='Vegetarian')

    res = self.client.get(TAGS_URL)
    tags = Tag.objects.all().order_by('-name')
    serializer = TagSerializer(tags, many=True)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_tags_limited_to_user(self):
    """Test that tags returned are for the authenticated user only"""
    user2 = get_user_model().objects.create_user(
      'testuser2@cyrx.org', 'tester2'
    )
    Tag.objects.create(user=user2, name='fruity')
    tag = Tag.objects.create(user=self.user, name='Comfort food' )

    res = self.client.get(TAGS_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data), 1)
    self.assertEqual(res.data[0]['name'], tag.name)




