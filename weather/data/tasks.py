import requests

from datetime import datetime, timedelta
from celery import shared_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from .serializers import WeatherSerializer
from .models import Weather


class WeatherData:

    def __init__(self):
        self.url = ("https://api.open-meteo.com/v1/forecast?latitude=39.9199&longitude=32.8543&hourly=temperature_2m"
                    "&format=json&timezone")

    @staticmethod
    def get_current_hour():
        now = datetime.now().replace(minute=0)
        return now.strftime('%Y-%m-%dT%H:%M')

    def get_open_meteo_weather_data(self):
        response = requests.get(self.url)
        data = response.json()
        hourly_temperatures = zip(data["hourly"]['time'], data["hourly"]['temperature_2m'])
        return hourly_temperatures

    @staticmethod
    def find_match_for_current_hour(current_hour, temperatures):
        for time, temp in temperatures:
            if time == current_hour:
                return time, temp
        return None, None

    @staticmethod
    def save_weather_data_to_db(date, temp):
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M')
        data = {'date': date, 'temperature': temp}
        if Weather.objects.filter(date=date).exists():
            return None
        serializer = WeatherSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            raise ValueError(serializer.errors)

    def get_temperature(self):
        current_hour = self.get_current_hour()
        temperatures = self.get_open_meteo_weather_data()
        date, temp = self.find_match_for_current_hour(current_hour, temperatures)
        if date and temp:
            self.save_weather_data_to_db(date, temp)


def delete_older_30_days_data():
    older_30_days_data = Weather.objects.filter(created_at__lt=datetime.now() - timedelta(days=30))
    older_30_days_data.delete()


@shared_task
def get_weather_data():
    weather_data = WeatherData()
    weather_data.get_temperature()
    delete_older_30_days_data()


def create_interval_job():
    interval, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)
    PeriodicTask.objects.create(interval=interval, name='Get Weather Data', task='data.tasks.get_weather_data')
    return interval
