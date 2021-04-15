from django.conf.urls import url, include
from . import views

# final url patterns (everything included)
urlpatterns = [
    url(r'^(/?)$', views.FrontendView.as_view(), name='frontend-view'),
]
