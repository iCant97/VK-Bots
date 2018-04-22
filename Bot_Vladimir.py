# -*- coding: utf-8 -*- 
import requests
import time
import json

from threading import Thread
from datetime import datetime
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style

init()

class Bot(Thread):
    
    def __init__(self, token, group_id):
        Thread.__init__(self)
        self.token = token
        self.group_id = group_id
        
        self.version = '5.74'
        
        self.ts = 0
        self.key = None
        self.server = None
        self.wait = 10
        
        self.session = requests.Session()
        
        self.connect()
    
    def connect(self):
		
        values = {
            'group_id': self.group_id,
        }
        
        response = self.method('groups.getLongPollServer', values)
        
        print('[API] Try to connect with VK LongPoll server...', end=' ')

        try:
            self.server = response['response']['server'] 
            self.key = response['response']['key'] 
            self.ts = response['response']['ts']
            print(Style.BRIGHT + Fore.CYAN + 'TRUE' + Style.RESET_ALL)
        except:
            print('Error: %s' % response)
            return
        
        
    def check(self):
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
        }
        try: 
            response = self.session.get(
                self.server,
                params=values,
                timeout=30
            ).json()
            
            self.ts = response['ts']
        
            for raw in response['updates']:
                if raw['type'] == 'message_new': 
                    print('[%s] ASK %s: %s' %  (datetime.now(),raw['object']['user_id'],raw['object']['body']))
                    if raw['object']['body'] == '/time':
						
                        clock = datetime.now()
                        
                        clock = str(clock)
						
                        clock = clock[:-7]
                        val = {
                            'user_id' : raw['object']['user_id'],
                            'message' : '%s' % clock
                        }
                    
                        self.method('messages.send', val)
                        
                elif raw['type'] == 'message_reply':
                    print('[%s] REPLY %s' % (datetime.now(),raw['object']['user_id']))                        
                            
        except:
            print('[%s] Reconnect...' % datetime.now())
            self.connect()
		    
        return []
        
           
    def run(self):
        print('[API] Start listening...')
        while True:
            for event in self.check():
                return event
        

    def method(self, method, values = None):
		
        values = values.copy() if values else {}
        
        values['access_token'] = self.token
        values['v'] = self.version
		
        response = self.session.post(
            'https://api.vk.com/method/' + method,
            values
        ).json()
        
        if 'error' in response:
            print('Error: %s' % response)
            return False
        else: return response
        
class Sender(Thread):
    
    def __init__(self, bot):

        Thread.__init__(self)
        self.bot = bot
        self.topics = []
    
    def run(self):

        while True:
           time.sleep(1)
           
           clock = datetime.now()
           
           if (clock.hour == 11 and clock.minute == 39 and clock.second == 1) or (clock.hour == 15 and clock.minute == 0 and clock.second == 1) or (clock.hour == 17 and clock.minute == 0 and clock.second == 1) or (clock.hour == 22 and clock.minute == 0 and clock.second == 1):
			   
               self.topics.clear()
               text = self.getTProger()
               text = 'Новости ТП:' + text
               self.bot.method('messages.send', {'user_id' : 396433116, 'message' : text})
               
           elif (clock.hour == 8 and clock.minute == 45 and clock.second == 1) or (clock.hour == 11 and clock.minute == 0 and clock.second == 1) or (clock.hour == 20 and clock.minute == 0 and clock.second == 1):
			   
               text = self.getHabr()
               text = 'Новости Хабрахабр:' + text
               self.bot.method('messages.send', {'user_id' : 396433116, 'message' : text})
               
           
    def getTProger(self):
        r = requests.get('https://tproger.ru').text

        soup = BeautifulSoup(r, 'lxml')

        content = soup.find_all('div', class_= 'news-row ')
        
        text = ''

        for tp in content:
            text += '\n\n%s.' % tp.a.contents[0]
            text += '\n%s' % tp.a.get('href')
            strr = tp.a.get('href')
            self.topics.append(strr)
	        
        return text
        
    def getHabr(self):
        r = requests.get('https://habrahabr.ru/all/').text

        soup = BeautifulSoup(r, 'lxml')

        content = soup.find_all('a', class_= 'post__title_link')
        
        text = ''

        for topic in content:
            text += '\n\n%s' % topic.contents[0]
            text += '\n%s' % topic.get('href')
	        
        return text
        
class Command(Thread):
    
    def __init__(self, bot, send):

        Thread.__init__(self)
        self.bot = bot
        self.send = send
        self.ls = []
    
    def run(self):
        while True:
            cmd = input()
            
            if cmd.lower() == 'gethb':
                r = requests.get('https://habrahabr.ru/all/').text

                soup = BeautifulSoup(r, 'lxml')

                content = soup.find_all('a', class_= 'post__title_link')
                
                for topic in content:
                    print('%s' % topic.contents[0], end = Fore.CYAN + Style.BRIGHT + ' - ' + Style.RESET_ALL)
                    print('%s' % topic.get('href'))
                    
            elif cmd.lower() == 'gettp':
                r = requests.get('https://tproger.ru').text

                soup = BeautifulSoup(r, 'lxml')

                content = soup.find_all('div', class_= 'news-row ')
               
                all_ = len(content)
                
                for i, topic in enumerate(content):
                    print('%s' % topic.a.contents[0], end = Fore.CYAN + Style.BRIGHT + ' - ' + Style.RESET_ALL)
                    print('%s' % topic.a.get('href'))
                    if topic.a.get('href') == self.send.topics[i]:
                        all_ -= 1
                        
                        
                if all_ == len(content): text = 'Все темы новые!'
                elif all_ > 0: text = 'Новых тем: %d' % all_
                else: text = 'Новых тем нет!'
                
                print(text)
        
        
def main():
    print('[API] Loading bot...')
    
    bot = Bot('fa7883e679d6d9229cde206ac5c70410dc3ede2b83208201622d03e8234f0402a53e4106dd8f3164beeee', 165377765)
    send = Sender(bot)
    cmd = Command(bot, send)
    
    bot.start()
    send.start()
    cmd.start()
        
if __name__ == '__main__':
    main()
