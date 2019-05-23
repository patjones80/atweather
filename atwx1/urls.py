
from django.conf.urls import url
from . import views

urlpatterns = [
				 url(r'^$', views.index, name = 'index'),
				 url(r'^forecast', views.forecast, name = 'forecast'),
				 url(r'^about', views.about, name = 'about'),
				 url(r'^disclaimer', views.disclaimer, name = 'disclaimer'),
				 url(r'^learn/(?P<learn_topic>[^\s]+)', views.learn, name = 'learn'),
				 url(r'^learn', views.learn, name = 'learn'), ]
