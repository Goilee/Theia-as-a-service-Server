# Запускает контейнер RIDE на случайном порту и возвращает выделенный порт и ID контейнера
ID=$(docker run -dp 3000 ride)
docker inspect -f '{{ (index (index .NetworkSettings.Ports "3000/tcp") 0).HostPort }}' $ID
echo $ID
