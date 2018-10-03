from django.contrib import admin
from .models import *

@admin.register(StockData)
class StockDataAppAdmin(admin.ModelAdmin):
    pass