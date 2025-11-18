# Weather App Backend

Backend API dla aplikacji pogodowej zbudowany w FastAPI z bazą danych SQLite.

## Funkcjonalności

- **POST /login** - Logowanie użytkownika (zwraca JWT token)
- **GET /weather** - Pobiera wszystkie rekordy pogodowe z bazy danych (publiczne)
- **POST /weather** - Dodaje nowy rekord pogodowy (wymaga autentykacji)
- **PUT /weather** - Aktualizuje rekord pogodowy (wymaga autentykacji)
- **DELETE /weather/{id}** - Usuwa rekord pogodowy (wymaga autentykacji)

## Instalacja - Instrukcja krok po kroku

### Wymagania wstępne

- Python 3.12 lub nowszy (projekt używa Python 3.12.8)
- pip (menedżer pakietów Python)
- Git (opcjonalnie, do klonowania repozytorium)

### Krok 1: Sklonuj lub pobierz projekt

**Opcja A: Jeśli masz repozytorium Git:**
```bash
git clone <URL-repozytorium>
cd ZAI_WeatherApp_Backend
```

**Opcja B: Jeśli masz pliki projektu:**
- Rozpakuj pliki projektu do wybranego folderu
- Otwórz terminal/wiersz poleceń w folderze projektu

### Krok 2: Stwórz wirtualne środowisko (zalecane)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Po aktywacji wirtualnego środowiska w terminalu powinieneś zobaczyć `(venv)` na początku linii.

### Krok 3: Zainstaluj zależności

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

To zainstaluje wszystkie wymagane biblioteki:
- FastAPI - framework webowy
- Uvicorn - serwer ASGI
- SQLAlchemy - ORM do bazy danych
- python-jose - biblioteka do JWT
- passlib - hashowanie haseł
- i inne...

### Krok 4: Zainicjalizuj bazę danych

```bash
python init_db.py
```

To wykona:
- Utworzenie tabel w bazie danych SQLite
- Dodanie 100 przykładowych rekordów pogodowych (10 miast × 10 miesięcy)
- Utworzenie użytkownika admin (username: `admin`, password: `admin`)

Powinieneś zobaczyć komunikaty:
```
Successfully initialized database with 100 weather records.
Successfully added admin user (username: admin, password: admin - hashed).
```

### Krok 5: Uruchom serwer development

```bash
uvicorn main:app --reload
```

Flaga `--reload` automatycznie przeładuje serwer przy zmianach w kodzie (przydatne podczas developmentu).

### Krok 6: Sprawdź czy aplikacja działa

Serwer będzie dostępny pod adresem: `http://localhost:8000`

Otwórz w przeglądarce:
- **Główny endpoint:** http://localhost:8000
- **Dokumentacja Swagger UI:** http://localhost:8000/docs
- **Dokumentacja ReDoc:** http://localhost:8000/redoc

## Uruchomienie bez wirtualnego środowiska (niezalecane)

Jeśli nie chcesz używać wirtualnego środowiska:

```bash
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

**Uwaga:** Instalacja bezpośrednio w systemie może powodować konflikty z innymi projektami Python.

## Rozwiązywanie problemów

### Problem: `python: command not found` lub `python: nie rozpoznano polecenia`

**Rozwiązanie:**
- Windows: Użyj `py` zamiast `python`: `py -m venv venv`
- Linux/macOS: Użyj `python3` zamiast `python`: `python3 -m venv venv`
- Sprawdź czy Python jest zainstalowany: `python --version` lub `python3 --version`

### Problem: `pip: command not found`

**Rozwiązanie:**
- Windows: `py -m pip install -r requirements.txt`
- Linux/macOS: `python3 -m pip install -r requirements.txt`

### Problem: Błędy podczas instalacji zależności

**Rozwiązanie:**
1. Upewnij się, że używasz najnowszej wersji pip:
   ```bash
   pip install --upgrade pip
   ```
2. Sprawdź wersję Pythona (wymagane: Python 3.12+):
   ```bash
   python --version
   ```

### Problem: Błąd podczas uruchamiania `uvicorn`

**Rozwiązanie:**
- Upewnij się, że wszystkie zależności są zainstalowane: `pip install -r requirements.txt`
- Sprawdź czy jesteś w katalogu projektu
- Sprawdź czy wirtualne środowisko jest aktywowane

### Problem: Port 8000 już w użyciu

**Rozwiązanie:**
Uruchom serwer na innym porcie:
```bash
uvicorn main:app --reload --port 8001
```

### Problem: Baza danych nie jest inicjalizowana

**Rozwiązanie:**
- Uruchom ręcznie: `python init_db.py`
- Sprawdź czy plik `weather.db` został utworzony w katalogu projektu
- Sprawdź komunikaty błędów w terminalu

## Deaktywacja wirtualnego środowiska

Po zakończeniu pracy:

```bash
deactivate
```

## Weryfikacja instalacji

Po uruchomieniu serwera, sprawdź:

1. **Główny endpoint:** http://localhost:8000
   - Powinien zwrócić: `{"message": "Weather App API", "docs": "/docs", "redoc": "/redoc"}`

2. **Dokumentacja Swagger:** http://localhost:8000/docs
   - Powinien otworzyć się interfejs Swagger UI

3. **Test endpointu GET /weather:** http://localhost:8000/weather
   - Powinien zwrócić listę 100 rekordów pogodowych

4. **Test logowania:**
   ```bash
   curl -X POST "http://localhost:8000/login" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}"
   ```
   - Powinien zwrócić token JWT

## Domyślne dane logowania

Po inicjalizacji bazy danych:

- **Username:** `admin`
- **Password:** `admin`

**⚠️ Uwaga:** W produkcji zmień te dane na bezpieczniejsze!

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

