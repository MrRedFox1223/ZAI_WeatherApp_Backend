# Weather App Backend

Backend API dla aplikacji pogodowej zbudowany w FastAPI z bazą danych SQLite.

## Funkcjonalności

- **GET /weather** - Pobiera wszystkie rekordy pogodowe z bazy danych
- **PUT /weather** - Aktualizuje rekord pogodowy (ID w ciele żądania)

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

## Struktura projektu

- `main.py` - Główny plik aplikacji FastAPI z endpointami
- `database.py` - Konfiguracja bazy danych SQLite
- `models.py` - Modele SQLAlchemy
- `schemas.py` - Schematy Pydantic do walidacji danych
- `init_db.py` - Skrypt do inicjalizacji bazy danych z przykładowymi danymi
- `requirements.txt` - Zależności projektu

## Baza danych

Baza danych SQLite jest przechowywana w pliku `weather.db` w katalogu głównym projektu.

