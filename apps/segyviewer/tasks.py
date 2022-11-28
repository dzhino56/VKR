from __future__ import unicode_literals, absolute_import

from celery import shared_task


@shared_task
def add(x, y):
    return x + y
