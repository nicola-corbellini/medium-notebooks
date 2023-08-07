import email as em


def get_emails(mail):
        # Get unread emails
        mail.select('inbox')
        status, data = mail.search(None, '(UNSEEN)')

        if status == "OK":
            # Format unread emails indexes to be a list
            mail_ids = [block.split() for block in data]
            mails = {}
            # Loop al unread emails indexes
            for idx in mail_ids[0]:
                # Fetch the message content
                status, message = mail.fetch(str(idx.decode()), '(RFC822)')
                if status == "OK":
                    for response in message:
                        if isinstance(response, tuple):
                            # Decode email content to string
                            msg = em.message_from_bytes(response[1])
                            # Retrieve the object
                            subject_parts = em.header.decode_header(msg["Subject"])
                            subject = "".join([s[0].decode() for s in subject_parts if not isinstance(s[0], str)])
                            # Retrive the sender
                            sender, encoding = em.header.decode_header(msg["From"])[0]
                            if isinstance(sender, bytes):
                                sender = sender.decode(encoding)
                            # Retrieve content of the email
                            if msg.is_multipart():
                                body = ""
                                for part in msg.walk():
                                    try:
                                        body += part.get_payload(decode=True).decode()
                                    except:
                                        pass

                # Store all email in a dictionary
                mails[idx.decode()] = {"Subject": subject, "From": sender, "Body": body}

        return mails
