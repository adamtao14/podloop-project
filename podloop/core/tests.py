from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import Podcast, Category
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


User = get_user_model()
class UserAndPodcastCreationTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'name': 'Test',
            'last_name': 'User',
            'password': 'testpassword',
        }

        self.podcast_data = {
            'name': 'Test Podcast',
            'description': 'This is a test podcast',
            'owner': None,  # To be filled during the test
        }

    def test_user_and_podcast_creation(self):
        # Create a user
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])

        # Create a podcast
        self.podcast_data['owner'] = user
        podcast = Podcast.objects.create(**self.podcast_data)
        self.assertEqual(podcast.name, self.podcast_data['name'])
        self.assertEqual(podcast.description, self.podcast_data['description'])
        self.assertEqual(podcast.owner, user)

        # Add the category to the podcast
        podcast.categories.add(self.category)
        self.assertIn(self.category, podcast.categories.all())

        # Upload a podcast thumbnail (assuming you have an image file)
        thumbnail_file = SimpleUploadedFile(
            'test_thumbnail.jpg',
            b'binarydata',
            content_type='image/jpeg'
        )
        podcast.podcast_thumbnail = thumbnail_file
        podcast.save()

        # Test the uploaded thumbnail
        self.assertIsNotNone(podcast.podcast_thumbnail)

        # Optional: Test the ManyToMany relationship from Category to Podcast
        self.assertIn(podcast, self.category.podcasts.all())

        # Optional: Test the reverse relationship from User to Podcast
        self.assertIn(podcast, user.podcast_set.all())

        # Test creating another podcast with the same name (should raise an IntegrityError)
        with self.assertRaises(IntegrityError):
            Podcast.objects.create(name=self.podcast_data['name'], description='Another podcast', owner=user)

        # Test creating a podcast with a different name (should not raise an exception)
        Podcast.objects.create(name='Another Podcast', description='Different podcast', owner=user)

    def test_category_name_uniqueness(self):
        # Test creating a category with an existing name (should raise an IntegrityError)
        with self.assertRaises(IntegrityError):
            Category.objects.create(name=self.category.name, slug='test-slug')

    def test_podcast_thumbnail_format(self):
        # Test creating a podcast with an invalid thumbnail format (should raise a ValidationError)
        with self.assertRaises(ValidationError):
            thumbnail_file = SimpleUploadedFile(
                'test_thumbnail.gif',
                b'binarydata',
                content_type='image/gif'
            )
            podcast = Podcast(
                name='Test Podcast',
                description='This is a test podcast',
                owner=None,
                podcast_thumbnail=thumbnail_file
            )
            podcast.full_clean()
