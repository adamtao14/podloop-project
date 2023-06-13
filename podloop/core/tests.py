from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import Podcast, Category
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.urls import reverse
User = get_user_model()


class category_test(TestCase):
    def setUp(self):
        # Set up initial data for tests
        self.category_data = {
            'name': "test category",
            'slug': 'test-category'
        }    
        
    def test_create_category(self):
        # Test the creation of a category
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, self.category_data['name'])
        self.assertEqual(category.slug, self.category_data['slug'])

    def test_category_name_uniqueness(self):
        # Test the creation of a category with the same name as one already made
        Category.objects.create(**self.category_data)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(**self.category_data)
                
    def tearDown(self):
        # Delete all objects from the database
        Category.objects.all().delete()
        super().tearDown()
                
class user_test(TestCase):
    def setUp(self):
        # Set up initial data for tests
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'name': 'Test',
            'last_name': 'User',
            'password': 'testpassword',
        }
        
    def test_create_user(self):
        # Test the creation of a user
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])

    def test_user_email_uniqueness(self):
        # Test the creation of a user with the same email as one already made
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(**self.user_data)    
                
    def tearDown(self):
        # Delete all objects from the database
        User.objects.all().delete()
        super().tearDown()
        
class podcast_test(TestCase):
    def setUp(self):
        # Set up initial data for tests
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
        }

        self.category_data = {
            'name': "test category",
            'slug': 'test-category'
        }


    def test_podcast_thumbnail_invalid_format(self):
        # Test creating a podcast with an invalid thumbnail format (should raise a ValidationError)
        with self.assertRaises(ValidationError):
            thumbnail_file = SimpleUploadedFile(
                'test_thumbnail.mp3',
                b'binarydata',
                content_type='audio/mpeg'
            )
            podcast = Podcast(
                name='Test Podcast',
                description='This is a test podcast',
                owner=None,
                podcast_thumbnail=thumbnail_file
            )
            podcast.full_clean()

    def test_create_podcast_with_category(self):
        # Create a category
        category = Category.objects.create(**self.category_data)
        # Create a user
        user = User.objects.create_user(**self.user_data)

        # Upload a podcast thumbnail (assuming you have an image file)
        thumbnail_file = SimpleUploadedFile(
            'test_thumbnail.jpg',
            b'binarydata',
            content_type='image/jpeg'
        )
        # Create a podcast
        self.podcast_data['owner'] = user
        self.podcast_data['podcast_thumbnail'] = thumbnail_file
        podcast = Podcast.objects.create(**self.podcast_data)

        # Add the category to the podcast
        podcast.categories.add(category)
        podcast.save()

        # Test if the category got added to podcast
        self.assertIn(category, podcast.categories.all())

        # Test the uploaded thumbnail
        self.assertIsNotNone(podcast.podcast_thumbnail)

        # Test the ManyToMany relationship from Category to Podcast
        self.assertIn(podcast, category.podcasts.all())

    def tearDown(self):
        # Delete all objects from the database
        Category.objects.all().delete()
        User.objects.all().delete()
        Podcast.objects.all().delete()
        super().tearDown()

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='be@*qpOBW&bY',
            email='testuser@gmail.com',
            name='test',
            last_name='user'
        )
        self.user_2 = User.objects.create_user(
            username='testuser2',
            password='be@*qpOBW&bY',
            email='testuser2@gmail.com',
            name='test',
            last_name='user'
        )
        self.podcast_data = {
            'name': 'My Podcast',
            'description': 'This is a test podcast',
            'slug':'my-podcast'
        }

        self.category_data = {
            'name': "test category",
            'slug': 'test-category'
        }

    def test_login_success_and_home_view(self):
        # Log in the user
        self.client.force_login(self.user)

        # Make a GET request to the view URL
        response = self.client.get(reverse('core:profile'))

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected content
        self.assertContains(response, "Update profile")

    def test_anonymus_home_view(self):

        # Make a GET request to the view URL
        response = self.client.get(reverse('core:profile'))

        # Assert that the response has a status code of 302 
        # This is because if you are not logged in, you get redireceted to login
        self.assertEqual(response.status_code, 302)

    
    
    def test_podcast_edit_page_view(self):
        # Log in the user
        self.client.force_login(self.user)
        # Create a category
        category = Category.objects.create(**self.category_data)
        # Upload a podcast thumbnail (assuming you have an image file)
        thumbnail_file = SimpleUploadedFile(
            'test_thumbnail.jpg',
            b'binarydata',
            content_type='image/jpeg'
        )
        # Create a podcast
        self.podcast_data['owner'] = self.user
        self.podcast_data['podcast_thumbnail'] = thumbnail_file
        podcast = Podcast.objects.create(**self.podcast_data)

        # Add the category to the podcast
        podcast.categories.add(category)
        podcast.save()
        
        response = self.client.get(reverse('core:podcast-edit', kwargs={'slug':self.podcast_data['slug']}))

        # Assert that the response has a status code of 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the expected content
        self.assertContains(response, 'Edit <span class="text-warning">'+self.podcast_data['name']+'</span>')
        
    def test_podcast_edit_page_view_not_authorized(self):
        # Create a category
        category = Category.objects.create(**self.category_data)
        # Upload a podcast thumbnail (assuming you have an image file)
        thumbnail_file = SimpleUploadedFile(
            'test_thumbnail.jpg',
            b'binarydata',
            content_type='image/jpeg'
        )
        # Create a podcast
        self.podcast_data['owner'] = self.user
        self.podcast_data['podcast_thumbnail'] = thumbnail_file
        podcast = Podcast.objects.create(**self.podcast_data)

        # Add the category to the podcast
        podcast.categories.add(category)
        podcast.save()
        # Log in the user
        self.client.force_login(self.user_2)
        
        response = self.client.get(reverse('core:podcast-edit', kwargs={'slug':self.podcast_data['slug']}))

        # Assert that the response has a status code of 401, this is because user_2 is not the owner
        self.assertEqual(response.status_code, 401)


    def tearDown(self):
        self.client.logout()
        # Delete all objects from the database
        Category.objects.all().delete()
        User.objects.all().delete()
        Podcast.objects.all().delete()
        super().tearDown()