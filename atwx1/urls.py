
from django.urls import re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
				 re_path(r'^$', views.index, name = 'index'),
				 re_path(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")), 
				 re_path(r'^forecast', views.forecast, name = 'forecast'),
				 re_path(r'^about', views.about, name = 'about'),
				 re_path(r'^other', views.other, name = 'other'),				 
				 re_path(r'^disclaimer', views.disclaimer, name = 'disclaimer'),
				 re_path(r'^learn/(?P<learn_topic>[^\s]+)', views.learn, name = 'learn'),
				 re_path(r'^learn', views.learn, name = 'learn'), ]
