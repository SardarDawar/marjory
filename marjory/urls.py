from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.views.static import serve 

urlpatterns = [
    # django admin urls
    path('admin/', admin.site.urls),

    # my app urls
    path('logout/', auth_views.LogoutView.as_view(template_name='common/logout.html'), name='logout'),
    path('', include('common.urls')),
    path('', include('scripts.urls')),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

handler404 = 'common.views.handler404'
handler400 = 'common.views.handler400'
handler403 = 'common.views.handler403'
handler500 = 'common.views.handler500'

if settings.DEBUG:
    urlpatterns+= static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    from common.views import handler404 as hndlr404, handler400 as hndlr400, handler403 as hndlr403, handler500 as hndlr500
    urlpatterns += [
        re_path(r'^400/$', hndlr400, kwargs={'exception': Exception('')}),
        re_path(r'^403/$', hndlr403, kwargs={'exception': Exception('')}),
        re_path(r'^404/$', hndlr404, kwargs={'exception': Exception('')}),
        re_path(r'^500/$', hndlr500),
    ]