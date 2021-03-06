# zresolver

Тестовая модель для разрешения доменных имен. Здесь много ограничений в работе программы, т.к. это модель создана для обучения работе dns. Она может обращатся к базе данных, например, sqlite3 и в ответ отправлять хранящиеся в базе значения. Если в базе нет значения, то программа обращается к вышестоящему dns. Есть задание основных параметров через файл resolver.conf.

Есть пакет для fedora, который устанавливает дистрибутив в /usr/lib/zresolver, создается директория /var/log/zresolver для лога и /etc/zresolver для файла конфигурации. В файле конфигурации /etc/zresolver/zresolver.conf есть параметры:

    resolverIP = 127.0.0.1 - адрес, который будет использоватся программой
    resolverPORT = 53530 - порт который будет слушать UDP запросы
    masterDNS = 192.168.0.99, 8.8.8.8, 1.1.1.1 - список вышестоящих dns, если по запросу, в базе, не найдено значение
    logfile = /var/log/zresolver/logfile.log - путь до файла лога
    nameDB = test_resolver.db - название базы данных, хранится по пути /usr/lib/zresolver
    typeDB = sqlite3 - тип базы данных

Это модель для обучения, в ней преобразования выполняются из байткода в hex код и обратно. Поэтому многие преобразования выполняются по несколько раз. Пример, как обрабатывается сообщение:

![alt text](https://github.com/eaxr/zresolver/blob/master/images/resolver4.png?raw=true)

После того как сообщение обработано и есть ифнормация для отправки ответа, формируется сообщение для отправки. Формирование заголовка:

![alt text](https://github.com/eaxr/zresolver/blob/master/images/resolver5.png?raw=true)

Если в базе данных программы нет запрашиваемого доменного имени, то она обращается к вышестоящему dns и результат сохраняет в базе данных. Поэтому, когда есть запрос иммени, который есть в базе данных, то программа отправляет его сразу. Программа периодически обращается к базе, чтобы изменять значение TTL хранящихся данных. Пример сохранённых значений в базе данных:

![alt text](https://github.com/eaxr/zresolver/blob/master/images/resolver23.png?raw=true)

Пример запуска программы и создания запросов через nslookup. После запуска программа ожидает udp запросы и начинает их обрабатывать:

![alt text](https://github.com/eaxr/zresolver/blob/master/images/resolver30.png?raw=true)

Если на машине, где установлен пакет, задать адрес доступный для других машин и указать открытый dns порт, а на другом машине указать адрес машины с запущенной программой, то возможно обрабатывать dns сообщения. Демонстрация:
![alt text](https://github.com/eaxr/zresolver/blob/master/images/zResolver_1.gif?raw=true)
