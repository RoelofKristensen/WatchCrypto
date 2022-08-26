import requests
import winsound
import threading
from datetime import datetime

# Global Variables
levelsList = []
previousPrice = 0.0
currentPrice = 0.0


# Write list to new file
def writeFile():
    fo = open("c:\\Temp\\levelsFile.txt", "w")
    for item in levelsList:
        fo.write("%s\n" % item)  # %s\n means: convert everything in item to a string and then add \n
    fo.close()


# Read file into list
def readFile():
    try:
        fo = open("c:\\Temp\\levelsFile.txt", "r")
        lineCounter = 1
        for line in fo:
            # if the last two characters in the line is "\n", remove them
            if (line.find('\n')):
                line = line[:-1]
            levelsList.append(float(line))
        fo.close()
    except:
        return


# Call the CoinDesk Exchange
def getCoinDeskPrice():
    bitcoin_api_url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
    return response_json["bpi"]["USD"]["rate_float"]


# Sound and display the alarm
def alarm(freq):
    duration = 500  # milliseconds
    winsound.Beep(freq, duration)
    print('\x1b[6;30;42m' + 'Alarm!' + '\x1b[0m')


# Sort and Display the levelsList
def displayList():
    print("Price Levels In The List")
    print("========================")
    levelsList.sort(reverse=True)
    for item in levelsList:
        print(item)
    print('')


# Update the list
def updateList():
    min = 0
    max = 2
    errorMsg = "Please enter a valid option between " + str(min) + " and " + str(max)
    selection = 99
    while selection != 0:
        print(chr(27) + "[2J")  # Clear the screen
        displayList()

        print("Update The List")
        print("===============")
        print("1. Add a price level")
        print("2. Remove a price level")
        print("0. Finish updating the list")

        try:
            selection = int(input("Please enter one of the options: "))
            if (selection == 1):
                try:
                    levelsList.append(float(input("Enter the price level to add: ")))
                    writeFile()
                except:
                    print("Please retry and enter a float value.")  # user did not enter a number
            elif (selection == 2):
                try:
                    price = float(input("Enter the price level to remove: "))
                    if price in levelsList:
                        levelsList.remove(price)
                        writeFile()
                except:
                    print("Please retry and enter a float value.")  # user did not enter a number
        except:
            print(errorMsg)  # user did not enter a number
            continue  # skip the following if statement
        if (selection < min or selection > max):
            print(errorMsg)  # user entered a number outside the required range


# Code to perform every 5 seconds
def watchLoop():
    threading.Timer(5.0, watchLoop).start()
    global previousPrice
    global currentPrice
    previousPrice = currentPrice
    currentPrice = getCoinDeskPrice()
    if (previousPrice == 0):  # First loop
        previousPrice = currentPrice

    print('')
    print('Price Check at ' + str(datetime.now()))
    print('=========================================')

    # Format previous price in blue
    previousPriceText = '\x1b[0;36;44m' + 'Previous Price: ' + str("%.2f" % previousPrice) + '\x1b[0m'

    # Format current price colour
    if (currentPrice > previousPrice):  # Price went up - use green
        currentPriceText = '\x1b[6;30;42m' + 'Current Price:  ' + str("%.2f" % currentPrice) + '\x1b[0m'
    elif (currentPrice < previousPrice):  # Price went down - use red
        currentPriceText = '\x1b[4;33;41m' + 'Current Price:  ' + str("%.2f" % currentPrice) + '\x1b[0m'
    else:  # Price did not change - use blue
        currentPriceText = '\x1b[0;36;44m' + 'Current Price:  ' + str("%.2f" % currentPrice) + '\x1b[0m'

    # Create a new list for displaying. This list will contain sub-lists. Each sublist will contain the
    # text to display - as well as its associated price (which is used to sort the list).
    displayList = []

    # Add levelsList to displayList
    for item in levelsList:
        tempList = ['Price Level:    ' + str("%.2f" % item), item]
        displayList.append(tempList)

    # Add previousPrice to displayList
    tempList = [previousPriceText, previousPrice]
    displayList.append(tempList)

    # Add currentPrice to displayList
    tempList = [currentPriceText, currentPrice]
    displayList.append(tempList)

    # Sort displayList using the second items of all sub-lists in displayList
    displayList = sort2DList(displayList)

    # Print the first items of all sub-lists in displayList
    for i in range(0, len(displayList)):
        print(displayList[i][0])

    # Test if the alarm should be sound
    if (previousPrice != 0):
        for i in range(0, len(displayList)):
            if ("Price Level" in displayList[i][0]):
                if ((previousPrice > displayList[i][1] and currentPrice < displayList[i][1]) or
                        (previousPrice < displayList[i][1] and currentPrice > displayList[i][1])):
                    alarm(400)


# Sort the 2-D displayList based on a value in its sublists
# https://www.geeksforgeeks.org/python-sort-list-according-second-element-sublist/
def sort2DList(sub_li):
    return (sorted(sub_li, key=lambda x: x[1], reverse=True))


# Main Code Section
# =================

# Load list
readFile()

# Update list
updateList()

# Check Exchange
watchLoop()
