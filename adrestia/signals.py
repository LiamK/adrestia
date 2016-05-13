import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Delegate, Candidate

log = logging.getLogger(__name__)

# Signals
@receiver(post_save, sender=Delegate)
def add_opponents(sender, instance, **kwargs):
    candidates = instance.get_opponents()
    if candidates:
        instance.opponents.add(*candidates)

@receiver(post_save, sender=Candidate)
def add_delegate(sender, instance, **kwargs):
    delegate = instance.get_delegate()
    if delegate:
        instance.delegate_set.add(delegate)
