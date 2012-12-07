# coding=utf-8
import smtplib


def email(to, about):
    if about == 'pass_reset':
        # The email constructing actions
        pass

    # The common sending actions go here
    # with exceptions going to a log


    
# here one has to generate mail and send it TODO - configure mail server and check if it works
#sender = 'from@fromdomain.com'
#receivers = ['asd@a.com']
#message = """From: From Person <from@fromdomain.com>
#To: To Person <to@todomain.com>
#Subject: SMTP e-mail test
#This is a test e-mail message.
#"""
#try:
    #smtpObj = smtplib.SMTP('localhost')
    #smtpObj.sendmail(sender, receivers, message)         
    #print "Successfully sent email"
#except SMTPException:
    #print "Error: unable to send email"
