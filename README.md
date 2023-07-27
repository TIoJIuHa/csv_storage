# CSV storage

Хранилище для csv файлов, позволяет хранить файлы и получать информацию из них.

### Как запустить проект в Docker-контейнере

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/TIoJIuHa/csv_storage
```
```
cd csv_storage
```

Запустить Docker и создать образ:
```
docker build -t flask-app csv_storage/
```

Из созданного образа запустить контенер:
```
docker run -d -p 5000:5000 flask-app
```

Сайт будет доступен по адресу `http://127.0.0.1:5000`.

### Примеры запросов к API

После запуска проекта по адресу `http://127.0.0.1:5000/api/ui` будет доступна документация для API.

Пример запроса:
```
GET http://127.0.0.1:5000/api/files
```
Пример ответа сервера:
```
[
    {
        "columns": [
            "user id",
            "subscription type",
            "monthly revenue",
            "join date",
            "last payment date",
            "country",
            "age",
            "gender",
            "device",
            "plan duration"
        ],
        "id": 2,
        "name": "Netflix Userbase.csv"
    },
    {
        "columns": [
            "продукт",
            "ед.измерения"
        ],
        "id": 1,
        "name": "ingredients.csv"
    }
]
```

Запрос с переданным параметром `name` (будут отображаться файлы, содержащие в названии переданное значение):
```
GET http://127.0.0.1:5000/api/files?name=edie
```
Пример ответа сервера:
```
[
    {
        "columns": [
            "продукт",
            " ед.измерения"
        ],
        "id": 1,
        "name": "ingredients.csv"
    }
]
```

Пример запроса:
```
POST http://127.0.0.1:5000/api/files
```
```
{
    "name": "file.csv",
    "data": "first;second;third\nMasha;Tanya;Petya\nSasha;Luda;Artem\nMisha;Vanya;Lena"
}
```
Пример ответа сервера:
```
{
    "columns": [
        "first",
        "second",
        "third"
    ],
    "id": 3,
    "name": "file.csv"
}
```

Пример запроса:
```
GET http://127.0.0.1:5000/api/files/3
```
Пример ответа сервера:
```
[
    {
        "first": "Masha",
        "index": 0,
        "second": "Tanya",
        "third": "Petya"
    },
    {
        "first": "Sasha",
        "index": 1,
        "second": "Luda",
        "third": "Artem"
    },
    {
        "first": "Misha",
        "index": 2,
        "second": "Vanya",
        "third": "Lena"
    }
]
```
Также в запросе по этому адресу в качестве параметров можно передавать названия столбцов из файла (будут отображаться записи удовлетворяющие фильтрам):
```
GET http://127.0.0.1:5000/api/files/3?second=anya&third=l
```
Пример ответа сервера:
```
[
    {
        "first": "Misha",
        "index": 2,
        "second": "Vanya",
        "third": "Lena"
    }
]
```

Пример запроса:
```
DELETE http://127.0.0.1:5000/api/files/3
```
Пример ответа сервера:
```
Файл 3 'file.csv' успешно удалён
```