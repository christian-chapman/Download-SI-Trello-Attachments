import requests
import os
from trello import TrelloClient
import configparser


def cleanup_name(name):
    if "%5B" in name:
        name = name.replace("%5B", "[")

    if "%5D" in name:
        name = name.replace("%5D", "]")

    if "_" in name:
        name = name.replace("_", " ")

    return name


def open_attachments(class_name, attachment_url):
    r = requests.get(attachment_url, allow_redirects=True)
    current_dir = "F21/" + class_name
    url_list = attachment_url.split("/")
    name = url_list[-1]
    name = cleanup_name(name)

    if not os.path.exists(current_dir):
        os.makedirs(current_dir)

    file = open(current_dir + '/' + name, 'wb')
    file.write(r.content)
    file.close()


def get_all_attachments(trello_client):
    class_attachments = {}  # syntax for key: value == class name&number: list of all links for downloadable attachments
    all_boards = trello_client.list_boards()
    all_boards = [board for board in all_boards if "Fa 21" in board.name]
    print(all_boards)

    for i in range(1):
        board = all_boards[i]

        board_lists = list(board.all_lists())  # gets all the class lists in this board

        for board_list in board_lists:  # iterate through those lists to get the name of the class and attachments
            class_tokens = str(board_list).split()
            class_name = class_tokens[1] + " " + class_tokens[2]  # gets the name of the course

            attachments = []

            cards = board_list.list_cards()  # gets all the cards in this list, aka each week's card

            for card in cards:  # iterate over those cards to get the attachments
                card_attachments = card.get_attachments()

                if len(card_attachments) != 0:

                    for j in range(len(card_attachments)):
                        file_types = ["docx", "dotx", "pdf", "pptx"]

                        if any([x in str(card_attachments[j]) for x in file_types]) and (
                                "https://trello" in str(card_attachments[j].url)):
                            attachments.append(card_attachments[j].url)

            if class_name not in class_attachments:
                class_attachments[class_name] = attachments
            else:
                class_attachments[class_name] = class_attachments[class_name] + attachments

    return class_attachments


try:
    cwd = os.getcwd()
    config = configparser.ConfigParser()
    config.read(cwd + "\\credentials.txt")  # Assuming this is on a windows environment.
    print(config.get("read", "apiKey"))
    print(config.get("read", "token"))
    print(config.get("read", "secret"))
except configparser.Error:
    print("Please verify credentials.txt file")
    exit(0)

client = TrelloClient(
    api_key=config.get("read", "apiKey"),
    api_secret=config.get("read", "secret"),
    token=config.get("read", "token"),
    token_secret=config.get("read", "secret")
)

allAttachments = get_all_attachments(client)

print(allAttachments.values())

for classname, url in allAttachments.items():
    for link in url:
        open_attachments(classname, link)
