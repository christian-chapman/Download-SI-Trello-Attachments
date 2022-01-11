import os
import configparser
import base64
from urllib.request import urlopen
import urllib.error
import requests
from trello import TrelloClient


def create_onedrive_directdownload(onedrive_link):
    # found this function from the website below
    # https://towardsdatascience.com/how-to-get-onedrive-direct-download-link-ecb52a62fee4#1dc6
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/', '_').replace('+', '-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl


def display_board_names(trello_client, common_identifier):
    all_boards = trello_client.list_boards()
    all_boards = [board for board in all_boards if common_identifier in board.name]

    for board in all_boards:
        print(board.name)


def has_available_boards(trello_client, common_identifier):
    all_boards = trello_client.list_boards()
    all_boards = [board for board in all_boards if common_identifier in board.name]

    if len(all_boards) != 0:
        return True
    else:
        return False


def get_google_url(comment):
    comment_tokens = comment.split()
    for token in comment_tokens:
        if "https://drive.google.com" in token:
            return token


def get_google_file_id(drive_url):
    url_tokens = drive_url.split("/")
    return url_tokens[-2]


def cleanup_name(name):
    if "%5B" in name:
        name = name.replace("%5B", "[")

    if "%5D" in name:
        name = name.replace("%5D", "]")

    if "%23" in name:
        name = name.replace("%23", "#")

    if "%2C" in name:
        name = name.replace("%2C", ",")

    if "%2B" in name:
        name = name.replace("%2B", "+")

    if "_" in name:
        name = name.replace("_", " ")

    return name


def open_attachments(class_name, semester, attachment_url):
    file_name = ""
    current_dir = semester + "/" + class_name

    if not os.path.exists(current_dir):
        os.makedirs(current_dir)

    if "https://trello" in attachment_url:
        url_list = attachment_url.split("/")
        file_name = url_list[-1]
        file_name = cleanup_name(file_name)

    elif "https://1drv.ms" in attachment_url:
        # I attached the file_name to the end of the URL when retrieving the data from Trello in the other function
        # Here, we are unpacking that data and converting the OneDrive link into the downloadable link
        try:
            url_with_file_format = urlopen(attachment_url.split()[0]).url
            file_name = attachment_url.split()[-1] + "." + url_with_file_format.split("%2c")[-1]

        except urllib.error.HTTPError as e:
            file_name = attachment_url.split()[-1] + "." + e.url.split("%2c")[-1]

        attachment_url = create_onedrive_directdownload(attachment_url.split()[0])

    elif "https://docs.google.com" in attachment_url:
        r = requests.get(attachment_url, allow_redirects=True, auth=client.oauth)

        if r.status_code != 200:
            print(f"Error with downloading a google file present in {class_name}. HTTP Error code:{r.status_code}")
            print("Continuing to download the rest of the files...")
            return

        req_json_header = r.headers.get("Content-Disposition")
        file_name = req_json_header.split('"')[1]

        file = open(current_dir + '/' + file_name, 'wb')
        file.write(r.content)
        file.close()

        return  # need to return to avoid running code below that downloads for trello and one drive attachments

    r = requests.get(attachment_url, allow_redirects=True, auth=client.oauth)

    file = open(current_dir + '/' + file_name, 'wb')
    file.write(r.content)
    file.close()


def get_all_attachments(trello_client, common_identifier):
    class_attachments = {}  # {key: value} is {class name/number: list of all links for downloadable attachments}
    all_boards = trello_client.list_boards()
    all_boards = [board for board in all_boards if common_identifier in board.name]  # filters boards based on common identifier

    for board in all_boards:
        board_lists = list(board.all_lists())  # gets each class's list in this board

        for board_list in board_lists:
            class_tokens = str(board_list).split()
            class_name = class_tokens[1] + " " + class_tokens[2]  # gets the name of the course w/o name of SI Leader

            if ">" in class_name:  # on the occasion that a > is in the class name, it needs to be removed.
                class_name = class_name.replace(">", "")

            attachments = []

            cards = board_list.list_cards()  # gets all the cards in this list, aka each week's card

            for card in cards:  # iterate over those cards to get the attachments
                card_attachments = card.get_attachments()
                card_comments = card.get_comments()

                if len(card_attachments) != 0:

                    for i in range(len(card_attachments)):
                        file_types = [".docx", ".dotx", ".pdf", ".pptx"]

                        if any([x in card_attachments[i].url for x in file_types]) and (
                                "https://trello" in card_attachments[i].url):
                            attachments.append(card_attachments[i].url)

                        elif "https://1drv.ms" in card_attachments[i].url:
                            attachments.append(card_attachments[i].url + " " + card_attachments[i].name)

                        elif "https://drive.google.com" in card_attachments[i].url:
                            google_file_id = get_google_file_id(card_attachments[i].url)
                            downloadURL = f'https://docs.google.com/uc?export=download&id={google_file_id}'
                            attachments.append(downloadURL)

                elif len(card_comments) != 0:
                    # if there are no attachments found in this card then check comments for a Google Drive link
                    for i in range(len(card_comments)):
                        if "https://drive.google.com" in card_comments[i]["data"]["text"]:
                            url = get_google_url(card_comments[i]["data"]["text"])
                            google_file_id = get_google_file_id(url)
                            downloadURL = f'https://docs.google.com/uc?export=download&id={google_file_id}'
                            attachments.append(downloadURL)

            if class_name not in class_attachments.keys():
                class_attachments[class_name] = attachments
            else:
                # this branch allows us to add attachments to the same class when it appears twice instead of
                # overwriting/replacing it
                class_attachments[class_name] = class_attachments[class_name] + attachments

    return class_attachments


if __name__ == "__main__":
    try:
        cwd = os.getcwd()  # gets the current working directory
        config = configparser.ConfigParser()
        config.read(cwd + "\\credentials.txt")  # Assuming this is on a windows environment.
    except configparser.Error:
        print("Please verify credentials.txt file")
        exit(0)

    client = TrelloClient(
        api_key=config.get("read", "apiKey"),
        api_secret=config.get("read", "secret"),
        token=config.get("read", "token"),
        token_secret=config.get("read", "secret")
    )

    boards_identifier = input("Enter the common identifier of the board(s) you would like to download from: ")
    semester = input("Enter the semester of these boards: ")  # determines name of folder

    if has_available_boards(client, boards_identifier):
        print("\nGetting attachments from Trello. The following board(s) will be selected:\n")
        display_board_names(client, boards_identifier)
    else:
        print("No available boards were found using that identifier. Please try again.\n")

    while not has_available_boards(client, boards_identifier):  # will continue looping until some boards are found
        boards_identifier = input("Enter the common identifier of the board(s) you would like to download from: ")
        semester = input("Enter the semester of these boards: ")  # determines name of folder

        if has_available_boards(client, boards_identifier):
            print("\nGetting attachments from Trello. The following board(s) will be selected:\n")
            display_board_names(client, boards_identifier)
        else:
            print("No available boards were found using that identifier. Please try again.\n")

    allAttachments = get_all_attachments(client, boards_identifier)

    print("\nSaving the attachments locally.")
    for className, url in allAttachments.items():
        for link in url:
            open_attachments(className, semester, link)

    print("Done.")
