from django.conf.urls import patterns, include, url
from django.contrib import admin
from data_browser import lucid_tracking, api, views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'data_browser.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'view/get/file_details$', views.file_details),
    url(r'view/get/frame_image$', views.frame_image),
    url(r'view/get/xyc$', views.get_xyc),
    url(r'view/', views.main),
    # API
    url(r'api/get/frames', api.get_frames),
    url(r'api/get/data_files', api.get_data_files),
    # LUCID tracking
    url(r'tracking/get/position$', lucid_tracking.get_position),
    url(r'tracking/get/line$', lucid_tracking.get_line),
    url(r'tracking', lucid_tracking.main),
    # Default landing page
    url(r'$', views.root)
)




