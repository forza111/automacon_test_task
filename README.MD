Приложение для создания / чтения пользовательских заметок. 
Используется JWT аутентификация.

### Запуск приложения
#### Запустите контейнеры
```shell
docker-compose up --build
```
#### Создайте пользователя в базе данных
В базе данных должен храниться пароль в зашифрованном виде. Чтобы получить хэш 
пароля с тем же типом шифрования, что и приложение, необходимо выполнить следующие действия:  
```shell
docker-compose exec web bash
python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context.hash('admin') #Передаем в функцию hash пароль
'$2b$12$E/wgiU8ZjTlrljd90PmgweKphxZDG1RK3BfoLRjKYsvNWp4WgC64O' #hash пароля
```
Запишите пользователя в БД, для этого выполните следующие действия:
```shell
docker-compose exec db psql -U postgres
INSERT into users (email, password) VALUES ('admin@example.com', '$2b$12$E/wgiU8ZjTlrljd90PmgweKphxZDG1RK3BfoLRjKYsvNWp4WgC64O');
```

Приложение будет доступно по адресу [http://localhost:8000/](http://localhost:8000/)  
Введите логин и пароль.

----
