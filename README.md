# Weather App Backend

Backend API dla aplikacji pogodowej zbudowany w FastAPI z bazą danych SQLite.

## Funkcjonalności

- **POST /login** - Logowanie użytkownika (zwraca JWT token)
- **GET /weather** - Pobiera wszystkie rekordy pogodowe z bazy danych (publiczne)
- **POST /weather** - Dodaje nowy rekord pogodowy (wymaga autentykacji)
- **PUT /weather** - Aktualizuje rekord pogodowy (wymaga autentykacji)
- **DELETE /weather/{id}** - Usuwa rekord pogodowy (wymaga autentykacji)

## Instalacja

1. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

2. Zainicjalizuj bazę danych z przykładowymi danymi:
```bash
python init_db.py
```

## Uruchomienie

Uruchom serwer development:
```bash
uvicorn main:app --reload
```

Serwer będzie dostępny pod adresem: `http://localhost:8000`

## Dokumentacja API

Po uruchomieniu serwera, dokumentacja Swagger jest dostępna pod adresem:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Format danych

### Pobieranie danych (GET /weather)
Zwraca listę rekordów:
```json
[
  {
    "id": 1,
    "city_name": "New York",
    "date": "2024-01-14",
    "temperature": 5.0
  }
]
```

### Aktualizacja danych (PUT /weather)
Ciało żądania:
```json
{
  "id": 1,
  "city_name": "New York",
  "date": "2024-01-14",
  "temperature": 5.0
}
```

Zwraca zaktualizowany rekord w tym samym formacie.

### Logowanie (POST /login)
Ciało żądania:
```json
{
  "username": "admin",
  "password": "admin"
}
```

Odpowiedź:
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Używanie tokena
Wszystkie endpointy wymagające autentykacji (POST, PUT, DELETE) wymagają nagłówka:
```
Authorization: Bearer <token>
```

## Autentykacja

Endpointy POST, PUT i DELETE wymagają autentykacji poprzez JWT token otrzymany podczas logowania. Token należy przekazać w nagłówku `Authorization` jako `Bearer <token>`.

Domyślny użytkownik:
- Username: `admin`
- Password: `admin`

## Struktura projektu

- `main.py` - Główny plik aplikacji FastAPI z endpointami
- `auth.py` - Funkcje autentykacji i weryfikacji JWT tokenów
- `database.py` - Konfiguracja bazy danych SQLite
- `models.py` - Modele SQLAlchemy
- `schemas.py` - Schematy Pydantic do walidacji danych
- `init_db.py` - Skrypt do inicjalizacji bazy danych z przykładowymi danymi
- `requirements.txt` - Zależności projektu

## Baza danych

Baza danych SQLite jest przechowywana w pliku `weather.db` w katalogu głównym projektu.

## Bezpieczeństwo

### SQL Injection
Aplikacja jest zabezpieczona przed atakami SQL injection poprzez użycie SQLAlchemy ORM, które automatycznie parametryzuje wszystkie zapytania do bazy danych. Wszystkie operacje na bazie danych używają bezpiecznych metod ORM zamiast bezpośrednich zapytań SQL.

### Hashowanie haseł
Hasła użytkowników są przechowywane jako zahashowane wartości używając bcrypt. Hasła są automatycznie hashowane podczas tworzenia użytkownika w `init_db.py`.

