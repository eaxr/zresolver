# zresolver

Тестовая модель для разрешения доменных имен.
Здесь много ограничений в работе программы, но она может обращатся к базе данных, например, sqlite3 и в ответ отправлять хранящиеся в базе значения.
Если в базе нет значения, то программа обращается к вышестоящему dns.
Есть задание основных параметров через файл resolver.conf.
