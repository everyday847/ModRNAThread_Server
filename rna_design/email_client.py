from email.mime.text import MIMEText
from datetime import date
import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "modrnathread.server@gmail.com"
SMTP_PASSWORD = "a_man_a_plan_a_canal:ribonucleic_acids"

EMAIL_FROM = "email@gmail.com"
EMAIL_SUBJECT = "RNA Redesign Job Finished : "

DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

DATA='This is the content of the email.'


def send_email(user_email, data_dir):
    print "email: |%s|" % user_email
    DATA = """ Dear %s:

    Your threading job is finished.
    See the results at
    http://modrnathread.stanford.edu/result/%s
    """ % (user_email, data_dir)

    EMAIL_TO = [user_email]

    msg = MIMEText(DATA)
    msg['Subject'] = EMAIL_SUBJECT + " %s" % (date.today().strftime(DATE_FORMAT))
    msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
    msg['From'] = EMAIL_FROM
    mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mail.starttls()
    mail.login(SMTP_USERNAME, SMTP_PASSWORD)
    mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    mail.quit()

if __name__=='__main__':
    send_email()
