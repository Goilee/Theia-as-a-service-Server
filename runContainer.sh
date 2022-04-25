# Скрипт для запуска контейнера на случайном порту. Выводит порт и ID
# Аргументы:
#   1: IP, на котором запускать
if [ -z "$1" ]
  then
    echo "Please, specify IP. Example:
$0 localhost"
  else
    ID=$(docker run --ip=$1 --detach --publish 3000 $(cat image))
    docker inspect -f '{{ (index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort }}' $ID
    echo $ID
fi
