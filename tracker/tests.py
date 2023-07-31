import json
from _decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from tracker.models import User, History, Intake

client = APIClient()


def format_decimal(number: Decimal) -> str:
    """
    Formata um número em decimal com duas casas após a vírgula
    """

    return '%.2f' % number


class CreateNewUserTest(APITestCase):
    def setUp(self) -> None:
        self.valid_payload = {
            "name": "Antônio João",
            "weight": 60
        }

        self.invalid_payload = {
            "name": "Antônio João",
            "weight": "aaaaaaaa"
        }

    def test_create_valid_user(self):
        response = client.post(
            reverse('user-list'),
            json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        response = client.post(
            reverse('user-list'),
            json.dumps(self.invalid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserDrinkTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            name="Antônio João", weight=75
        )

        self.valid_payload = {
            "quantity": 300
        }

        self.invalid_payload = {
            "quantity": None
        }

    def test_valid_user_drink(self):
        response = client.post(
            reverse('user-drink', kwargs={'pk': self.user.pk}),
            json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_user_drink(self):
        response = client.post(
            reverse('user-drink', kwargs={'pk': self.user.pk}),
            json.dumps(self.invalid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserResumeTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            name="Antônio João", weight=75
        )

        self.history_point = History.objects.create(
            user_id=self.user, goal=self.user.daily_goal
        )

        self.intake = Intake.objects.create(
            history_id=self.history_point, quantity=500
        )

    def test_resume(self):
        response = client.get(
            reverse('user-resume', kwargs={'pk': self.user.pk}),
        )
        body = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            body['date'],
            timezone.now().strftime('%Y-%m-%d')
        )
        self.assertEqual(len(body['intakes']), 1)
        self.assertEqual(
            body['goal'],
            format_decimal(self.user.daily_goal)
        )
        self.assertEqual(
            body['amount_taken'],
            format_decimal(self.intake.quantity)
        )
        self.assertEqual(
            body['amount_left'],
            format_decimal(self.user.daily_goal - self.intake.quantity)
        )
        self.assertEqual(body['reached_goal'], False)

    def test_invalid_resume_date(self):
        response = client.get(
            f"{reverse('user-resume', kwargs={'pk': self.user.pk})}?date=invalid_date",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_history(self):
        response = client.get(
            reverse('user-history', kwargs={'pk': self.user.pk}),
        )
        body = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['date'], timezone.now().strftime('%Y-%m-%d'))
