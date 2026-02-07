import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category


class CategoryAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        suffix = uuid.uuid4().hex[:8]
        identifier = f"zaintheuser{suffix}@example.com" if username_field == "email" else f"zaintheuser{suffix}"
        create_kwargs = {username_field: identifier}

        if username_field != "email" and any(f.name == "email" for f in User._meta.fields):
            create_kwargs["email"] = f"catuser{suffix}@example.com"

        cls.password = "Pass1234!Strong"
        cls.user = User.objects.create_user(**create_kwargs, password=cls.password)
        cls.login_identifier = identifier
        cls.username_field = username_field

    def setUp(self):
        self.client = APIClient()

    def _unique_payload(self):
        suffix = uuid.uuid4().hex[:8]
        return {"name": f"Category {suffix}", "slug": f"category-{suffix}"}

    def _categories_list_url(self):
        return reverse("category-list")

    def _categories_detail_url(self, pk):
        return reverse("category-detail", args=[pk])

    def _token_url(self):
        try:
            return reverse("token_obtain_pair")
        except NoReverseMatch as e:
            raise AssertionError("JWT token endpoint name 'token_obtain_pair' is missing/broken in urls.py") from e

    def _resp_debug(self, res):
        data = getattr(res, "data", None)
        if data is not None:
            return f"data={data}"
        try:
            return f"content={res.content.decode(errors='replace')}"
        except Exception:
            return f"raw_content={res.content!r}"

    def _auth_client(self):
        token_payload = {self.username_field: self.login_identifier, "password": self.password}
        res = self.client.post(self._token_url(), token_payload, format="json")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            msg=f"Token obtain failed: {res.status_code} {self._resp_debug(res)}",
        )
        token = res.data["access"]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_anonymous_list_categories_200(self):
        Category.objects.create(**self._unique_payload())
        res = self.client.get(self._categories_list_url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res["Content-Type"].startswith("application/json"))
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, res.data)

    def test_anonymous_detail_category_200(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.get(self._categories_detail_url(cat.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res["Content-Type"].startswith("application/json"))

    def test_anonymous_create_category_blocked(self):
        res = self.client.post(self._categories_list_url(), self._unique_payload(), format="json")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_patch_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.patch(
            self._categories_detail_url(cat.id),
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_delete_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.delete(self._categories_detail_url(cat.id))
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_auth_create_category_201_and_persists(self):
        auth_client = self._auth_client()
        payload = self._unique_payload()
        res = auth_client.post(self._categories_list_url(), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["slug"], payload["slug"])

        created_id = res.data["id"]
        self.assertTrue(Category.objects.filter(id=created_id).exists())

        get_res = self.client.get(self._categories_detail_url(created_id))
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["name"], payload["name"])
        self.assertEqual(get_res.data["slug"], payload["slug"])

    def test_auth_patch_category_200_and_persists(self):
        cat = Category.objects.create(**self._unique_payload())
        auth_client = self._auth_client()

        new_name = f"{cat.name} Updated"
        res = auth_client.patch(
            self._categories_detail_url(cat.id),
            {"name": new_name},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        cat.refresh_from_db()
        self.assertEqual(cat.name, new_name)

    def test_auth_delete_204_and_get_after_delete_404(self):
        cat = Category.objects.create(**self._unique_payload())
        auth_client = self._auth_client()

        del_res = auth_client.delete(self._categories_detail_url(cat.id))
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        get_res = self.client.get(self._categories_detail_url(cat.id))
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_create_duplicate_slug_fails(self):
        auth_client = self._auth_client()
        payload = {"name": "A", "slug": "dup-slug"}
        auth_client.post(self._categories_list_url(), payload, format="json")
        res = auth_client.post(
            self._categories_list_url(),
            {"name": "B", "slug": "dup-slug"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
