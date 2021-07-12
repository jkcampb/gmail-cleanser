import os
from dotenv import load_dotenv

import imaplib
import email
from email.header import decode_header

import shlex


LABELS = ['Ad']
OLDER_THAN = '60d'


def get_labels(imap):
    full_list = imap.list()[1]

    cleanse_list = []

    for search_label in LABELS:
        cleanse_list.append(search_label)

        search_folder = search_label + '/'
        result_list = [shlex.split(x.decode("utf-8"))[2] for x in full_list if search_folder in x.decode("utf-8")]

        cleanse_list.extend(result_list)

        break

    return cleanse_list

def search_string(label):
    gmail_search = '"label:{} -is:starred -is:important older_than{}"'.format(label, OLDER_THAN)

    return gmail_search

def get_message_ids(imap, search):
    status, messages = imap.search(None, 'X-GM-RAW', search)

    message_ids = messages[0].split(b' ')

    return message_ids

def delete_ids(imap, id_list):
    for message_id in id_list:
        _, msg = imap.fetch(message_id, "(RFC822)")
        # you can delete the for loop for performance if you have a long list of emails
        # because it is only for printing the SUBJECT of target email to delete
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes type, decode to str
                    subject = subject.decode()
                print("Deleting", subject)
        # mark the mail as deleted
        imap.store(message_id, "+FLAGS", "\\Deleted")

    # expunge to commit the deletions
    imap.expunge()


def handle():
    # Get username and pass from env vars or .env file
    load_dotenv()
    username = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    # authenticate
    imap.login(username, password)

    imap.select('"[Gmail]/All Mail"')

    # get full list of cleansing labels based off of LABEL global as a base label
    label_list = get_labels(imap)

    for label in label_list:
        print(f"Deleting {label}")
        cleanse_search = search_string(label)

        cleanse_ids = get_message_ids(imap, cleanse_search)

        print(f"\t{len(cleanse_ids)} messages")
        # delete_ids(imap, cleanse_ids)


if __name__ == '__main__':

    handle()