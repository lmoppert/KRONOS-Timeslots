""" Tests that verify, the views are working as expected.
"""

from django.test import TestCase
from timeslots.models import Station


class TimeslotsViewProcedureTestCase(TestCase):
    def setUp(self):
        Station.objects.create(
            name="Engstenberg",
            shortdescription="PKW",
            booking_deadline="00:00:00",
            rnvp="00:00:00",
            opened_on_weekend=False,
            multiple_charges=False,
            has_status=False,
            has_klv=False,
        )

    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/timeslots/login/')
        self.assertEqual(resp.status_code, 200)
