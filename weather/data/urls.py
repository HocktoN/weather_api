# urls.py
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import WeatherViewSet, AvgViewSet, FilteredWeatherViewSet, ScheduleViewSet, DataSaverViewSet


temperature_record_list = WeatherViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

temperature_record_detail = WeatherViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


urlpatterns = [
    path('weather/', temperature_record_list, name='temperature-record-list'),
    path('weather/<int:pk>/', temperature_record_detail, name='temperature-record-detail'),
    path('average/<int:days>/', AvgViewSet.as_view({'get': 'average_temperature'}), name='average-temperature'),
    path('filter/', FilteredWeatherViewSet.as_view({'get': 'list'}), name='filtered-weather'),
    path('schedule-job/', ScheduleViewSet.as_view({'get': 'create_schedule'}), name='create-schedule'),
    path('openmeteo-to-db/', DataSaverViewSet.as_view({'get': 'save_data'}), name='save-data'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
