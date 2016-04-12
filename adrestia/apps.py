from __future__ import unicode_literals
from django.apps import AppConfig

class AdrestiaConfig(AppConfig):
    name = 'adrestia'
    verbose_name = 'Adrestia Application'

    def ready(self):
        import adrestia.signals
