import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders




def mailit(toadress):
    fromaddr = "##########" #Enter the FROM Address
    toaddr=toadress
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "General FAQ Related to COVID-19"
    body = "Hi User,\n\nIn these challenging times, we are all navigating through uncertainty for ourselves, our loved ones and our community. We hope you are staying healthy and safe.\n\n\nPlease find attached some general FAQs related to COVID-19.\n\nWe shall overcome some day :)"
    msg.attach(MIMEText(body, 'plain'))
    filename = "COVID-19_FAQ"
    attachment = open("attach/COVID-19_FAQ.pdf", "rb")
    part = MIMEBase('application', 'pdf')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "###ENTER YOUR MAIL PASSWORD###")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

