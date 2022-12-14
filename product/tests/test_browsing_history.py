from django.contrib.auth import get_user_model
from django.urls import reverse
from product.models import ProductCategory, Product, Manufacturer
from product.services import BrowsingHistory
from user.tests import CacheTestCase

User = get_user_model()


class TestBrowsingHistory(CacheTestCase):
    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name="category", slug="category")
        man = Manufacturer.objects.create(name="Manufacturer")

        Product.objects.create(name="product_111", limited=False, category=category, manufacturer=man)
        Product.objects.create(name="product_222", limited=True, category=category, manufacturer=man)
        Product.objects.create(name="product_333", limited=True, category=category, manufacturer=man)
        User.objects.create_user(email="test@test.net", password="qwerty")

    def test_add_product_to_history_for_authorized_user(self):
        user = User.objects.get(email="test@test.net")
        user_history = BrowsingHistory(user)
        self.client.force_login(user)
        products = Product.objects.all()
        self.assertEqual(0, user_history.count)
        for product in products[0:2]:
            self.client.get(reverse("product-page", args=[product.id]))
        self.assertEqual(2, user_history.count)

    def test_not_add_product_to_history_for_unauthorized_user(self):
        user = User.objects.get(email="test@test.net")
        user_history = BrowsingHistory(user)
        products = Product.objects.all()
        self.assertEqual(0, user_history.count)
        for product in products:
            self.client.get(reverse("product-page", args=[product.id]))
        self.assertEqual(0, user_history.count)

    def test_right_order_product_in_history(self):
        user = User.objects.get(email="test@test.net")
        user_history = BrowsingHistory(user)
        self.client.force_login(user)
        products = Product.objects.all().order_by("-id")
        for product in products:
            self.client.get(reverse("product-page", args=[product.id]))
        history_id = [item.id for item in user_history.get_history()]
        self.assertEqual(history_id, sorted(history_id))
        # ?????????????? ?????????????????? ?????????????? ?????? ??????, ???? ???????????? ?????????? ????????????
        last_id = history_id[-1]
        self.client.get(reverse("product-page", args=[last_id]))
        self.assertEqual(last_id, user_history.get_history().first().id)
