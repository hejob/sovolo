# coding=utf-8
from django.db import models
from django.urls import reverse
from base.models import AbstractBaseModel
from django.conf import settings

from django.db.models import Q
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _

import os
import math


class Policy(AbstractBaseModel):
    # Numbers are arbitrary
    name = models.CharField(max_length=100)
    html = models.TextField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
