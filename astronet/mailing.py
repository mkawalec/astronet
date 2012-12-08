# coding=utf-8
import smtplib
from email.mime.text import MIMEText

def email(to, about,hash=None):
    if about == 'pass_reset':
        COMMASPACE = ', '
        sender = 'admin@astronet.pl'
        receivers = [to]
        msg = 'Witaj,\r'+\
        'dostaliśmy od Ciebie prośbę o zmianę hasła.\r'+\
        'Jeżeli to nie Ty chcesz zmienić hasło, zignoruj tę wiadomość.\r'+\
        'Jeżeli chcesz zmienić hasło kliknij w poniższy link i postępuj zgodnie z instrukcjami.\r'+\
        'http://127.0.0.1:5000/password_reset/%s' % (hash,)
        msg = MIMEText(msg)
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(receivers)
        msg['Subject'] = 'Astronet: Zmiana hasła'

        try:
            s = smtplib.SMTP('localhost')
            s.sendmail(sender,receivers, msg.as_string())
            s.quit()      
        except :
            pass
            #TODO logging - where? what exactly?

