# Ecommerce Project 2

Projet e-commerce realise avec Django.

## Technologies

- Python
- Django
- SQLite

## Installation

Cloner le projet :

```powershell
git clone https://github.com/89DJUD/ecommerce_project2.git
cd ecommerce_project2
```

Creer et activer un environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Installer Django :

```powershell
pip install django
```

## Lancer le projet

Aller dans le dossier Django :

```powershell
cd ecommerce
```

Appliquer les migrations :

```powershell
python manage.py migrate
```

Lancer le serveur :

```powershell
python manage.py runserver
```

Ouvrir ensuite :

```text
http://127.0.0.1:8000/products/
```

## Fonctionnalites

- Liste des produits
- Detail d'un produit
- Liste des categories
- Detail d'une categorie
- Images des produits

## Auteur

89DJUD
