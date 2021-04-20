__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

import logging
from anymail.exceptions import AnymailAPIError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Get an instance of a logger
logger = logging.getLogger('django')


class SendEmail:
    DEFAULT_SUBJECT = '[WEBSITE EMAIL]'

    class EmailType:
        STOCK_TRANSFER = 'Notification email sent when stock has been transferred'
        ACCOUNT_STOCK_UPDATE = 'Notification email sent when an account\'s stock data is updated'
        STOCK_TAKE = 'Stock take report'

    def __init__(self):
        self.email_invalid = False

    def email_validate(self, email=None):
        try:
            validate_email(email)
        except ValidationError as v:
            logger.error(f'Email {email} invalid!: {v}')
            self.email_invalid = True

    def send(self, body_plaintext=None, body_html=None, email_to=None, email_from=None, subject=None):
        email_to = [] if not isinstance(email_to, list) else email_to
        if body_plaintext and body_html and email_to:
            # validate email addresses first
            for c, e in enumerate(email_to):
                if e == '':  # remove any empty email addresses
                    email_to.pop(c)
                self.email_validate(e)
            self.email_validate(email_from)
            if not self.email_invalid:
                try:
                    if settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_on']:
                        msg = EmailMultiAlternatives(
                            subject if subject else SendEmail.DEFAULT_SUBJECT,
                            body_plaintext,
                            email_from,
                            email_to
                        )
                        msg.attach_alternative(body_html, "text/html")
                        # you can set any other options on msg here, then...
                        msg.send()
                    else:
                        logger.info(
                            f'Notifications are set to: '
                            f'{settings.STOCK_MANAGEMENT_OPTIONS["email"]}.'
                            f' If in live mode, notification email would be sent to: '
                            f'{[a for a in email_to] if email_to else "Nobody!"}'
                            f'The plaintext email body would read: {body_plaintext}'
                            f'The html email body would read: {body_html}')
                    return True
                except AnymailAPIError as e:
                    logger.error(f'An error has occurred in sending email: {e.describe_response()}')
                except Exception as e:
                    logger.error(f'Error sending email: {e}')
        return False

    def compose(
            self, records: dict = None, user: User = None, pre_formatted: dict = None, notification_type: str = None,
            subject: str = None) -> send:
        """
        :param records: updated records
        :param user: user making the update
        :param notification_type: type of notification to send
        :return: True|False
        This method composes notification emails, then sends them through the send() method.
        """
        record_list_success = []
        record_list_fail = []

        def compose_body_success(successful_updates=None):
            body_plaintext = []
            body_html = []
            if successful_updates:
                for stock_record in successful_updates:
                    formatted_time = stock_record['record_updated'].strftime('%d %b %Y %H:%M:%S %Z')
                    body_plaintext.append(f"""
                                    The following transfer has taken place on {formatted_time}:
                                    - Transfer to: {user} [{user.email}]
                                    - Stock line details:
                                      - SKU: {stock_record['sku']}
                                      - Description: {stock_record['desc']}
                                      - Units transferred: {stock_record['units_to_transfer']}
                                      - Unit price: {stock_record['unit_price']}
                                    """)
                    body_html.append(f"""
                                    <p>The following transfer has taken place on {formatted_time}</p>
                                    <ul>
                                    <li>Transfer to: {user} [<a href="mailto:{user.email}">{user.email}</a>]</li>
                                    <li>Stock line details:
                                    <ul>
                                    <li>SKU: {stock_record['sku']}</li>
                                    <li>Description: {stock_record['desc']}</li>
                                    <li>Units transferred: {stock_record['units_to_transfer']}</li>
                                    <li>Unit price: {stock_record['unit_price']}</li>
                                    </ul>
                                    </li>
                                    </ul>
                                    """)
            return body_plaintext, body_html

        def compose_body_fail(failed_updates=None):
            body_plaintext = []
            body_html = []
            if failed_updates:
                for stock_record in failed_updates:
                    # details_plain = '\n'.join([f'- {k}: {v}' for k, v in stock_record.items()])
                    # details_html = ''.join([f'<li>{k}: {v}</li>' for k, v in stock_record.items()])
                    # compose errors descriptions
                    reason = ', '.join([err for err in stock_record['error']])
                    # compose the plaintext body
                    body_plaintext.append(f"""
                                    The following transfer request failed:
                                    - Transfer to: {user} [{user.email}]
                                    - Reason for failure: {reason}
                                    - Request details:
                                      - SKU: {stock_record['data']['sku']}
                                      - Description: {stock_record['data']['desc']}
                                      - Unit price: {stock_record['data']['unit_price']}
                                      - Requested transfer: {stock_record['data']['units_to_transfer']} units
                                      - Units in stock: {stock_record['data']['units_total']}
                                    """)
                    # compose the html body
                    body_html.append(f"""
                                    <p>The following transfer request failed:</p>
                                    <ul>
                                    <li>Transfer to: {user} [<a href="mailto:{user.email}">{user.email}</a>]</li>
                                    <li>Reason for failure: {reason}</li>
                                    <li>Stock line details:
                                    <ul>
                                    <li>SKU: {stock_record['data']['sku']}</li>
                                    <li>Description: {stock_record['data']['desc']}</li>
                                    <li>Unit price: {stock_record['data']['unit_price']}</li>
                                    <li>Requested transfer: {stock_record['data']['units_to_transfer']} units</li>
                                    <li>Units in stock: {stock_record['data']['units_total']}</li>
                                    </ul>
                                    </li>
                                    </ul>
                                    """)
            return body_plaintext, body_html
        try:
            if notification_type == SendEmail.EmailType.STOCK_TAKE:
                """
                email stock take report to administrators + requester
                """
                admin_email_addr = User.objects.filter(groups__name='administrators').values_list(
                    'email', flat=True)  # list of all stock administrator's email addresses
                recipient_list = [a for a in admin_email_addr] if \
                    admin_email_addr and settings.STOCK_MANAGEMENT_OPTIONS['email'][
                        'notifications_to_administrators'] else []
                if settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_to_transfer_requester']:
                    recipient_list.append(user.email)  # add the transfer requester's email address
                recipient_list = list(set(recipient_list))  # remove any dupes
                """
                Send email notification to admins (and requester (e.g. store manager) if configured to receive in settings.py).
                """
                if recipient_list:
                    html_start = "<html><head></head><body>"
                    html_divider = "<br/><hr/><br/>"
                    html_end = "</body><footer><hr></footer></html>"
                    plaintext = pre_formatted['plain']
                    html = html_start + pre_formatted['html'] + html_end
                    return self.send(body_plaintext=plaintext, body_html=html,
                                     email_to=recipient_list,
                                     email_from=settings.DEFAULT_FROM_EMAIL,
                                     subject=subject)
            elif notification_type == SendEmail.EmailType.STOCK_TRANSFER:
                """
                email notification to administrators + requester
                """
                admin_email_addr = User.objects.filter(groups__name='administrators').values_list('email',
                                                                                                  flat=True)
                # list of all stock administrator's email addresses
                recipient_list = [a for a in admin_email_addr] if \
                    admin_email_addr and settings.STOCK_MANAGEMENT_OPTIONS['email'][
                        'notifications_to_administrators'] else []
                if settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_to_transfer_requester']:
                    recipient_list.append(user.email)  # add the transfer requester's email address
                recipient_list = list(set(recipient_list))  # remove any dupes
                """
                Send email notification to admins (and requester if configured to receive in settings.py).
                Email is only sent on stock transfer, not editing (determined by a truthy units_to_transfer submission).
                """
                # add successful updates and failure response records to lists, ready for return in email notification
                for r in records:
                    if r['data']:
                        record_list_success.append(r['data']) if r['success'] else record_list_fail.append(r)
                if recipient_list:
                    success_body_plaintext, success_body_html = compose_body_success(
                        successful_updates=record_list_success)
                    fail_body_plaintext, fail_body_html = compose_body_fail(failed_updates=record_list_fail)
                    html_start = "<html><head></head><body>"
                    html_divider = "<br/><hr/><br/>"
                    html_end = "</body><footer><hr></footer></html>"

                    plaintext = f"""
                    SUCCESSFUL UPDATES

                    {' '.join([b for b in success_body_plaintext])}

                    -------

                    FAILED UPDATES

                    {' '.join([b for b in fail_body_plaintext]) if fail_body_plaintext else 'None! All good!'}
                    """

                    html = html_start + '<h2>Successful transfer requests</h2>' + ''.join(
                        [b for b in success_body_html]) + html_divider + '<h2>Failed transfer requests</h2>' + (''.join(
                            [b for b in fail_body_html]) if fail_body_html else '<p>None! All good!</p>') + html_end
                    return self.send(body_plaintext=plaintext, body_html=html,
                                     email_to=recipient_list,
                                     email_from=settings.DEFAULT_FROM_EMAIL,
                                     subject='[STOCK MANAGEMENT] A transfer has taken place!')
        except Exception as e:
            logger.error(f'An error occurred whilst attempting to send email: {str(e)}')
        return False
