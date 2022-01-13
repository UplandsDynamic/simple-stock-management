from django.contrib import admin
from django.urls import path
from django.conf.urls import include, static
from django.urls import re_path
from rest_framework.authtoken import views as authviews

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/api-token-auth/', authviews.obtain_auth_token),
    re_path(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/v2/accounts/', include('accounts.urls', namespace='accounts')),
    re_path(r'^api/v2/', include('stock_control.urls', namespace='api')),
]