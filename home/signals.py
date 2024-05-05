from django.db.models.signals import post_save
from django.dispatch import receiver

from home.models import Company
from utils.tasks import parse_all_shareholders

@receiver(post_save, sender=Company)
def print_test(sender, instance, created, **kwargs):
    if created:
        parse_all_shareholders.delay(pk=instance.pk)