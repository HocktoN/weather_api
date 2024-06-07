from django.db import models


class Weather(models.Model):
    date = models.DateTimeField(null=False, blank=False)
    temperature = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"<Weather object: {self.date} ({self.temperature})>"
