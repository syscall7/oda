from django.conf.urls import include, url

from  oda.apps.users import views

urlpatterns = [
    url(r'files/$', views.files)
]