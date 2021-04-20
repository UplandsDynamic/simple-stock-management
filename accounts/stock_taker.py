__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

import logging
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction, IntegrityError
from .models import AccountStockData, AccountData, AccountStockTake, AccountStockTakeLines
from django.db.models import Q, F
from django.contrib.auth.models import User, Group
from .report_generator import generate_report
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger('django')


def stock_taker(stock_data: list) -> bool:
    success = False
    try:
        sterling = Decimal('0.01')
        report_stats = []
        user = stock_data[0].owner if stock_data else None
        """
            async stock taking function.
            Performs the following functions:
                - obtains current running_total_xfer_value & resets to 0
                - obtains current running_total_selling_value
                - obtains current opening_stock & then updates field current_total_units (representing 
                    opening stock for the next stock take)
                
            """
        grand_held_opening_stock = 0
        grand_held_closing_stock = 0
        grand_units_transferred_since_st = 0
        grand_units_recorded_sold_since_st = 0
        grand_units_recorded_shrunk_since_st = 0
        grand_units_unrecorded_hist_diff_since_st = 0
        grand_total_value_recorded_sold_since_st = 0
        grand_total_value_recorded_shrunk_since_st = 0
        grand_total_value_current_xfer_price_unrecorded_change_since_st = 0
        grand_total_value_current_retail_price_unrecorded_change_since_st = 0
        grand_all_time_total_at_actual_xfer_price = 0
        grand_total_xferred_value_since_last_stock_take = 0
        held_stock_value_at_current_xfer_price = 0
        held_stock_value_at_present_retail_price = 0
        with transaction.atomic():  # iterate stock lines & commit all DB changes in single transaction
            for item in stock_data:
                try:
                    # obtain data & do calculations for each line
                    stock_units_differential = item.units_total - item.opening_stock
                    unrecorded_history = item.units_total - \
                        ((item.opening_stock + item.xferred_units) -
                         item.sold_units - item.shrinkage)
                    recorded_sold = Decimal(item.running_total_sold_value).quantize(
                        sterling, ROUND_HALF_UP)
                    recorded_shrinkage = Decimal(item.running_total_shrinkage_value).quantize(
                        sterling, ROUND_HALF_UP)
                    xferred_value = Decimal(item.running_total_xfer_value).quantize(
                        sterling, ROUND_HALF_UP)
                    unknown_history_at_current_xfer_price = Decimal(
                        abs(unrecorded_history) * item.xfer_price).quantize(sterling, ROUND_HALF_UP)
                    unknown_history_at_current_retail_price = Decimal(
                        abs(unrecorded_history) * item.selling_price).quantize(sterling, ROUND_HALF_UP)
                    held_stock_current_xfer_price = Decimal(
                        item.units_total * item.xfer_price).quantize(sterling, ROUND_HALF_UP)
                    held_stock_retail_price = Decimal(
                        item.units_total * item.selling_price).quantize(sterling, ROUND_HALF_UP)
                    # update 'grand totals'
                    grand_held_opening_stock += item.opening_stock
                    grand_held_closing_stock += item.units_total
                    grand_units_transferred_since_st += item.xferred_units
                    grand_units_recorded_sold_since_st += item.sold_units
                    grand_units_recorded_shrunk_since_st += item.shrinkage
                    grand_units_unrecorded_hist_diff_since_st += unrecorded_history
                    grand_total_value_recorded_sold_since_st += recorded_sold
                    grand_total_value_recorded_shrunk_since_st += recorded_shrinkage
                    grand_total_value_current_xfer_price_unrecorded_change_since_st += unknown_history_at_current_xfer_price
                    grand_total_value_current_retail_price_unrecorded_change_since_st += unknown_history_at_current_retail_price
                    grand_total_xferred_value_since_last_stock_take += xferred_value
                    held_stock_value_at_current_xfer_price += held_stock_current_xfer_price
                    held_stock_value_at_present_retail_price += held_stock_retail_price
                    # update account stock data in database
                    AccountStockData.objects.filter(id=item.id).update(
                        opening_stock=item.units_total,
                        xferred_units=0,
                        running_total_xfer_value=0,
                        running_total_sold_value=0,
                        running_total_shrinkage_value=0,
                        shrinkage=0,
                        sold_units=0
                    )
                    # create report stats
                    report_stats.append({
                        'stock_line': item.sku,
                        'stock_desc': item.desc,
                        'xfer_price': item.xfer_price,
                        'retail_price': item.selling_price,
                        'opening_stock': item.opening_stock,
                        'total_units': item.units_total,
                        'units_diff': stock_units_differential,
                        'units_xferred': item.xferred_units,
                        'units_sold': item.sold_units,
                        'units_shrunk': item.shrinkage,
                        'unrecorded': unrecorded_history,
                        'sold_value': recorded_sold,
                        'shrinkage_value': recorded_shrinkage,
                        'xferred_value': xferred_value,
                        'unrecorded_xfer_price': unknown_history_at_current_xfer_price,
                        'unrecorded_retail_price': unknown_history_at_current_retail_price,
                        'held_stock_current_xfer_price': held_stock_current_xfer_price,
                        'held_stock_retail_price': held_stock_retail_price,
                    })
                except IntegrityError as e:
                    logger.error(f'Database update failed!')
                    raise
            """
                calc all-time xfer value for the account
                note: needs to be done before generate_report() so value can be used in the report
                """
            try:
                accountData, created = AccountData.objects.get_or_create(
                    owner=item.owner)
                new_all_time_total_xfer_value = Decimal(accountData.all_time_total_xfer_value).quantize(
                    sterling, ROUND_HALF_UP) + grand_total_xferred_value_since_last_stock_take
            except AccountData.DoesNotExist:
                logger.info(
                    'AccountData all_time_total_xfer_value field did not exist in database ...')
            # generate report for lines
            generate_report(user=user, stats_list=report_stats, type='LINES')
            # generate report for grand totals
            grand_stats = {
                'grand_held_opening_stock': grand_held_opening_stock,
                'grand_held_closing_stock': grand_held_closing_stock,
                'grand_units_transferred_since_st': grand_units_transferred_since_st,
                'grand_units_recorded_sold_since_st': grand_units_recorded_sold_since_st,
                'grand_units_recorded_shrunk_since_st': grand_units_recorded_shrunk_since_st,
                'grand_units_unrecorded_hist_diff_since_st': grand_units_unrecorded_hist_diff_since_st,
                'grand_total_value_recorded_sold_since_st': grand_total_value_recorded_sold_since_st,
                'grand_total_value_recorded_shrunk_since_st': grand_total_value_recorded_shrunk_since_st,
                'grand_total_value_unrecorded_current_xfer_price_since_st': grand_total_value_current_xfer_price_unrecorded_change_since_st,
                'grand_total_value_unrecorded_current_retail_price_since_st': grand_total_value_current_retail_price_unrecorded_change_since_st,
                'grand_total_xferred_value_since_last_stock_take': grand_total_xferred_value_since_last_stock_take,
                'grand_all_time_total_at_actual_xfer_price': new_all_time_total_xfer_value,
                'grand_held_stock_value_at_current_xfer_price': held_stock_value_at_current_xfer_price,
                'grand_held_stock_value_at_present_retail_price': held_stock_value_at_present_retail_price
            }
            generate_report(user=user, stats=grand_stats, type='GRAND')
            # add stock take stats to historical record for user in database
            try:
                # add record to main stock take table
                stock_take_record = AccountStockTake(owner=user, **grand_stats)
                stock_take_record.save()
                # update lines table for the individual lines
                with transaction.atomic():
                    for item in report_stats:
                        AccountStockTakeLines(
                            stock_take=stock_take_record, **item).save()
                # update accountdata
                AccountData.objects.update_or_create(owner=user, defaults={
                    'all_time_total_xfer_value': new_all_time_total_xfer_value,
                })
                # delete lines with zero units from database
                AccountStockData.objects.filter(
                    owner=user, units_total=0).delete()
            except IntegrityError as e:
                logger.error(f'Database update failed')
                raise
        success = True
    except Exception as e:
        raise
        logger.error(
            f'An error has occurred during the stock taking process: {e}')
    return {'success': success, 'user': user}
