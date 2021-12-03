import smtplib
from email.mime.text import MIMEText
import imaplib
import email
from email_reply_parser import EmailReplyParser
from datetime import datetime


class EmailEngine():
    def __init__(self):
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        self.smtp_ssl_host = 'smtp.gmail.com'
        self.smtp_ssl_port = 465
        self.username = self.email =  'upmusicpromo.com@gmail.com'
        self.password = 'Cazzogloria00%'
        self.server = smtplib.SMTP_SSL(self.smtp_ssl_host, self.smtp_ssl_port)

    def sendEmail(self,mail_to,text,subject):
        try:
            self.server.login(self.username, self.password)

            message = MIMEText(text)
            message['subject'] = subject
            message['from'] = self.email
            message['to'] = mail_to

            self.server.sendmail(self.email, [mail_to], message.as_string())
            self.server.quit()
            return True
        except:
            return False


    def searchEmail(self,mail_to,id_request,id_playlist):
        new_message = []
        self.imap.login(self.email,self.password)
        #print(self.imap.list())
        self.imap.select('"[Gmail]/Tutti i messaggi"')
        result, data = self.imap.search(None,f'(FROM "{mail_to}" HEADER Subject "#{id_request} #{id_playlist}" UNSEEN)')

        mail_ids = []
        for block in data:
            mail_ids += block.split()

        if mail_ids != []:
            print(mail_ids)
            for i in mail_ids:
                status, data = self.imap.fetch(i, '(RFC822)')
                for response_part in data:

                    if isinstance(response_part, tuple):
                        message = email.message_from_bytes(response_part[1])
                        mail_time = message["Date"]
                        mail_from = message['from']
                        mail_subject = message['subject']
                        message_content = ""
                        # Body details
                        for part in message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload()
                                message_content += body
                            else:
                                continue
                        print(message_content)
                        message_content = EmailReplyParser.parse_reply(message_content).split("\n\n")[0]
                        mail_time = datetime.strptime(mail_time, '%a, %d %b %Y %H:%M:%S %z')
                        new_message.append({"data":mail_time,"message":message_content})

        self.imap.logout()
        print(new_message)
        return new_message
