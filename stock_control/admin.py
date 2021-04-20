__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

from django.contrib import admin
from .models import *


@admin.register(StockData)
class StockDataAppAdmin(admin.ModelAdmin):
    pass
