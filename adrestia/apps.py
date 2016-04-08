from __future__ import unicode_literals
from django.apps import AppConfig

print 'importing', __name__

class AdrestiaConfig(AppConfig):
    name = 'adrestia'
    verbose_name = 'Adrestia Application'

    def ready(self):
        print 'calling ready'
        import adrestia.signals
