# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.test import skipIfDBFeature, TestCase

from timeslots.models import UserProfile
