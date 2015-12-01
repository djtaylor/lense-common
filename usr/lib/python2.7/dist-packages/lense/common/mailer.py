from django.core.mail import send_mail

class LenseAPIEmail(object):
    """
    Wrapper class for handling emails.
    """
    @staticmethod
    def send(subject, body, sender, recipient):
        """
        Send an email.
        
        :param subject:   The subject of the email
        :type  subject:   str
        :param body:      The body of the email
        :type  body:      str
        :param sender:    The sender's email
        :type  sender:    str
        :param recipient: Email recipients
        :type  list|str   A list of recipient emails, or a single email string
        """
        if LENSE.CONF.email.smtp_enable:
                
            # Send the email
            try:
                
                # Supports a single or list of recipients
                _recipient = recipient if isinstance(recipient, list) else [recipient]
                
                # Send the email
                send_mail(subject, body, from_email=sender, recipient_list=_recipient, fail_silently=False)
                LENSE.LOG.info('Sent email to "{}"'.format(_recipient))
                return True
            
            # Failed to send email
            except Exception as e:
                LENSE.LOG.exception('Failed to send email to "{}": {}'.format(str(_recipient), str(e)))
                return False

        # SMTP disabled
        else:
            return False