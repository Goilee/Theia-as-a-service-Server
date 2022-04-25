# Скрипт для остановки и удаления контейнера
# Аргументы:
#   1: ID или имя контейнера
if [ -z "$1" ]
  then
    echo "Please, specify container ID or name. Example:
$0 ride"
  else
    docker rm -f $1
fi
