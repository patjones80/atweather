"""atweather URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/

	Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import re_path, include
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.views.generic import TemplateView

from atwx1 import views

# overrides default error handlers
handler404 = 'atwx1.views.http_404'
handler500 = 'atwx1.views.http_500'

urlpatterns = [
				re_path(r'^admin/', admin.site.urls),  
				re_path(r'^', include('atwx1.urls')), 
				re_path(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")), ]
