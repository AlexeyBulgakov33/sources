# coding=utf-8
import json,serial,getopt,sys,logging,re,time,timeit
device_name ="us-800"
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'mylog.log')
#сохранение конфигурации
def saveConfig():
    with open("Config.json", 'r') as f:
        data = json.loads(f.read())
    f.close()
    for i in data['port']['COM']:
           if i['id'] == '1':
               if not i['name'] == port:
                   i['name'] = port
               if not i['baudrate'] == baudrate:
                   i['baudrate'] = baudrate
    with open('Config.json', 'w') as f:  # открываем файл на запись
        f.write(json.dumps(data, ensure_ascii=False))
#проверка значения порта
def checkPort(port):
    with open("Config.json", 'r') as f:
        data = json.loads(f.read())
    if (port == ""):
        for i in data['port']['COM']:
            if i['id'] == '1':
                port = i['name']
                log_out("Loading the port value from the config")
                con_print("Loading the port value from the config")
    f.close()
    return port
#проверка значения скорости
def checkBaud(baudrate):
    with open("Config.json", 'r') as f:
        data = json.loads(f.read())
    if (baudrate == 0):
        for i in data['port']['COM']:
            if i['id'] == '1':
                baudrate = i['baudrate']
                log_out("Loading the baudrate value from the config")
                con_print("Loading the baudrate value from the config")
    f.close()
    return baudrate
#Выводить ли лог
def log_out(msg):
    if log:
        logging.info(msg)
#а не вывести ли это все в консоль
def con_print(msg):
    if con:
        print(msg)
#расчет crc полученного пакета
def checkCRC(message):
    poly = 0x1021
    reg = 0x0000
    message +='0000'
    for byte in message:
        mask = 0x80
        while(mask > 0):
            reg<<=1
            if ord(byte) & mask:
                reg += 1
            mask>>=1
            if reg > 0xffff:
                reg &= 0xffff
                reg ^= poly
    return reg
#присваение диаметра трубы если его нет
def consumption(diametr):
    with open('diametr.json', 'r') as f:
        data = json.loads(f.read())
        for i in data['diametr']['trumped']:
            if i['id'] == '1':
                k = i[str(diametr)]
    return k
#подсчет расхода
def counter(diametr,t):
    q = consumption(diametr)
    return q*t
ft1 = False
ft2 = False
fd1 = False
fd2 = False
t = time.time()
t2 = time.time()
diametr1 = 15
diametr2 = 25
port = ""
baudrate = 0
save = False
log = True
con = False
shortopts = 'p:b:s:l:c:t:y:d:f:h'
longopts = ["port","baudrate","save", "log", "quet mode","start t1","start t2", "init d1", "init d2" "help"]
try:
    opts,argv = getopt.getopt(sys.argv[1:],shortopts,longopts)
except getopt.GetoptError, err:
    print str(err)
    usage()
    exit(2)
#обработка аргументов консоли
for o, a in opts:
    if o == '-p':
         port = a
    elif o == "-b":
        baudrate = a
    elif o == "-s":
        save = a
    elif o == "-l":
        log = a
    elif o == "-c":
        con = a
    elif o == "-t":
        ft1 = a
        t1 = time.time()-t
    elif o == "-y":
        ft2 = a
        t2 = time.time()-t
    elif o == "-d":
        fd1 = True
        diametr1 = a
    elif o == "-f":
        fd2 = True
        diametr2 = a
    elif o == "-h":
        usage()
        exit(0)
    else:
        usage()
        exit(2)
#проверка на ввод данных
port = checkPort(port)
baudrate = checkBaud(baudrate)
init_port(port,baudrate)
if save:
    saveConfig()
if not ft1:
    t1 = time.time()-t
if not ft2:
    t2 = time.time()-t
if not fd1:
    diametr1 = 15
if not fd2:
    diametr2 = 25
while True:
    #считывание пакета
    package = sys.stdin.readline()
    package = re.sub(r'\s', '', package)
    n = len(package)
    not_my_crc = "0x" + package[n - 4] + package[n - 3] + package[n - 2] + package[n - 1]
    package = package[0:-4]
    my_crc = checkCRC(package)
    my_crc = str(hex(my_crc))
    if not_my_crc == my_crc:
        print "Correct package"
		if (package == "010302000007"):
            #Все параметры по первому каналу
            t1 = time.time() - t
            t1 /= 3600
            print consumption(diametr1)
            print counter(diametr1, t1)
            print t1
        if (package == "010302200007"):
            #Все параметры по второму каналу
            t2 = time.time() - t
            t2 /= 3600
            print consumption(diametr2)
            print counter(diametr2, t2)
            print t2
        if (package == "010302000002"):
            #Расход по первому каналу
            print consumption(diametr1)
        if (package == "010302200002"):
            #Расход по второму каналу
            print consumption(diametr2)
        if (package == "010302020002"):
            #Накопленный объем в первом канале
            t1 = time.time() - t
            t1 /= 3600
            print counter(diametr1, t1)
        if (package == "010302220002"):
            #Накопленный объем во втором канале
            t2 = time.time()-t
            t2 /= 3600
            print counter(diametr2, t2)
        if (package == "010302050002"):
            #Время наработки первый канал
            print t1 / 3600
        if (package == "010302250002"):
            #Время наработки второй канал
            print t2 / 3600
