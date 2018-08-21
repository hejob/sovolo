# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from user.models import User, UserActivation
# from base.utils import send_template_mail
from django.utils import timezone
import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Command(BaseCommand):
    help = """
    以下の動作をします。毎日午前9時に一度実行されることを想定しています。
    - アクチベーションコード有効期限を過ぎたもののユーザーを削除する
    """
    # from_address = "reminder@sovol.moe"

    def handle(self, *args, **options):
        self.stdout.write("running...")

        limit = timezone.now() - datetime.timedelta(hours=24)

        acts = UserActivation.objects.filter(created__lt=limit, user__isnull=False)
        for act in acts:
            user = act.user
            if not user is None:
                if user.is_active:
                    self.stdout.write("found user activation already used in key: " + act.key + " with user:" + user.username)
                    # ? remove or set None
                    act.user = None
                    act.save()
                else:
                    self.stdout.write("delete user " + user.username + " in key: " + act.key)
                    # remove user and code
                    user.delete()
                    # ? remove or set None
                    act.user = None
                    act.save()

        self.stdout.write("success...!")
