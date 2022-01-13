__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.schemas import get_schema_view

app_name = 'stock-control'

"""
set up the routers for the viewset class based views
"""
# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'stock', views.StockDataViewSet)  # define manually to allow DRF unit testing (router testing buggy)
# router.register(r'change-password', views.PasswordUpdateViewSet)  # define manually below to allow dots in usernames

"""
set up the url patterns for the functional views and simple class based views
Note: Mapping for actions (used in as_view), are:
    {
    'get': 'retrieve'  # to retrieve one object, as spec by pk passed in url param, e.g. /stock/1
    'get': 'list' # to list all objects, e.g. /stock/
    'get': 'latest' # CUSTOM action (defined in views.StockDataViewSet.latest(), routed /api/v1/stock/latest/ (below)).
    'post': 'create'
    'put': 'update',
    'patch': 'partial_update',
    'patch': 'perform_single_update', # CUSTOM ACTION, routed in /api/v1/stock/<PK> (with path)
    'patch': 'perform_bulk_partial_update',  # CUSTOM ACTION, routed in /api/v1/stock/ (without the ID in the path)
    'delete': 'destroy',
    }
"""
functional_view_urlpatterns = [
    re_path('^change-password/(?P<username>[a-zA-Z0-9.].+)/$', views.PasswordUpdateViewSet.as_view(
        {'patch': 'partial_update'})),
    re_path(r'^logout/$', views.Logout.as_view()),
    re_path('^stock/$', views.StockDataViewSet.as_view(
        {'get': 'list', 'post': 'create', 'patch': 'perform_bulk_partial_update'})),
    re_path('^stock/(?P<pk>\d+)/$', views.StockDataViewSet.as_view(
        {'get': 'retrieve', 'patch': 'perform_single_update', 'delete': 'destroy', 'put': 'update'})),
    re_path('^stock/latest/$', views.StockDataViewSet.as_view(
        {'get': 'latest'})),
]

"""
add in extra urls to provide option to add content type suffix to requests 
(as handled by the api_view wrapper, in views.py)
"""
urlpatterns = format_suffix_patterns(functional_view_urlpatterns)

"""
set up schema
"""
schema_view = get_schema_view(
    title='Stock Data API',
    permission_classes=[permissions.IsAdminUser]  # not public api, so only allow admin to view the schema
)

# final url patterns (everything included)
urlpatterns += [
    re_path(r'^(/?)$', schema_view),
    re_path(r'^schema(/?)$', schema_view),
    # re_path(r'^v1/', include(router.urls)),
]
