# coding=utf-8
import smtplib
from email.mime.text import MIMEText

from flask import url_for, g
from flaskext.bable import gettext as _
from .helpers import localize
from .models import User


class Mailer:

    sender = 'admin@astronet.pl'
    server = 'astronet.pl'

    def __init__(self, user):
        self.user = user
        if isinstance(user, User):
            self.hash = user.confirmation_codes[-1].code

    @localize
    def activation(self):
        msg = _('Hello %(name)s,\n'
                'You have created an Astronet account and you are '
                'almost ready to use it. Please click the activation '
                'link below to discover the wonders of the Astronet.\n'
                'In the off chance that you don\'t remember creating '
                'the account, just ignore this email.\n\n'
                '%(link)s\n\n'
                'Yours,\n'
                'Astronet', name=self.user.real_name,
                link=url_for('api.activate', confirmaton=self.hash,
                    _external=True))
        self._send_msg(msg, _('Activate your Astronet account'))

    @localize
    def pass_reset(self):
        msg = _('Hello %(name)s,\n'
                'It seems that you wanted your Astronet password '
                'to be reset. If it was you who requested it, please '
                'click the link below to complete resetting your password.'
                '\n\n%(link)s\n\n'
                'Yours,\n'
                'Astronet',
                name=self.user.real_name, link=url_for('api.set_new_password',
                    confirmation=self.hash, _external=True))

        self._send_msg(msg, _('Password reset request for Astronet'))

    def _send_msg(self, message, subject):
        msg = MIMEText(message, 'text', 'utf-8')
        msg['Subject'] = subject
        msg['Sender'] = self.sender

        if isinstance(self.user, User):
            msg['To'] = self.user.email
        else:
            msg['To'] = '; '.join(map(lambda x: x.email, self.user))

        s = smtplib.SMTP(self.server)
        s.ehlo()
        s.starttls()
        s.ehlo()

        s.login('devnull@astronet.pl', 'almublah')
        s.sendmail(sender,receivers, msg.as_string())
        s.quit()      
