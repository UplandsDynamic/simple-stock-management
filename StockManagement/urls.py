from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include, static
from rest_framework.authtoken import views as authviews

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/api-token-auth/', authviews.obtain_auth_token),
    url(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v2/accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^api/v2/', include('stock_control.urls', namespace='api')),
]