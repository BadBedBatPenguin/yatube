## Yatube

Социальная сеть с постами, комментами и лентой подписок :)

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```Shell
git clone https://github.com/BadBedBatPenguin/yatube.git
```

```Shell
cd Yatube
```

Cоздать и активировать виртуальное окружение:

```Shell
python3 -m venv env
```

```Shell
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```Shell
python3 -m pip install --upgrade pip
```

```Shell
pip install -r requirements.txt
```

Выполнить миграции:

```Shell
python3 manage.py migrate
```

Запустить проект:

```Shell
python3 manage.py runserver
```

## Использованные технологии

Django\
Django ORM\
SQLite\
Unittest

## Автор

Цёсь Максим ([BadBedBatPenguin] (https://github.com/BadBedBatPenguin))
