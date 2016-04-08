import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Delegate

log = logging.getLogger(__name__)

log.debug('importing %s', __name__)

# Signals
@receiver(post_save, sender=Delegate)
def add_opponents(sender, instance, **kwargs):
    log.debug('Saving %s', instance)
    candidates = instance.get_opponents()
    if candidates:
        log.info('%s', candidates)
        instance.opponents.add(*candidates)
