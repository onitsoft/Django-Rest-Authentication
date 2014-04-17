from django.conf.urls import patterns, include, url

from django.contrib import admin
from . import api_urls

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'vita_auth.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_urls)),
    # url(r'^auth-api/', include('rest_framework.urls', namespace='rest_framework')),
)
