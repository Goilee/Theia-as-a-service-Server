# Theia application server

Этот проект предназначен для запуска сред разработки, основанных на [Theia](https://theia-ide.org/), как application-as-a-service. В теории, должно работать с произвольным приложем, упакованным в докер-контейнер, и публикующим единственный порт.

Принцип работы состоит в том, что на каждое входящее соединение создаётся и запускается новый контейнер, а клиент перенаправляется на него. Фоновый процесс регулярно проверяет логи контейнеров, и если видит, что клиент покинул контейнер (закрыл вкладку), то контейнер останавливается.

Клиентам предоставится страница их проектов, каждый проект представляет собой докер контейнер. Клиенты могут создавать, удалять и запускать проекты (контейнеры), а также делиться ссылкой на конетйнер с другими пользователями.

# Необходимое ПО

- Python 3
- [Docker](https://docs.docker.com/engine/install/)

Необходимые модули Python можно установить с помощью утилиты pip из корневой директории проекта:

    sudo apt install pip
    sudo pip install -r requirements.txt

# Настройка Google

Для работы Google авторизации необходимо настроить проект в [console.cloud.google.com](console.cloud.google.com).

1. Создаём проект, имя и прочие параметры настраиваем по желанию.
![image](https://user-images.githubusercontent.com/38074143/167285372-3cb81f76-7345-4cf9-be99-1155162e9e6f.png)
![image](https://user-images.githubusercontent.com/38074143/167285397-f999dae0-b81f-4a3f-9f5c-1412b6a0bc61.png)
![image](https://user-images.githubusercontent.com/38074143/167285415-b8a87442-abb2-4abe-be62-2d13bbe74820.png)
![image](https://user-images.githubusercontent.com/38074143/167285452-ea5851b8-5a09-4e43-aa57-982bf2a4d7b6.png)
2. Настраиваем OAuth consent screen.
2.1. В меню навигации (левый край экрана) заходим в APIs & Services --> OAuth consent screen.
![image](https://user-images.githubusercontent.com/38074143/167285485-b5a84e39-134a-4882-91c6-fb0658a1494a.png)
2.2. Указывает User Type = External и нажимаем CREATE.
![image](https://user-images.githubusercontent.com/38074143/167285509-84d09237-34af-4986-8ccc-e971d05b0a2d.png)
2.3. Заполняем данные о приложениии нажимаем SAVE AND CONTINUE.
![image](https://user-images.githubusercontent.com/38074143/167285622-bdff2bdd-471b-446e-88a1-c0153bb05213.png)
2.4. На экранах Scopes, Test users и Summary можно ничего не менять.
![image](https://user-images.githubusercontent.com/38074143/167285655-89c7c838-1691-4687-86e1-00f3627e16cf.png)
![image](https://user-images.githubusercontent.com/38074143/167285670-30c35174-ed7d-40c9-8425-91ef44bddc94.png)
![image](https://user-images.githubusercontent.com/38074143/167285681-418c55f3-5e4d-408f-a0a0-f93996c9c5e9.png)
3. Настраиваем Credentials.
3.1. Переходим в APIs & Services -> Credentials.
![image](https://user-images.githubusercontent.com/38074143/167286196-be90b33c-3baf-439e-b578-ff1f49a5e94c.png)
3.2. Создаём OAuth client ID.
![image](https://user-images.githubusercontent.com/38074143/167286227-9c214392-05c6-4967-a6fb-46dfadd63ef4.png)
![image](https://user-images.githubusercontent.com/38074143/167286249-8b65ad1d-061f-4c81-bffe-ecc80ef39813.png)
3.3. Заполняем поля данными о приложенни. В Authorized redirect URIs добавляем адрес "http://\<host\>/callback", заменив \<host\> на адрес своего хоста.
![image](https://user-images.githubusercontent.com/38074143/167286294-1bf8d034-8146-4e3c-a684-abc92df75071.png)
![image](https://user-images.githubusercontent.com/38074143/167286301-08cdf565-3d25-46b7-acfd-b0e8c6d45fc6.png)
4. Скачиваем сгенерированные данные в формате JSON. Копируем файл в корневую директорию под названием, указанным в config.ini (по умолчанию client_secret.json).
![image](https://user-images.githubusercontent.com/38074143/167286329-8a59a7a1-d38e-4900-b65a-9025b5298d35.png)

# Настройка параметров сервера

Файл [config.ini](https://github.com/Goilee/RIDE-server/blob/4a31a5c23972b775c0237a7334b9b3bdfded33a8/config.ini) содержит все настраиваемые параметры сервера.

# Запуск

Сервер запускается командой

    sudo python3 run_project.py [--debug]
    
Опция --debug запускает сервер в отладочном режиме. Рекомендуется использоваться при тестировании, но не в релизе, поскольку с этой опцией в случае необработанного исключения клиенты увидят его подробности.
