from rest_framework.test import APITestCase
from django.urls import reverse
from inventory.models import Product, Customer

# Create your tests here.


class OrderTestCase(APITestCase):
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Klant", email="test@klant.nl"
        )

        self.product = Product.objects.create(
            name="Test Product", price=100, stock=5
        )

    def test_order_stock(self):
        url = reverse('order-list')  
        data = {
            "customer_id": self.customer.id,
            "items": [{"product_id": self.product.id, "quantity": 2}]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)


    def test_order_quantity(self):
        url = reverse('order-list')
        data = {
            "customer_id": self.customer.id,
            "items": [{"product_id": self.product.id, "quantity": 10}]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("There is not enough in stock", str(response.data))