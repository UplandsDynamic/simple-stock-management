__Author__ = """By:  Aninstance
www.githup.com/Aninstance/simple-stock-management"""
__Copyright__ = "Copyright (c) 2021 Aninstance"
__Version__ = "Version 1.0"

from django.contrib import admin
from .models import *

@admin.register(StockData)
class StockDataAppAdmin(admin.ModelAdmin):
    pass