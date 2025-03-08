import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = 'vivekramprakhash@gmail.com'
receiver_email = 'aruncse60@gmail.com'
password = 'maco zjgp qsms ozcw'
subject = 'Test Email'
body = 'This is a test email sent from Python!'

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

smtp_server = 'smtp.gmail.com'
smtp_port = 587

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print('Email sent successfully!')
except Exception as e:
    print(f'Error: {e}')
finally:
    server.quit()
