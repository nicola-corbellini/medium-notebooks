import os
import sys
import time
import imaplib
import tkinter as tk
import cheshire_cat_api as ccat
from utils import get_emails


class Login:
    def __init__(self, master):
        self.master = master

        # Add a frame
        self.frame = tk.Frame(self.master)

        #Username label and text box 
        username_lbl = tk.Label(self.master, text="User Name").grid(row=0, column=0)
        self.username = tk.StringVar()
        username_entry = tk.Entry(self.master, textvariable=self.username).grid(row=0, column=1)  

        #Password label and text box
        password_lbl = tk.Label(self.master,text="Password").grid(row=1, column=0)  
        self.password = tk.StringVar()
        password_entry = tk.Entry(self.master, textvariable=self.password, show='*').grid(row=1, column=1)  

        # Login button
        self.login_btn = tk.Button(self.master, text = 'Login', command = self.new_window).grid(row=2, column=1)

    def new_window(self):
        # Connect to mail server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.username.get(), self.password.get())

        # COnnect to Cat server
        cat_client = ccat.CatClient()

        # Open chat
        self.new_window = tk.Toplevel(self.master)
        self.app = Chat(self.new_window, mail, cat_client)


class Chat:
    def __init__(self, master, mail, cat_client):
        self.mail = mail
        self.cat_client = cat_client
        self.master = master
        self.frame = tk.Frame(self.master)

        # Update emails button
        update_emails = tk.Button(self.master, text="Update emails", 
                                  command=lambda: self.upload_emails(self.mail)).grid(row=0)

        # Cat's answer text widget
        self.txt = tk.Text(self.master, width=60)
        self.txt.grid(row=1, column=0, columnspan=2)
        
        # Scroolbar 
        scrollbar = tk.Scrollbar(self.txt)
        scrollbar.place(relheight=1, relx=0.974)
        
        # User's input widget
        self.e = tk.Entry(self.master, width=55)
        self.e.grid(row=2, column=0)
        
        # Send message button
        send = tk.Button(self.master, text="Send", command=lambda: self.send_message(self.e.get())).grid(row=2, column=1)

        # Redirect stdout to text widget
        sys.stdout.write = self.redirect_stdout

    def redirect_stdout(self, text):
        # Format Cat's message end insert it in text widget
        self.txt.insert("end", f"{text}\n")

    def send_message(self, text):
        # Send a message to Cat via websocket
        self.cat_client.send(message=text,
                    prompt_settings={
                        "prefix": """
                    You're an office assistant.
                    You inform the user about received emails. If you don't know the answer, don't invent.
                    """,
                    "use_procedural_memory": False,
                    "use_episodic_memory": True,
                    "use_declarative_memory": True
                    })


    def upload_emails(self, mail):
        # Retrieve unread emails
        mails = get_emails(mail)
        
        files = []
        for content in mails.values():
            # Save email content to a file to upload it with ease in the Cat's memory
            with open(f"{content['From']}_{content['Subject']}.txt", "w") as tmp:
                text = f"""
                From: 
                {content["From"]}
                Subject
                {content["Subject"]}
                Content
                {content["Body"]}
                """
                tmp.write(text)

                # Send file down the Rabbit Hole
                self.cat_client.api.rabbit_hole.upload_file(file=f"{content['From']}_{content['Subject']}.txt", 
                                                    chunk_size=1000,
                                                    chunk_overlap=200)
                time.sleep(1)
            # Store files to delete lately
            files.append(f"{content['From']}_{content['Subject']}.txt")

        # Delete files
        for file in files:
            os.remove(file)


