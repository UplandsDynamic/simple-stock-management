from django.conf.urls import url, include
from rest_framework import routers, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as authviews

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
    'delete': 'destroy'
    }
"""
functional_view_urlpatterns = [
    url('^v1/change-password/(?P<username>[a-zA-Z0-9.].+)/$', views.PasswordUpdateViewSet.as_view(
        {'patch': 'partial_update'})),
    url('^v1/stock/$', views.StockDataViewSet.as_view(
        {'get': 'list', 'post': 'create'})),
    url('^v1/stock/(?P<pk>\d+)/$', views.StockDataViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy', 'put': 'update'})),
    url('^v1/stock/latest/$', views.StockDataViewSet.as_view(
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
    url(r'^(/?)$', schema_view),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
    url(r'^schema(/?)$', schema_view),
    # url(r'^v1/', include(router.urls)),
]
