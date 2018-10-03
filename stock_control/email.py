import logging
from anymail.exceptions import AnymailAPIError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User, Group

# Get an instance of a logger
logger = logging.getLogger('django')


class SendEmail:
    DEFAULT_SUBJECT = '[WEBSITE EMAIL]'

    class EmailType:
        STOCK_TRANSFER = 'Notification email sent when stock has been transferred'

    def __init__(self):
        pass

    @staticmethod
    def send(body_plaintext=None, body_html=None, email_to=None, email_from=None, subject=None):
        email_to = [] if not email_to else email_to
        if body_plaintext and body_html and email_to:
            try:
                msg = EmailMultiAlternatives(
                    subject if subject else SendEmail.DEFAULT_SUBJECT,
                    body_plaintext,
                    email_from if email_from else settings.DEFAULT_FROM_EMAIL,
                    email_to
                )
                msg.attach_alternative(body_html, "text/html")
                # you can set any other options on msg here, then...
                msg.send()  # send the message
                return True
            except AnymailAPIError as e:
                logger.error(f'An error has occurred in sending email: {e.describe_response()}')
        return False

    @staticmethod
    def compose(instance=None, notification_type=None):
        """
        :param instance: request object
        :param notification_type: type of notification to send
        :return: True|False
        This method composes notification emails, then sends them through the send() method.
        """
        if notification_type == SendEmail.EmailType.STOCK_TRANSFER:
            if instance:
                """
                email notification to administrators + requester
                """
                try:
                    admin_email_addr = User.objects.filter(groups__name='administrators').values_list('email',
                                                                                                      flat=True)
                    recipient_list = [a for a in admin_email_addr]  # list of all stock administrator's email addresses
                    if settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_to_transfer_requester']:
                        recipient_list.append(instance.user.email)  # add the transfer requester's email address
                    recipient_list = list(set(recipient_list))  # remove any dupes
                    """Remove email address of an admin if that admin is doing the editing
                    """
                    if instance.user.email in recipient_list and instance.user.groups.filter(
                            name='administrators').exists():
                        recipient_list.remove(instance.user.email)
                    """
                    Send email notification to admins (and requester if configured to receive in settings.py).
                    Email is not sent to an admin who creates/edits a record themselves.
                    """
                    if recipient_list:
                        body_plaintext = f"""
                                The following transfer has taken place on {instance.record_updated.strftime("%d/%m/%Y %H:%M:%S %Z")}:
                                - Transfer to: {instance.user} [{instance.user.email}]
                                - Stock line details:
                                  - SKU: {instance.sku}
                                  - Description: {instance.desc}
                                  - Units transferred: {instance.transferred}
                                  - Unit price: {instance.unit_price}
                                """
                        body_html = f"""<html>
                                <body>
                                <p>The following transfer has taken place on {instance.record_updated.strftime("%d/%m/%Y %H:%M:%S %Z")}</p>
                                <ul>
                                <li>Transfer to: {instance.user} [<a href="mailto:{instance.user.email}">{instance.user.email}</a>]</li>
                                <li>Stock line details:
                                <ul>
                                <li>SKU: {instance.sku}</li>
                                <li>Description: {instance.desc}</li>
                                <li>Units transferred: {instance.transferred}</li>
                                <li>Unit price: {instance.unit_price}</li>
                                </ul>
                                </li>
                                </ul>
                                </body>
                                </html>
                                """
                        if settings.STOCK_MANAGEMENT_OPTIONS['email']['notifications_on']:
                            return SendEmail.send(body_plaintext=body_plaintext, body_html=body_html,
                                                  email_to=recipient_list,
                                                  subject='[STOCK MANAGEMENT] A transfer has taken place!')
                        else:
                            logger.info(
                                f'If in live mode, notification email would be sent to: {[a for a in recipient_list]}')
                    else:
                        logger.info('There are no recipients in the notification email list!')
                except User.DoesNotExist:
                    logger.error('Error in sending email - queried user does not exist!')
            return False
