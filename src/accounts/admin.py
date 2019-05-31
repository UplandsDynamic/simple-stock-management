from django.contrib import admin
from .models import *

@admin.register(AccountStockData)
class AccountStockDataAppAdmin(admin.ModelAdmin):
    pass
