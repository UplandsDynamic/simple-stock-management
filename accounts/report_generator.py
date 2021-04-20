__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

import logging
import datetime
import locale
import pytz
import markdown
from email_service.email import SendEmail
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils.formats import date_format

# Get an instance of a logger
logger = logging.getLogger('django')


def generate_report(user: User, type: str, stats: dict = None, stats_list: list = None, ) -> bool:
    # create report emails
    report_email = {'plain': None, 'html': None}
    line_reports = []
    if type == 'LINES':
        for stats in stats_list:
            line_reports.append(
                f"""
## Units

- Stock line: {stats['stock_line']}
- Description: {stats['stock_desc']}
- Opening stock units: {stats['opening_stock']}
- Closing stock units: {stats['total_units']}
- Stock units change: {stats['units_diff']}
- Units transferred since last stock take: {stats['units_xferred']}
- Units recorded sold since last stock take: {stats['units_sold']}
- Units recorded shrinkage since last stock take: {stats['units_shrunk']}
- Units +/- with unrecorded history since last stock take: {stats['unrecorded']} [i.e. unrecorded sales, unrecorded transfers, unrecorded loss]

## Values

- Current unit transfer value: {locale.currency(stats['xfer_price'], grouping=True)}
- Current unit retail price: {locale.currency(stats['retail_price'], grouping=True)}
- Total value of units recorded sold since last stock take: {locale.currency(stats['sold_value'], grouping=True)}
- Total value of units recorded shrinkage since last stock take: {locale.currency(stats['shrinkage_value'], grouping=True)}
- Total value of units transferred since last stock take: {locale.currency(stats['xferred_value'], grouping=True)}
- Total value of units +/- with unrecorded history since last stock take, at present xfer price: {
    locale.currency(stats['unrecorded_xfer_price'], grouping=True)}
- Total value of units with unrecorded history since last stock take, at present retail price: {
    locale.currency(stats['unrecorded_retail_price'], grouping=True)} [i.e. unrecorded sales, unrecorded transfers, shrinkage]
- Current total held stock transfer value at present xfer price: {locale.currency(stats['held_stock_current_xfer_price'], grouping=True)}
- Current total held stock retail value at present retail price: {locale.currency(stats['held_stock_retail_price'], grouping=True)}

"""
            )
            report_email['plain'] = f"""
# LINE TOTALS FOR ACCOUNT: {user.username}

Report generated: {date_format(datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)), format='DATETIME_FORMAT', use_l10n=True)}

---
{'---'.join(line_reports)}
"""
            report_email['html'] = markdown.markdown(report_email['plain'])
            report_email[
                'subject'] = f'[STOCK MANAGEMENT] Stock Take: Lines Report for {user.username}'
    if type == 'GRAND':
        report_email['plain'] = f"""
# WAREHOUSE GRAND TOTALS FOR ACCOUNT: {user.username}

Report generated: {date_format(datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)), format='DATETIME_FORMAT', use_l10n=True)}

---
## Units

- Opening stock: {stats['grand_held_opening_stock']}
- Closing stock: {stats['grand_held_closing_stock']}
- Transferred since last stock take: {stats['grand_units_transferred_since_st']}
- Recorded sold since last stock take: {stats['grand_units_recorded_sold_since_st']}
- Recorded shrinkage since last stock take: {stats['grand_units_recorded_shrunk_since_st']}
- Change (with unrecorded history) since last stock take: {stats['grand_units_unrecorded_hist_diff_since_st']} [i.e. unrecorded sales, unrecorded transfers, unrecorded loss]

## Values

- Recorded sold since last stock take: {locale.currency(stats['grand_total_value_recorded_sold_since_st'], grouping=True)}
- Recorded shrinkage since last stock take: {locale.currency(stats['grand_total_value_recorded_shrunk_since_st'], grouping=True)}
- Total value change of units with unrecorded history since last stock take at current transfer value: {
    locale.currency(stats['grand_total_value_unrecorded_current_xfer_price_since_st'], grouping=True)
}
- Total value of units with unrecorded history since last stock take at current retail value: {
    locale.currency(stats['grand_total_value_unrecorded_current_retail_price_since_st'], grouping=True)
}  [i.e. unrecorded sales, unrecorded transfers, unrecorded loss]
- Total transfer value since last stock take (at actual xfer prices): {
    locale.currency(stats['grand_total_xferred_value_since_last_stock_take'], grouping=True)}
- All time total transfer value (at actual xfer prices): {locale.currency(stats['grand_all_time_total_at_actual_xfer_price'], grouping=True)}
- Held stock at current transfer price: {locale.currency(stats['grand_held_stock_value_at_current_xfer_price'], grouping=True)}
- Held stock at current retail price: {locale.currency(stats['grand_held_stock_value_at_present_retail_price'], grouping=True)}
---
"""
        report_email['html'] = markdown.markdown(report_email['plain'])
        report_email[
            'subject'] = f'[STOCK MANAGEMENT] Stock Take: Grand Totals Report for {user.username}'
    try:
        # dispatch email
        dispatch_email(user=user, pre_formatted=report_email)
    except Exception as e:
        logger.error(
            f'An error occurred whilst attempting to send email: {e}')
    return True


def dispatch_email(records=None, user=None, pre_formatted: dict = None) -> bool:
    """
    method to dispatch email on successful update
    """
    SendEmail().compose(pre_formatted=pre_formatted, user=user, subject=pre_formatted['subject'],
                        notification_type=SendEmail.EmailType.STOCK_TAKE)
    return True
