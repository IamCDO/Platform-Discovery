from django.contrib.auth import get_user_model
from django.test import TestCase

from .forms import ProductForm
from .models import Business, BusinessCategory, Product


class CategoryAndBusinessUiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='storeowner',
            email='owner@example.com',
            password='securepass123',
        )
        self.category = BusinessCategory.objects.create(
            name='Technology',
            slug='technology',
            description='Student tech products and services.',
        )
        self.business = Business.objects.create(
            owner=self.user,
            category=self.category,
            name='Pixel Cart',
            slug='pixel-cart',
            location='Online',
            email='shop@example.com',
            description='Student tech store.',
            status=Business.STATUS_APPROVED,
        )

    def test_category_detail_page_renders_businesses(self):
        response = self.client.get('/category/technology/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pixel Cart')
        self.assertContains(response, 'Technology')

    def test_business_portal_page_renders_for_business_owner(self):
        self.client.login(username='storeowner', password='securepass123')
        response = self.client.get('/business-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Business Portal')
        self.assertContains(response, 'Pixel Cart')

    def test_category_slug_is_generated_when_missing(self):
        category = BusinessCategory(name='Tech Accessories')
        category.save()
        self.assertEqual(category.slug, 'tech-accessories')
        self.assertEqual(category.pk, BusinessCategory.objects.get(slug='tech-accessories').pk)

    def test_business_slug_is_sanitized_for_url(self):
        self.business.name = "Developer's Haven"
        self.business.slug = ""
        self.business.save()
        self.assertEqual(self.business.slug, 'developers-haven')
        response = self.client.get('/business/developers-haven/')
        self.assertEqual(response.status_code, 200)

    def test_product_image_url_field_is_saved_and_form_includes_it(self):
        product = Product.objects.create(
            business=self.business,
            name='Wireless Mouse',
            description='Slim wireless mouse for student setups.',
            price=45.00,
            discount_percent=10,
            stock=12,
            is_available=True,
            image_url='https://example.com/mouse.jpg',
        )

        self.assertEqual(product.image_url, 'https://example.com/mouse.jpg')

        form = ProductForm()
        self.assertIn('image_url', form.fields)

    def test_profile_page_shows_login_and_signup_modes(self):
        login_response = self.client.get('/profile/')
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, "If you don't have an account")
        self.assertContains(login_response, 'click here to sign up')

        signup_response = self.client.get('/profile/?mode=signup')
        self.assertEqual(signup_response.status_code, 200)
        self.assertContains(signup_response, 'Create your account')
        self.assertContains(signup_response, 'Already have an account?')

    def test_profile_login_preserves_next_url(self):
        response = self.client.post('/profile/', {
            'mode': 'login',
            'username': 'storeowner',
            'password': 'securepass123',
            'next': '/cart/',
        })

        self.assertRedirects(response, '/cart/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_cart_quantity_controls_update_and_remove_item(self):
        product = Product.objects.create(
            business=self.business,
            name='Wireless Mouse',
            description='Slim wireless mouse for student setups.',
            price=45.00,
            stock=2,
        )
        session = self.client.session
        session['cart'] = {str(product.pk): 1}
        session.save()

        response = self.client.post('/cart/', {'product_id': product.pk, 'action': 'increase'})
        self.assertRedirects(response, '/cart/')
        self.assertEqual(self.client.session['cart'][str(product.pk)], 2)

        response = self.client.post('/cart/', {'product_id': product.pk, 'action': 'increase'})
        self.assertRedirects(response, '/cart/')
        self.assertEqual(self.client.session['cart'][str(product.pk)], 2)

        response = self.client.post('/cart/', {'product_id': product.pk, 'action': 'decrease'})
        self.assertRedirects(response, '/cart/')
        self.assertEqual(self.client.session['cart'][str(product.pk)], 1)

        response = self.client.post('/cart/', {'product_id': product.pk, 'action': 'decrease'})
        self.assertRedirects(response, '/cart/')
        self.assertNotIn(str(product.pk), self.client.session['cart'])
