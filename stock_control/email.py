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
                    if settings.STOCK_MANAGEMENT_OPTIONS[settings.RUN_TYPE]['email']['notifications_on']:
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
                            f'{settings.STOCK_MANAGEMENT_OPTIONS[settings.RUN_TYPE]["email"]}.'
                            f' If in live mode, notification email would be sent to: '
                            f'{[a for a in email_to] if email_to else "Nobody!"}')
                    return True
                except AnymailAPIError as e:
                    logger.error(f'An error has occurred in sending email: {e.describe_response()}')
                except Exception as e:
                    logger.error(f'Error sending email: {e}')
        return False

    def compose(self, instance=None, notification_type=None):
        """
        :param instance: request object
        :param notification_type: type of notification to send
        :return: True|False
        This method composes notification emails, then sends them through the send() method.
        """
        try:
            if notification_type == SendEmail.EmailType.STOCK_TRANSFER:
                if instance.units_to_transfer:
                    """
                    email notification to administrators + requester
                    """
                    admin_email_addr = User.objects.filter(groups__name='administrators').values_list('email',
                                                                                                      flat=True)
                    # list of all stock administrator's email addresses
                    recipient_list = [a for a in admin_email_addr] if \
                        admin_email_addr and settings.STOCK_MANAGEMENT_OPTIONS[settings.RUN_TYPE]['email'][
                            'notifications_to_administrators'] else []
                    if settings.STOCK_MANAGEMENT_OPTIONS[settings.RUN_TYPE]['email'][
                        'notifications_to_transfer_requester']:
                        recipient_list.append(instance.user.email)  # add the transfer requester's email address
                    recipient_list = list(set(recipient_list))  # remove any dupes
                    """
                    Send email notification to admins (and requester if configured to receive in settings.py).
                    Email is only sent on stock transfer, not editing (determined by a truthy units_to_transfer submission).
                    """
                    if recipient_list:
                        body_plaintext = f"""
                                The following transfer has taken place on {instance.record_updated.strftime(
                            "%d/%m/%Y %H:%M:%S %Z")}:
                                - Transfer to: {instance.user} [{instance.user.email}]
                                - Stock line details:
                                  - SKU: {instance.sku}
                                  - Description: {instance.desc}
                                  - Units transferred: {instance.units_to_transfer}
                                  - Unit price: {instance.unit_price}
                                """
                        body_html = f"""<html>
                                <body>
                                <p>The following transfer has taken place on {instance.record_updated.strftime(
                            "%d/%m/%Y %H:%M:%S %Z")}</p>
                                <ul>
                                <li>Transfer to: {instance.user} [<a href="mailto:{instance.user.email}">{instance.user.email}</a>]</li>
                                <li>Stock line details:
                                <ul>
                                <li>SKU: {instance.sku}</li>
                                <li>Description: {instance.desc}</li>
                                <li>Units transferred: {instance.units_to_transfer}</li>
                                <li>Unit price: {instance.unit_price}</li>
                                </ul>
                                </li>
                                </ul>
                                </body>
                                </html>
                                """
                        return self.send(body_plaintext=body_plaintext, body_html=body_html,
                                         email_to=recipient_list,
                                         email_from=settings.DEFAULT_FROM_EMAIL,
                                         subject='[STOCK MANAGEMENT] A transfer has taken place!')
                else:
                    logger.info('No email to send as this is not a transfer.')
        except Exception as e:
            logger.error(f'An error occurred whilst attempting to send email: {str(e)}')
        return False
