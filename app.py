import os
from dotenv import load_dotenv

import imaplib
import email
from email.header import decode_header

import shlex


LABELS = ["Ad"]
OLDER_THAN = "90d"


def get_labels(imap):
    '''
    Add all labels from the global and all sub-labels to a list
    to a complete list of labels to cleanse emails from
    '''

    # get complete list of gmail labels
    full_list = imap.list()[1]

    cleanse_list = []

    for search_label in LABELS:\
        # add the base label to the list (eg. Ad)
        cleanse_list.append(search_label)

        search_folder = search_label + "/"

        # build list of search_label sub-labels (eg. Ad/Newegg)
        result_list = [
            shlex.split(x.decode("utf-8"))[2]
            for x in full_list
            if search_folder in x.decode("utf-8")
        ]

        cleanse_list.extend(result_list)

    return cleanse_list


def search_string(label):
    '''
    the gmail search string of emails to be trashed
    in this case, all emails in the passed label that are
    older than OLDER_THAN and NOT starred and NOT marked important

    this will allow you to keep older emails that have cleanse labels 
    if you star them or mark as important
    '''

    gmail_search = '"label:{} -is:starred -is:important older_than:{}"'.format(
        label, OLDER_THAN
    )

    return gmail_search


def get_message_ids(imap, search):
    '''
    get the list of email ids that are a result of the search
    '''
    
    _, messages = imap.search(None, "X-GM-RAW", search)

    message_ids = [x for x in messages[0].split(b" ") if x != b""]

    return message_ids


def trash_ids(imap, id_list):
    '''
    Iterate through list of email ids and label them
    with the Trash label. Once in the trash, Gmail 
    will delete permanently after 30 days.
    '''

    for message_id in id_list:
        _, msg = imap.fetch(message_id, "(RFC822)")
        # you can delete the for loop for performance if you have a long list of emails
        # because it is only for printing the SUBJECT of target email to trash
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes type, decode to str
                    subject = subject.decode()
                print("Trashing", subject)

        # put the email in the trash folder
        imap.store(message_id, "+X-GM-LABELS", "\\Trash")


def handle():
    # Get username and pass from env vars or .env file
    load_dotenv()
    username = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASSWORD")

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    # authenticate
    imap.login(username, password)

    # need to select a imap folder, but can search across everything
    imap.select('"[Gmail]/All Mail"')

    # get full list of cleansing labels based off of LABEL global as a base label
    label_list = get_labels(imap)

    # iterate over each cleanse label, find messages and trash
    for label in label_list:
        print(f"Trashing {label}")
        search_results = search_string(label)

        cleanse_ids = get_message_ids(imap, search_results)

        if cleanse_ids is not None:
            trash_ids(imap, cleanse_ids)

    imap.close()
    imap.logout()


if __name__ == "__main__":

    handle()
