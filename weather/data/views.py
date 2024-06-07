import requests

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta

from .models import Weather
from .serializers import WeatherSerializer
from .tasks import create_interval_job


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class WeatherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing the weather records.
    """
    permission_classes = [IsAuthenticated]
    queryset = Weather.objects.all().order_by('-date')
    serializer_class = WeatherSerializer
    pagination_class = Pagination


class FilteredWeatherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing the filtered weather records by date range.
    """

    permission_classes = [IsAuthenticated]
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Weather.objects.all().order_by('-date')
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset


class AvgViewSet(viewsets.ViewSet):
    """
    ViewSet for calculating the average temperature of the last n days.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def average_temperature(self, request, days):
        data = Weather.objects.filter(date__gt=datetime.now() - timedelta(days=days))
        total = sum(record.temperature for record in data)
        if data:
            average = total / len(data)
            return Response({'Days': days, 'Average': average})
        else:
            return Response({'error': 'No data found for the specified number of days'}, status=404)


class ScheduleViewSet(viewsets.ViewSet):
    """
    ViewSet for creating an interval job to get the weather data every hour.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def create_schedule(self, request):
        try:
            create_interval_job()
            return Response("Interval job created! It will run every hour and get Ankara's weather data.",
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class DataSaverViewSet(viewsets.ViewSet):
    """
    ViewSet get open-meteo data and save it to the database by date range.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def save_data(self, request):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if not start_date or not end_date:
            return Response("Please provide start_date and end_date parameters in the format of 'YYYY-MM-DD'",
                            status=status.HTTP_400_BAD_REQUEST)

        url = (f"https://api.open-meteo.com/v1/forecast?latitude=39.9199&longitude=32.8543&hourly=temperature_2m"
               f"&start_date={start_date}&end_date={end_date}&format=json&timezone")

        response = requests.get(url)
        data = response.json()
        hourly_temperatures = zip(data["hourly"]['time'], data["hourly"]['temperature_2m'])

        for time, temp in hourly_temperatures:
            date = datetime.strptime(time, '%Y-%m-%dT%H:%M')
            data = {'date': date, 'temperature': temp}
            serializer = WeatherSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise ValueError(serializer.errors)
        return Response(f"{start_date} to {end_date} data saved to database successfully!",
                        status=status.HTTP_200_OK)
