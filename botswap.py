import csv
import logging
import io
import telepot
import telegram.ext
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telepot.loop import MessageLoop
from telepot.helper import UserContext
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import string
import random
import requests
from bs4 import BeautifulSoup
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = "439102130:AAG8fC4CLtcI8b11iV4tpCLk4-EruDTplms'"
# Passing token to bot
updater = Updater(TOKEN)
# Setting range of conversation
DECISION , READY, COURSE_CODE, INDEX_NUMBER, DESIRED , AGAIN= range(6)
# the two data files we used to store the indexes and user ids
dbfile = 'swapdata.csv'
dbfile2 = 'friendfinding.csv'
#start of the bot
def start(bot,update):
    reply_keyboard = [['Swap Factory'],['Find Friends'],['SOS']]#reply keyboard for the user
    update.message.reply_text('Welcome to the Duck Swapper Company, How may I help you today?',reply_markup=ReplyKeyboardMarkup(keyboard = reply_keyboard, one_time_keyboard = True, resize_keyboard = True))
    return DECISION
#user decides if he wants to carry on with the swap
def swap_decision(bot, update):
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text(
        'Quack~! My name is the Duck Swapping Bot.\n'
        '  Send /cancel to stop talking to me.\n\n'
        'Are you ready to swap Index Numbers?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,resize_keyboard=True))
    return READY

def ready(bot,update):
    msg = update.message.text
    if msg == 'Yes':#if user clicked yes, ask for course code
        update.message.reply_text('Quack! Please input your Course Code',
                                  reply_markup=ReplyKeyboardRemove())
        return COURSE_CODE
    else: return cancel(bot,update)#if no end programme

def course_code(bot,update,chat_data,user_data):
    msg = update.message.text  #updater gets the text messaage of user input
    user_data['course_code'] = msg #temp store the content into user_data
    user = update.message.from_user #get user info
    update.message.reply_text('Quacksome! Now, enter your Index Number.\nOmit the 0 in front.\neg: 015321 = 15321')
    return INDEX_NUMBER#ask for next user input ie:the index they have


    #supposed to be able to parse the ntu link website but unable to due to technical difficulites

def index_number(bot,update,chat_data,user_data):
    msg = update.message.text #updater get the message of user input
    user_data['index_number'] = msg #temp store the content into user data
    user = update.message.from_user # get user info
    if len(user_data)>=2: # branching as we reused the fuction. this the path when user wants to swap
        update.message.reply_text('Quackgeous! Now, enter your Desired Index Number.\nOmit the 0 in front.\neg: 015321 = 15321')
        return DESIRED    #ask for next user input ie: the index they want
    else: #path of finding friends
        update.message.reply_text('hehehe')#fun message as the bot is still underdevelopment
        return friendfinding(bot,update,chat_data,user_data)

def desired(bot,update,chat_data,user_data):
    msg = update.message.text#updater get the message of user input
    user_data['desired'] = msg #temp storage of message into user data
    user = update.message.from_user #get user info
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)#make the bot send the action as if its typing while it checks for matches
    matchcheck(bot,update,chat_data,user_data) #function call for the matching algorithm                                             #the user sees typing....
    return ConversationHandler.END

def matchcheck(bot, update,chat_data,user_data):#function that contains the matching algorithm
    data = list()# empty list 
    for key, value in user_data.items():
        data.append('%s' % value)   #append all pervious messages that was temp stored in user data to the list
    data.append(update.message.chat_id)#add user id to the list too
    
   
    with open(dbfile, 'rt+') as fileA:#open database(db) file for reading and writing
        for row in csv.reader(fileA , delimiter=','): #for loop to loop through all rows in the db
            if data[1] == row[2] and  data[2] == row[1]:#both conditions must be True ie: Person A wants 'a' and has 'b' AND Person B wants 'b' and has 'a'
                user1= update.message.from_user.id#if True get user id of Person A and B 
                user2= row[3]#get user id from db
                message = '<a href="tg://user?id=' + str(user2) + '">Your swap is ready, click here to get started!</a>'#notify both of them and export opposite username to both.
                message2 = '<a href="tg://user?id=' + str(user1) + '">Your swap is ready, click here to get started!</a>'
                bot.sendMessage(parse_mode='HTML', chat_id= chat , text=message)
                bot.sendMessage(parse_mode='HTML', chat_id= chat1 , text=message2)
                fileA.close() 
                deleter(row)# function call to delete data that already got matched
                return endmessage(bot,user1,user2) #function call to end the convesation
            elif (len(list(csv.reader(fileA , delimiter=',')))-counter == 0): #make sure to check through the whole list   
                update.message.reply_text("Your Entry has been stored!\nWe will Quaaack if we find a match!")
                writer = csv.writer(open(dbfile, 'a'), dialect='excel')#in case of no match, store data(course code, index, index-want,user id)
                writer.writerows([data])
                return start(bot,update)
    #return "\n".join(data).join(['\n', '\n'])

def deleter(row_num):
    with open(dbfile, 'w+') as fileA:
        rows =()
        for row in csv.reader(fileA):#PUT ALL DATA INTO A LIST
            rows += (tuple(row))
        fileA.close()
    for line in rows:#CHECK LIST FOR MATCHING DATA WITH ROW_NUM
        if line != row_num:#WRITE DATA TO FILE EXCLUDING THE MATCHING ROW
            writer = csv.writer(fileA, dialect='excel')
            writer.writerows(line)
                

def friendfinding(bot, update, chat_data, user_data):
    data = list()  # empty list
    for key, value in user_data.items():
        data.append('%s' % value)  # append all pervious messages that was temp stored in user data to the list
    data.append(update.message.chat_id)  # add user id to the list too

    with open(dbfile2, 'rt+') as fileB:  # open database(db) file for reading and writing
        for row in csv.reader(fileB, delimiter=','):  # for loop to loop through all rows in the db
            try:
                if data[0] == row[0]:
                    user1 = update.message.from_user.id  # if True get user id of Person A and B
                    user2 = row[1]  # get user id from db
                    message = '<a href="tg://user?id=' + str(
                        user2) + '">Your boat has arrived, click here to get started!</a>'  # notify both of them and export opposite username to both.
                    message2 = '<a href="tg://user?id=' + str(
                        user1) + '">Your boat has arrived, click here to get started!</a>'
                    bot.sendMessage(parse_mode='HTML', chat_id=user1, text=message)
                    bot.sendMessage(parse_mode='HTML', chat_id=user2, text=message2)
                    fileB.close()
                    deleter(user2)  # function call to delete data that already got matched
                    return endmessage(bot, user1, user2)  # function call to end the convesation.
            except IndexError:
                return ConversationHandler.END

        update.message.reply_text("Your Entry has been stored!\nWe will Quaaack if we find a match!")
        writer = csv.writer(open(dbfile, 'a'),
                            dialect='excel')  # in case of no match, store data(course code, index, index-want,user id)
        writer.writerows([data])
        return ConversationHandler.ENDs
        




def find(bot,update):
    update.message.reply_text("Feeling lonely? Fret not I'll sort you right out!\n But first i need your index number!\
        \n Enter your Index Number.\nOmit the 0 in front.\neg: 015321 = 15321")
    return INDEX_NUMBER

def cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text('Byeeee Quaaack.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def endmessage(bot,chat,chat1):
    bot.sendMessage(chat_id=chat1,text='Thanks for using the duckswapper!')
    bot.sendMessage(chat_id=chat,text='Thanks for using the duckswapper!')
    return ConversationHandler.END


def again(bot,update):
    msg = update.message.text
    if msg == 'Yes':
        sos(bot,update)
    else: return start(bot,update)
   
def sos(bot,update):
    # Define max amount of pages, define url base
    pages = 100
    random_page = random.randint(1, pages)
    url = 'https://me.me/s/computer%20python%20coding%20memes' + str(random_page)
    response = requests.get(url)

    # BS4 scrape, finding random img over site.
    soup = BeautifulSoup(response.text, 'html.parser')
    image_container = soup.find('div', {'class': 'grid-item'})
    images = image_container.find_all('img')
    random_image = random.choice(images)

    chat = update.message.from_user.id
    bot.send_chat_action(chat_id=chat,action='upload_photo')
    bot.send_photo(chat_id=chat, photo=random_image['src'])
    keyboard = [['HIT ME UP,BRUH'],['Nahh, I\'ll pass ']]
    bot.sendMessage(chat_id=chat, text='Would you like another one?', reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,resize_keyboard=True))

    return AGAIN 

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
# Main flow of sequence
def main():
    print('listening...')
    # Shortcut for dp
    dp = updater.dispatcher
    # Introducing the states READY COURSE_CODE INDEX_NUMBER DESIRED of conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        
        states={
            DECISION:[RegexHandler('^Swap Factory$',swap_decision),
                    RegexHandler('^Find Friends$',find),
                    RegexHandler('^SOS$',sos,)], 
            
            READY:[RegexHandler('^(Yes|No)$',ready)],
    
            COURSE_CODE: [MessageHandler(Filters.text | Filters.command, course_code, pass_chat_data=True, pass_user_data=True)],

            INDEX_NUMBER: [MessageHandler(Filters.text | Filters.command, index_number, pass_chat_data=True, pass_user_data=True)],

            DESIRED: [MessageHandler(Filters.text | Filters.command, desired, pass_chat_data=True, pass_user_data=True)],

            AGAIN:[RegexHandler('^(Yes|No)$',again)],


      },

        # Fallback statement in case of abrupt end
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

# Start the Bot
    updater.start_polling()

# Idling
    updater.idle()


if __name__ == '__main__':
    main()