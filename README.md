# Download-SI-Trello-Attachments

## Overview
Welcome to the script for automating UMKC's SI Trello Boards. The goal of this script is to download all the SI Plans that were used in the previous semester. These plans are uploaded as attachments to Trello cards, and this script runs through those cards and downloads them locally.

## How To Use
In order to use this script, you will need a Trello API Key, API Secret, and Token. These can all be found at [this link](https://trello.com/app-key), and below there is a section in detail on how to get each one of those from that link. Following retrieving the key, secret, and token, they will need to be put in the credentials.txt file that is in this repository.

Next, you will need to run the script. You will be prompted with two user inputs, one for the common identifier between the boards that are being selected (i.e., what text the boards share in common, such as the same semester like "Fa 21"). The other prompted input is for the name of the semester that these boards are from, and this is only to name the folder that the attachments are getting saved into.

Once entering the desired input, the program will continue running until the "Done." message is displayed. The attachments have been successfully saved locally to your machine in the folder that is the name of the semester which was input earlier.

## How To Get API Key, API Secret, & Token
Go to [this link](https://trello.com/app-key) when signed in to your Trello account. This page should display your Key and Secret (key is at the top of the page under Developer API Keys and Secret is near the bottom by OAuth and Secret). To access your token, go to the top of the page under Developer API Keys, there should be a link to "generate a Token." Click on that link, allow access for Server Token, and now you will be given your Token.