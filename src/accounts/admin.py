from django.contrib import admin
from .models import *

@admin.register(AccountStockData)
class AccountStockDataAppAdmin(admin.ModelAdmin):
    pass

@admin.register(AccountData)
class AccountDataAppAdmin(admin.ModelAdmin):
    pass
    
@admin.register(AccountStockTake)
class AccountStockTakeAdmin(admin.ModelAdmin):
    pass

@admin.register(AccountStockTakeLines)
class AccountStockTakeLinesAdmin(admin.ModelAdmin):
    pass