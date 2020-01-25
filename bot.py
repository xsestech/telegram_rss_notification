# -*- coding: utf-8 -*-
from telebot import apihelper #this is lib for proxy
import telebot #import lib for telegram
from telebot import types
import config 
import requests # import lib for getting html from site
from bs4 import BeautifulSoup as BS # import lib for parsing
import sqlite3
import logging # import lib for logging data

logging.basicConfig(filename='bot.log',level=logging.DEBUG)
r = requests.get('http://tproger.ru/feed') #get html from tproger
rss = BS(r.content,features='xml') #setup parser
bot = telebot.TeleBot(config.TOKEN) #create bot obj and configure Token
apihelper.proxy = {'https':'socks5://176936165:qCsF0ugt@grsst.s5.opennetwork.cc:999'} #add proxy
conn = sqlite3.connect(config.DBPATH,check_same_thread = False)
cursor = conn.cursor()

mybots = {}
titles = ('1',) #set for caching titles


@bot.message_handler(commands=['start','help'])
def resp(message):
    start_message = "Привет,<b>{}</b>\nЭто бот для получения уведомления о новостях с сайтов \n Чтобы добавить url напишите /url rss_url.ru/feed\nДля того, чтобы получить n кол-во новостей используйте /get num_of_news ".format(message.chat.first_name) # create start msg
    bot.send_message(message.chat.id,start_message,parse_mode='html') #send start smg
    cursor.execute("SELECT id FROM users") # sql
    ids = cursor.fetchall()[0] # get all ids from db
    if message.chat.id not in ids: # add user to db if it is new
        logging.info("New user {}".format(message.chat.id))
        cursor.execute("INSERT INTO users(ID) VALUES({})".format(str(message.chat.id)))
        conn.commit()


@bot.message_handler(commands=['get'])
def lastest_news(message):
    try:
        cursor.execute("SELECT url FROM users WHERE id={}".format(message.chat.id)) #get url to parse
        url = 'http://'+cursor.fetchall()[0][0]
        r = requests.get(url) #get html from tproger
        rss = BS(r.content,features='xml') #setup parser
        try:
            num = int(message.text.replace("/get ",'')) # get num of news
        except ValueError:
            bot.send_message(message.chat.id,"Неправильный формат",parse_mode='html')
        news=""

        for i in range(num): #get latest news
            news+=str(i+1) + '. '
            news+=rss.find_all('item')[i].title.text+'\n\n'
        markup = types.InlineKeyboardMarkup(row_width=2)
        for x in range(num):
            item = types.InlineKeyboardButton(x+1,callback_data=str(x+1))
            markup.add(item)
        bot.send_message(message.chat.id,news,parse_mode='html',reply_markup=markup)
    except Exception as e:
        print(repr(e))


@bot.message_handler(commands=['url']) # update user's rss url
def resp(message):
    try:
        usrurl = message.text.replace("/url ",'')
        cursor.execute("UPDATE users SET url='{0}' WHERE id = {1};".format(str(usrurl),message.chat.id))
        conn.commit()
    except Exception as e:
        print(repr(e))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call): # send news for user's request 
    try:
        if call.message:
            i = int(call.data)
            cursor.execute("SELECT url FROM users WHERE id={}".format(call.message.chat.id)) # get urls
            url = 'http://'+cursor.fetchall()[0][0]
            r = requests.get(url) #get html 
            rss = BS(r.content,features='xml') #setup parser
            msg="<b>"#add bold to title
            msg +=rss.find_all('item')[i].title.text
            msg+="</b>"
            msg+= '\n'
            msg.replace('\n','')
            msg+= BS(rss.find_all('item')[i].description.text, "lxml").text #delete all html
            link = BS(rss.find_all('item')[i].description.text, "lxml").find('a').get('href') #get link
            msg+="<a href='{}'".format(link)+">"+"Watch in site"+"</a>" #send link to user
            bot.send_message(call.message.chat.id,msg,parse_mode='html')
    except Exception as e:
        print(repr(e))
                

try: #check all users and send updates from rss
    cursor.execute("SELECT id FROM users")
    ids = cursor.fetchall()[0]
    for id in ids:
        cursor.execute("SELECT url FROM users WHERE id={}".format(id))
        url = 'http://'+cursor.fetchall()[0][0]
        r = requests.get(url) #get html from tproger
        rss = BS(r.content,features='xml') #setup parser
        last=rss.find('item')
        if last.title.text not in titles:
            msg = "<b>"
            msg+=last.title.text
            msg+="</b>"
            msg.replace('\n','')
            msg+= BS(last.description.text, "lxml").text
            link = BS(last.description.text, "lxml").find('a').get('href')
            msg+= '\n'
            msg+="<a href='{}'".format(link)+">"+"Watch in site"+"</a>"
    
            bot.send_message(id, text=msg,parse_mode='html')
            titles = titles + (last.title.text,)
except Exception as e:
    print(repr(e))


bot.polling(none_stop=True) #start bot