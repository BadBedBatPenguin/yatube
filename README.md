## Yatube
Social network where user may create his own account, post text and pictures, follow another users and comment posts.
Used technologies: Django, Django ORM, SQLite, Unittest


## How to run project

Clone repo and move to its directory:

```Shell
git clone https://github.com/BadBedBatPenguin/yatube.git
```

```Shell
cd Yatube
```

Create and activate virtual environment:

```Shell
python3 -m venv env
```

```Shell
source env/bin/activate
```

Install packages from requirements.txt:

```Shell
python3 -m pip install --upgrade pip
```

```Shell
pip install -r requirements.txt
```

Migrate:

```Shell
python3 manage.py migrate
```

Run project:

```Shell
python3 manage.py runserver
```

## Author

Max Tsyos ([BadBedBatPenguin](https://github.com/BadBedBatPenguin))
