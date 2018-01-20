from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView, TemplateView

import oda.apps.rest.urls as rest_urls
import oda.apps.users.urls as user_urls
from oda.apps.odaweb import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/static/home/index.html')),
    url(r'^doc$', RedirectView.as_view(url='/static/doc/html/index.html')),

    #Legacy Redirects
    url(r'^odaweb/run_hex.*$',  RedirectView.as_view(url='/odaweb/')),
    url(r'^odaweb/file_upload.*$', RedirectView.as_view(url='/odaweb/')),

    #Django Admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^superadmin/', include(admin.site.urls)),

    url(r'^odaweb/_save$', views.save),
    url(r'^odaweb/_upload$', views.upload),
    url(r'^odaweb/_fileinfo$', views.fileinfo),
    url(r'^odaweb/_instdoc$', views.instdoc),
    url(r'^odaweb/optionsview', views.options_form),
    url(r'^odaweb/_download', views.download_text_listing),

    #User Dealing with URL
    # this url is used to generate email content
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset,
        name='password_reset_confirm'),
    url(r'^password-reset/$',
        TemplateView.as_view(template_name="password_reset.html"),
        name='password-reset'),
    url(r'^password-reset/confirm/$',
        TemplateView.as_view(template_name="password_reset_confirm2.html"),
        name='password-reset-confirm'),

    url(r'^odaweb/auth/', include('rest_auth.urls')),
    url(r'^odaweb/auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^user/', include(user_urls.urlpatterns)),

    url(r'^odaweb/api/', include(rest_urls.urlpatterns)),

    #url(r'^oda/connect/(?P<share_name>\w{0,16})$$', views.connect, name='connect'),
    url(r'^oda/', views.oda, name='oda'),
    url(r'^odaweb/(?P<short_name>\w{0,16})$$', views.ace, name='index_without_revision'),
    url(r'^odaweb/(?P<short_name>\w{0,16})/(?P<version>\w{0,16})$$', views.ace, name="index"),
]
