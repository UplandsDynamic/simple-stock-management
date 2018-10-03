from django.conf.urls import url, include
from rest_framework import routers, renderers, permissions
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as authviews

# from rest_framework.renderers import CoreJSONRenderer

"""
set up the routers for the viewset class based views
"""
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'stock', views.StockDataViewSet)
# router.register(r'change-password', views.PasswordUpdateViewSet)  # define manually below to allow dots in usernames

"""
set up the url patterns for the functional views and simple class based views
"""
functional_view_urlpatterns = [
    # url(r'^api/some_action/', views.SomeActionClass.as_view(), name='someactionclassview'),
    url('^v1/change-password/(?P<username>[a-zA-Z0-9.].+)/$', views.PasswordUpdateViewSet.as_view(
        {'patch': 'partial_update'})),
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
    url(r'^v1/', include(router.urls)),
    url(r'^schema(/?)$', schema_view),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
]
