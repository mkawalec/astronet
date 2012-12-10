# coding=utf-8
import smtplib
from email.mime.text import MIMEText

def email(to, about,hash=None):
    sender = 'admin@astronet.pl'
    receivers = [to]
    msg = ''

    if about == 'pass_reset':
        COMMASPACE = ', '
        msg = u'Witaj,\r'+\
        u'dostaliśmy od Ciebie prośbę o zmianę hasła.\r'+\
        u'Jeżeli to nie Ty chcesz zmienić hasło, zignoruj tę wiadomość.\r'+\
        u'Jeżeli chcesz zmienić hasło kliknij w poniższy link i postępuj zgodnie z instrukcjami.\r'+\
        u'http://127.0.0.1:5000/password_reset/%s' % (hash,)
        msg = MIMEText(msg.encode('utf-8'), 'plain', 'UTF-8')
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(receivers)
        msg['Subject'] = u'Astronet: Zmiana hasła'

    s = smtplib.SMTP('astronet.pl')

    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login('devnull@astronet.pl', 'almublah')
    s.sendmail(sender,receivers, msg.as_string())
    s.quit()      
    #TODO logging - where? what exactly?

