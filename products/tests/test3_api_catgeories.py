import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category


class CategoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _unique_payload(self):
        suffix = uuid.uuid4().hex[:8]
        return {"name": f"Category {suffix}", "slug": f"category-{suffix}"}

    def _auth_as(self, password="pass12345"):
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        suffix = uuid.uuid4().hex[:8]
        identifier = f"zaintheuser{suffix}@example.com" if username_field == "email" else f"zaintheuser{suffix}"
        create_kwargs = {username_field: identifier}

        if username_field != "email" and any(f.name == "email" for f in User._meta.fields):
            create_kwargs["email"] = f"catuser{suffix}@example.com" 

        User.objects.create_user(**create_kwargs, password=password)
        token_payload = {username_field: identifier, "password": password}
        res = self.client.post(reverse("token_obtain_pair"), token_payload, format="json")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            msg=f"Token obtain failed: {res.status_code} {getattr(res, 'data', res.content)}",
        )
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_anonymous_list_categories_200(self):
        Category.objects.create(**self._unique_payload())
        res = self.client.get(reverse("category-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_anonymous_detail_category_200(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.get(reverse("category-detail", args=[cat.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_anonymous_create_category_blocked(self):
        res = self.client.post(reverse("category-list"), self._unique_payload(), format="json")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_patch_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.patch(
            reverse("category-detail", args=[cat.id]),
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_delete_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.delete(reverse("category-detail", args=[cat.id]))
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_auth_create_category_201_and_persists(self):
        self._auth_as()
        payload = self._unique_payload()
        res = self.client.post(reverse("category-list"), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["slug"], payload["slug"])

        created_id = res.data["id"]
        self.assertTrue(Category.objects.filter(id=created_id).exists())

        get_res = self.client.get(reverse("category-detail", args=[created_id]))
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["name"], payload["name"])
        self.assertEqual(get_res.data["slug"], payload["slug"])

    def test_auth_patch_category_200_and_persists(self):
        cat = Category.objects.create(**self._unique_payload())
        self._auth_as()

        new_name = f"{cat.name} Updated"
        res = self.client.patch(
            reverse("category-detail", args=[cat.id]),
            {"name": new_name},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        cat.refresh_from_db()
        self.assertEqual(cat.name, new_name)

    def test_auth_delete_204_and_get_after_delete_404(self):
        cat = Category.objects.create(**self._unique_payload())
        self._auth_as()

        del_res = self.client.delete(reverse("category-detail", args=[cat.id]))
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        get_res = self.client.get(reverse("category-detail", args=[cat.id]))
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_create_duplicate_slug_fails(self):
        self._auth_as()
        payload = {"name": "A", "slug": "dup-slug"}
        self.client.post(reverse("category-list"), payload, format="json")
        res = self.client.post(
            reverse("category-list"),
            {"name": "B", "slug": "dup-slug"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
