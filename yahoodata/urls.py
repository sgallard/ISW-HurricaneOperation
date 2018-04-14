from django.urls import path

from . import views

app_name = 'yahoodata'

urlpatterns = [
    path('', views.index, name='index'),
    path('getData',views.getdata, name='getData')
]
