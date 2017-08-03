from telegram.ext import Updater,CommandHandler,MessageHandler,ConversationHandler
from telegram.ext.filters import Filters
import logging
import urllib.parse
import urllib.request
import requests
from io import BytesIO
from db_wrap import db_interface
import sqlite3

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

base_api_url = 'http://202.127.24.18/v4/bin/astro.php?'

ADD_POSITION,ADD_CAPTION = list(range(2))
db = db_interface()
def help(bot,update):
    bot.send_message(chat_id=update.message.chat_id,text="you can send me location to "
                                                         "get weather information about you stargazing site,"
                                                         "use /add to add you places and /list to check your site list")

def reply_location(bot, update):
    location = update.message.location
    param = {'lon': location.longitude, 'lat': location.latitude, 'output': 'internal'}
    query_url = base_api_url + urllib.parse.urlencode(param)
    logging.info(query_url)
    r = requests.get(query_url)
    bot.send_photo(chat_id=update.message.chat_id,photo=BytesIO(r.content))
    # pic_file, headers = urllib.request.urlretrieve(query_url, 'test.png')
    # bot.send_photo(chat_id=update.message.chat_id,photo=open(pic_file,'rb'))
    # urllib.request.urlcleanup()

def trigger_add_position(bot,update):
    """
    callback function for command /add_position, should be part of add_position conversition
    :param bot: telegram.bot
    :param update: telegram.Update
    :return: next state, ADD_POSITION
    """
    bot.send_message(chat_id=update.message.chat_id,text='please send the site you want to add to your personal favorite')
    return ADD_POSITION

def add_position(bot,update,user_data):
    """
     
    :param bot: 
    :param update: 
    :return: 
    """
    #FILTER make sure that

    location = update.message.location
    user_data['location'] = location
    bot.send_message(chat_id=update.message.chat_id,text='looks good, please give this stargazing site a name')
    return ADD_CAPTION

def add_caption(bot,update,user_data):

    #TODO: the logic to retrive location and call db_wrap method to save it into database
    position_entity = dict()
    position_entity['name'] = update.message.text
    position_entity['user_id'] = update.message.from_user.id
    position_entity['latitude']=user_data['location'].latitude
    position_entity['longitude'] = user_data['location'].longitude
    db = db_interface()
    try:
        db.insert_position(position_entity)
    except sqlite3.Error as e:
        bot.send_message(chat_id=update.message.chat_id,text='something went wrong, try it again')
        logging.debug(e)
    else:
        bot.send_message(chat_id=update.message.chat_id,text='great, you site is saved, you can check it through /query command')
    finally:
        db.db_close()
        return ConversationHandler.END


def error(bot,update):
    bot.send_message(chat_id=update.message.chat_id,text='Bad Request, please try it again')
    return ConversationHandler.END

def show_list(bot,update):
    #build a list of string from database result and show it;
    db = db_interface()
    try:
        res = db.select_user_list(update.message.from_user.id)
    except sqlite3.Error as e:
        logging.debug(e)
    finally:
        db.db_close()
    strlist = list()
    if res:
        for row in res:
            strlist.append('*{}* {}'.format(row[0],row[2]))
        response_text = "\n".join(strr for strr in strlist)
        bot.send_message(chat_id=update.message.chat_id,text=response_text,parse_mode="Markdown")
    else:
        bot.send_message(chat_id=update.message.chat_id,text='you have no saved site, use /add_site to add new site')

def query_site(bot,update,args):
    if len(args)==1 and args[0].isdigit():
        db = db_interface()
        id = int(args[0])
        try:
            res = db.select_specific_position(id)
            logging.debug(type(res))
            if res:

                param = {'lon': res[3], 'lat': res[4], 'output': 'internal'}
                query_url = base_api_url + urllib.parse.urlencode(param)
                logging.info(query_url)
                r = requests.get(query_url)
                bot.send_photo(chat_id=update.message.chat_id, photo=BytesIO(r.content),caption=res[2])
            else:
                bot.send_message(chat_id=update.message.chat_id,text='invalid index, please use /show_site_list to find the right number')
        except sqlite3.Error as e:
            logging.debug(e)
        finally:
            db.db_close()
    else:
        bot.send_message(chat_id=update.message.chat_id,text='invalid parameter, please input a number')

def delete_site(bot,update,args):
    if len(args)==1 and args[0].isdigit():
        db = db_interface()
        id = int(args[0])
        try:
            res = db.select_specific_position(id)
            if res and res[1] == update.message.from_user.id:
                db.delete_specific_position(id)
                bot.send_message(chat_id=update.message.chat_id,text='delete successful')
            else:
                bot.send_message(chat_id=update.message.chat_id,text="this site is not in your list, you can't do that!")
        except sqlite3.Error as e:
            logging.debug(e)
            bot.send_message(chat_id=update.message.chat_id,text='invalid index, please use /show_site_list to find the right number')
        finally:
            db.db_close()

    else:
        bot.send_message(chat_id=update.message.chat_id,text='invalid parameter, please input a number')
def main():
    with open('token','r') as f:
        token = f.readline()

    token = token.rstrip('\n')
    updater = Updater(token)
    dispatcher = updater.dispatcher


    help_handler = CommandHandler('help',help)
    location_handler = MessageHandler(Filters.location, reply_location)
    add_position_conversation = ConversationHandler(
        entry_points=[CommandHandler('add_site',trigger_add_position)],
        states={
            ADD_POSITION:[MessageHandler(Filters.location,add_position,pass_user_data=True)],
            ADD_CAPTION:[MessageHandler(Filters.text,add_caption,pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.all,error)]
    )
    show_list_handler = CommandHandler('show_site_list',show_list)
    query_site_handler = CommandHandler('query_site',query_site,pass_args=True)
    delete_site_handler = CommandHandler('delete_site',delete_site,pass_args=True)


    dispatcher.add_handler(add_position_conversation)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(location_handler)
    dispatcher.add_handler(show_list_handler)
    dispatcher.add_handler(query_site_handler)
    dispatcher.add_handler(delete_site_handler)
    updater.start_polling()



if __name__ == '__main__':
    main()