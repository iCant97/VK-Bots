# -*- coding: utf-8 -*- 
import requests
import json
import datetime
import pymysql
import random

from colorama import init, Fore, Back, Style
from datetime import datetime, date, time

BOT_NAME = 'Anatolii'
BOT_VERSION = '1.0 stable'
BOT_AUTHOR = 'mahorazb'

VK_TOKEN = '9a823be46c215b90d80e990b3323b7b7e577e37f920e0ae3c448c22cb08a7b79d34a974fe047ec08461ce'
VK_ID = '164648417'

handle = None
ALL_TESTS = 0

init()

def main():
    if not loading(): return
    
    server = LongPoll()
	
    print('[API] Start listening...')
	
    #enableOnline()
	
    listen(server)
  
def listen(server):
    vk_ts = server['response']['ts']
    vk_server = server['response']['server']
    vk_key = server['response']['key']
    
    while True:
        try:
            tmp = requests.get("%s?act=a_check&key=%s&ts=%s&wait=15" % (vk_server, vk_key, vk_ts)).json()
            for event in tmp["updates"]:
                if event['type'] == 'message_new':
				    
                    user_id = event['object']['user_id']
                    if len(event['object']['body']) > 0:
                        text = event['object']['body']
                    else: continue
                        
                    show('Message %d: %s' % (user_id, text))
                    
                    user = fetchOne('SELECT * FROM users WHERE user_id = %d' % user_id)
                    
                    if user == None:
                        join(user_id)
                        continue
                    else:
                        pass

                    if user[12] == 0:
                        send('Анатолий требует подписаться!',user_id)
                        continue
                        
                    if user[7] == 1:
                        #send('Анатолии отдыхает в данный момент.', user_id)
                        continue
                
                    if text.lower() == 'я' or text.lower() == 'me':
                        me(user_id, user)
                        
                    elif text.lower() == 'топ' or text.lower() == 'top':
                        top(user_id)
                        
                    elif text.lower() == 'помощь' or text.lower() == 'help':
                        help_msg(user_id)
					
                    elif text.lower() == 'стоп' or text.lower() == 'stop':
                        if user[8] == 2:
                            handle.execute('UPDATE users SET tmp_test = 0, tmp_type = \'\', tmp_cor = 0, mode = 0, mode_true = \'\', mode_false = \'\', mode_score = 0 WHERE user_id = %d;' % user_id)
                            send('Вы вышли из режима РТ.', user_id)
                            continue
                        else:
                            continue
                    
                    elif text.lower() == 'рус' or text.lower() == 'rus':
                        if user[2] > 0:
                            send('Завершите предыдущее задание!', user_id)
                            continue
                        random.seed()
                        task_id = random.randint(1, ALL_TESTS)
                            
                        giveTask(user_id, task_id, 0)
                            
                    elif text.lower() == 'рт' or text.lower() == 'rt':
                        if user[2] > 0:
                            send('Завершите предыдущее задание!', user_id)
                            continue
                        task_id = 81;
                        
                        giveTask(user_id, task_id, 2)
						    
                    else:
                        text = text.lower()
                        if text.find('showtask', 0,8) >= 0 and user[13] == 3:
                            task_id = text[9:]
                            giveTask(user_id, int(task_id), 5)
                            
                        elif user[2] > 0:
                            arr = text.replace(' ', '').split(',')
                            if checkInt(arr[0]):
                                arr.sort()
                                correct = ''
                                for ans in arr:
                                    if checkInt(ans): correct += ans + ','
                                correct = correct[0:-1]
                                    
                                getTask(user_id, user, correct)
                            else:
                                continue
                        
                        elif text[0] == 'a' or text[0] == 'а':
                            if user[2] > 0:
                                send('Завершите предыдущее задание!', user_id)
                                continue
                                
                            if len(text) == 1: test = fetchAll('SELECT id FROM rus WHERE type = \'A1\'')
                            else: 
                                text = text[1:]
                                act = ''
                                if ord(text[0]) >= 49 and ord(text[0]) <= 57: act = act + text[0]
                                if len(text) == 2:
                                    if ord(text[1]) >= 48 and ord(text[1]) <= 57: act = act + text[1]
                           
                                if len(act) > 0: test = fetchAll('SELECT id FROM rus WHERE type = \'A%s\'' % (act))
                                else: test = fetchAll('SELECT id FROM rus WHERE type = \'A1\'')
 
                            random.seed()                   
                            if len(test) > 0: 
                                task_id = random.randint(0,len(test)-1)
                                giveTask(user_id, test[task_id][0], 1)
                            else:
                                continue
                         
                        elif text.find('орф',0,3) >= 0:
                            if user[2] > 0:
                                send('Завершите предыдущее задание!', user_id)
                                continue
                            if len(text) > 3:    
                                arr = text.split(' ')
                                getTrue(user_id, arr[1].replace(',', '').replace(' ', ''))
                             
                
                elif event['type'] == 'message_reply':
                    show('Reply message.')
            
                elif event['type'] == 'group_join':
                    user_id = event['object']['user_id']
					
                    try:
                        user = fetchOne('SELECT * FROM users WHERE user_id = %d' % user_id)
                        handle.execute('UPDATE users SET `join` = \'1\' WHERE user_id = %d' % user_id)
                    except:
                        pass
				
                    show('%d join to group.' % user_id)
                
                elif event['type'] == 'group_leave':
				
                    user_id = event['object']['user_id']
                    
                    handle.execute('UPDATE users SET `join` = \'0\' WHERE user_id = %d' % user_id)
				
                    show('%d leave group.' % user_id)
             
                elif event['type'] == 'user_block':
                    admin_id = event['object']['admin_id']
                    user_id = event['object']['user_id']
                    unban = event['object']['unblock_date']
                    reason = event['object']['reason']
					
                    handle.execute('UPDATE users SET ban = 1 WHERE user_id = %d' % user_id)
                    
                    show('User %d has been baned by %d. Reason: %d' % (user_id, admin_id, reason))
                    
                    send('Вы были заблокированы администрацией сообщества.',user_id)
                    
                elif event['type'] == 'user_unblock':
                    admin_id = event['object']['admin_id']
                    user_id = event['object']['user_id']
                    auto = event['object']['by_end_date']
                    
                    handle.execute('UPDATE users SET ban = 0 WHERE user_id = %d' % user_id)
                    
                    if auto == 1: show('User %d automatic unbaned. ' % user_id)
                    else: show('User %d unbaned by %d. Auto unban: %d ' % (user_id, admin_id, auto))
                    
                    send('Вы были разблокированы администрацией сообщества.',user_id)
                    
                elif event['type'] == 'group_officers_edit':
                    admin_id = event['object']['admin_id']
                    user_id = event['object']['user_id']
                    level_old = event['object']['level_old']
                    level_new = event['object']['level_new']
                    
                    show('Admin %d set admin access %d (%d to %d)' % (admin_id, user_id, level_old, level_new))
                    
                    handle.execute('UPDATE users SET `admin` = \'%d\' WHERE user_id = %d' % (level_new, user_id))
                    
            vk_ts = tmp["ts"]
            
        except:
            server = LongPoll()
            listen(server)
            return False
		
def help_msg(user_id):
    text = ''
    text += '*id0(ОРФ) - проверка орфографии слова. Пример: ОРФ молоко.\n'
    text += '*id0(А) - взять задание части A. Пример: A4.\n'
    text += '*id0(РУС) - получить задание на рейтинг.\n'
    text += '*id0(РТ) - начать режим РТ.\n'
    text += '*id0(Я) - личная статистика.\n'
    text += '*id0(ТОП) - общий рейтинг.\n\n'
    
    text += 'Доп. информация:\nПоследовательность правильных вариантов ответа не важана!'
    
    send(text, user_id)
    
def getTrue(user_id, word):
    text = ''

    tmp = requests.get('https://speller.yandex.net/services/spellservice.json/checkText?text=%s' % word).json()

    try:
        for string in tmp[0]['s']:
            text += string + ', '
        text = text[:-2]
    except:
        text = 'Все правильно!'
     
    send(text, user_id)

def sendRule(user_id, photo_rule):
    global VK_TOKEN
    
    message = requests.get("https://api.vk.com/method/messages.send?user_id=%d&attachment=%s&access_token=%s&v=5.74" % (user_id, photo_rule, VK_TOKEN)).json()
   
def join(user_id):
    user = requests.get("https://api.vk.com/method/users.get?user_id=%d&v=5.74" % (user_id)).json()
    
    print('Register newbie %s %s' % (user['response'][0]['first_name'], user['response'][0]['last_name']))
    
    handle.execute('INSERT INTO `users` (`user_id`, `user_name`, `join`) VALUES (\'%d\', \'%s %s\', \'1\')' % (user_id, user['response'][0]['first_name'], user['response'][0]['last_name']))
    
    send('Привет, %s! Я тебя долго ждал.\n\nДля того что бы разобраться в моих командах, отправь мне слово *id0(помощь).' % user['response'][0]['first_name'], user_id)

def me(user_id, user):
    if user[5] == 0: num = 0
    else: num = (user[4]/user[5]) * 100
	
    if user[13] == 0: send('Правильно выполнено: %d\nВсего выполнено: %d\nПравильность выполнения: *id0(%.1f%%)\n\nСтатус: *id0(%s)' % (user[4], user[5], num, getLevel(user[4])), user_id)
    else: send('Правильно выполнено: %d\nВсего выполнено: %d\nПравильность выполнения: *id0(%.1f%%)\n\nСтатус: *id0(%s)\nАдминистратор *id0(%d) уровня.' % (user[4], user[5], num, getLevel(user[4]), user[13]), user_id)
    
def top(user_id):
    data = fetchAll('SELECT user_id, user_name, tests FROM users ORDER BY tests DESC LIMIT 5')
	
    text = ''
    i = 1
	
    for user in data:
        text = text + '\n%d *id%d(%s) - \tВерные ответы: %d' % (i,user[0],user[1],user[2])
        i += 1
    
    send(text, user_id)
  
def giveTask(user_id, task_id, mode):
    task = fetchOne('SELECT * FROM rus WHERE id = %d' % task_id)
    text = ''
    
    if mode == 2 and task_id == 81:
        text += 'Вы начали режим РТ!\nЧто бы выйти, напишите "стоп".\n\n'
    
    text += '*id0(%s) (%d). %s\n\n' % (task[1],task[0],task[2])
    
    n = 3
    
    if task[4]:
        for i in range(5):
            if n == 7: text += '%d) %s.\n' % (i+1,task[n])
            else: text += '%d) %s;\n' % (i+1,task[n])
            n += 1
    else:
        text += '%s.\n' % task[3]
    
    if not mode == 5:
        text += '\nОтвет (цифры, через запятую):'
        handle.execute('UPDATE users SET `tmp_test` = \'%d\', `tmp_type` = \'%s\', `tmp_cor` = \'%s\', `mode` = \'%d\' WHERE `user_id` = \'%d\';' % (task_id, task[1], task[8], mode, user_id))
    elif mode == 5:
        text += '\nОтвет: *id0(%s)' % task[8]		

    send(text,user_id)
    
def getTask(user_id, user, answer):
    true = ''
    false = ''
    score = 0
	
    if user[3] == answer:
        if user[8] == 0: 
            send('Верно!\nВведите РУС чтобы продолжить.', user_id)
            aT = 'tests + 1'
            
        elif user[8] == 1:
            send('Верно!', user_id)
            
        elif user[8] == 2:
            true = user[6] + ', '
            score = 4
			
    else:
        if user[8] == 0:
            string = 'Неверно!\nПравильный ответ: *id0(%s)\nВведите РУС чтобы продолжить.' % user[3]
            send(string, user_id)
            aT = 'tests'
            
        elif user[8] == 1: 
            string = 'Неверно!\nПравильный ответ: *id0(%s)' % user[3]
            send(string, user_id)
            
        elif user[8] == 2:
            false = user[6] + ', '
    
    if user[8] == 0: sql = 'UPDATE users SET tmp_test = 0, tmp_cor = 0, tmp_type = \'\', all_tests = all_tests+1, mode = 0, tests = %s WHERE user_id = %d;' % (aT, user_id)
    elif user[8] == 1: sql = 'UPDATE users SET tmp_test = 0, tmp_type = \'\', tmp_cor = 0, mode = 0 WHERE user_id = %d;' % user_id
    elif user[8] == 2: sql = 'UPDATE users SET mode_true = CONCAT(`mode_true`, \'%s\'), mode_false = CONCAT(`mode_false`, \'%s\'), mode_score = mode_score + %d WHERE user_id = %d' % (true, false, score, user_id)
    
    handle.execute(sql)
    
    if user[8] == 2 and user[2] < 107: giveTask(user_id, user[2]+1, 2)
    elif user[8] == 2 and user[2] == 107:
        info = fetchOne('SELECT mode_true, mode_false, mode_score FROM users WHERE user_id = %d' % user_id)
        text = 'Ваш результат: *id0(%d баллов) из 100\n\n' % info[2]
        
        if len(info[0]) > 0:
            true = info[0]
            true = true[:-2]
            text += 'Верные ответы: %s.\n' % true
            
        if len(info[1]) > 0:
            false = info[1]
            false = false[:-2]
            text += 'Неверные ответы: %s.' % false
            
        handle.execute('UPDATE users SET tmp_test = 0, tmp_type = \'\', tmp_cor = 0, mode = 0, mode_true = \'\', mode_false = \'\', mode_score = 0 WHERE user_id = %d;' % user_id)
       
        send(text, user_id)
	
def getLevel(post):
    return {
            post == 0: 'Новичек',
            1 <= post <= 4: 'Ученик',
            5 <= post <= 9: 'Студент',
            10 <= post <= 19: 'Профи',
            20 <= post <= 49: 'Магистр',
            50 <= post <= 99: 'Гуру',
            100 <= post <= 249: 'Мудрец',
            250 <= post <= 499: 'Оракул',
            500 <= post <= 999: 'Гений',
            post >= 1000: 'ВЫСШИЙ РАЗУМ'
    }[True]
    
    
def send(text, user_id):
    message = json.loads(requests.get("https://api.vk.com/method/messages.send?user_id=%d&message=%s&access_token=%s&v=5.74" % (user_id, text, VK_TOKEN)).content)
    try:
        message['response']
    except:
        print('Error send message!')
   
def LongPoll(new = False):
    global ALL_TESTS
    server = json.loads(requests.get("https://api.vk.com/method/groups.getLongPollServer?group_id=%s&access_token=%s&v=5.74" % (VK_ID, VK_TOKEN)).content)
    
    print('[API] Try to connect with VK LongPoll server...', end=' ')

    try:
        server['response']
        print(Style.BRIGHT + Fore.CYAN + 'TRUE' + Style.RESET_ALL)
        ALL_TESTS = handle.execute('SELECT * FROM rus;')
        return server
    except:
        print(Style.BRIGHT + Fore.RED + 'FALSE' + Style.RESET_ALL)
        return False

def loading():
    global handle
    global ALL_TESTS
    print('[API] Loading bot...')
    print('[API] Try to connect with MySQL server...',end=' ')
    
    try:
        connect = pymysql.connect(host = 'localhost', user = 'root', password='', db='bot',  charset='utf8', use_unicode=True, autocommit=True)
        handle = connect.cursor()
        print(Style.BRIGHT + Fore.CYAN + 'TRUE' + Style.RESET_ALL)
        ALL_TESTS = handle.execute('SELECT * FROM rus;')
        print('[API] Loaded tests ' + Style.BRIGHT + Fore.YELLOW + '%d' % (ALL_TESTS) + Style.RESET_ALL)
        return True 
    except:
        print(Style.BRIGHT + Fore.RED + 'FALSE' + Style.RESET_ALL)
        return False
    
def checkInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False  

def fetchOne(sql):
    try:
        handle.execute(sql)
    
        data = handle.fetchone()
   
        return data
        
    except:
        show('Error MySQL request!')
        return False
        
def fetchAll(sql):
    try:
        handle.execute(sql)
    
        data = handle.fetchall()
   
        return data
        
    except:
        show('Error MySQL request!')
        return False
    
def show(text):
    print('[%s] %s' % (datetime.now(),text))

if __name__ == '__main__':
    main()
