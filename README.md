# Rent a Car – PZW projekt

Backend za aplikaciju za najam vozila. Agencija (admin) upravlja kategorijama i vozilima, a kupci rezerviraju vozila za određeni termin. Projekt za kolegij Programiranje za Web, Sveučilište u Zadru (1. dio: backend).

## Tehnologije

FastAPI, Pydantic, SQLAlchemy 2.0 (asinkrono, asyncpg), Alembic, PostgreSQL 17 (Docker), bcrypt, PyJWT, pytest, pytest-asyncio, httpx, freezegun, ruff.

## Struktura

```
docker-compose.yml       # PostgreSQL (glavna i testna baza)
.env.example             # predložak konfiguracije
docker/                  # init skripta za testnu bazu
api/
  app/
    main.py              # sastavlja aplikaciju
    seed.py              # idempotentni početni podaci
    core/                # konfiguracija, baza, sigurnost, ovisnosti, greške
    routers/             # rute: primaju zahtjev i vraćaju odgovor
    schemas/             # Pydantic sheme za unos, izmjenu i odgovor
    services/            # poslovna pravila
    repositories/        # upiti prema bazi
    models/              # SQLAlchemy modeli
  migrations/            # Alembic migracije 001–004
  tests/                 # pytest testovi
```

## Pokretanje na svježem klonu

Potrebno: Git, Python 3.11+, [uv](https://docs.astral.sh/uv/) i Docker Desktop.

```bash
git clone https://github.com/srdan2006/pzw-rent-a-car.git
cd pzw-rent-a-car

# 1) Konfiguracija (PowerShell: Copy-Item .env.example .env)
cp .env.example .env

# 2) Baza (stvara i bazu rentacar i testnu bazu rentacar_test)
docker compose up -d db

# 3) Backend
cd api
uv venv
source .venv/bin/activate          # PowerShell: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# 4) Tablice i početni podaci
alembic upgrade head
python -m app.seed                 # smije se pokrenuti više puta

# 5) Poslužitelj
uvicorn app.main:app --reload

# 6) Testovi (u drugom terminalu, iz mape api s aktiviranim okruženjem)
pytest
```

Provjera: `http://127.0.0.1:8000/health` vraća `{"status": "ok"}`, a `http://127.0.0.1:8000/docs` prikazuje Swagger.

Vraćanje svih migracija unatrag: `alembic downgrade base`.

## Korisnici iz početnih podataka

| Uloga | Email | Lozinka |
|---|---|---|
| admin | admin@rentacar.hr | admin123 |
| customer | ana@example.com | ana12345 |
| customer | marko@example.com | marko12345 |

Prijava u Swaggeru: `POST /auth/login` s emailom i lozinkom, zatim `access_token` iz odgovora zalijepiti u **Authorize**.

## Uloge i vlasništvo

- **admin** upravlja kategorijama i vozilima, vidi sve rezervacije i mijenja im status.
- **customer** rezervira vozila, vidi i otkazuje samo svoje rezervacije. Tuđa rezervacija vraća 404, kao da ne postoji.
- Popis i detalji kategorija i vozila dostupni su bez prijave.

## Poslovna pravila

| Pravilo | Vrsta | Kod |
|---|---|---|
| Isto vozilo ne smije imati rezervacije koje se preklapaju u terminu (otkazane i vraćene se ne računaju; preuzimanje na dan povratka je dopušteno) | kapacitet | `VEHICLE_NOT_AVAILABLE` |
| Rezervacija se može otkazati najkasnije dan prije preuzimanja | rok | `CANCELLATION_DEADLINE_PASSED` |
| Status ide samo `pending → confirmed → active → returned`; otkazati se može samo `pending` ili `confirmed` | prijelaz statusa | `INVALID_STATUS_TRANSITION` |

Cijenu rezervacije računa backend: broj dana × dnevna cijena kategorije vozila.

## Krajnje točke

| Metoda | Putanja | Pristup |
|---|---|---|
| POST | `/auth/login` | svi |
| POST | `/auth/refresh` | svi (refresh token) |
| GET | `/auth/me` | prijavljeni |
| GET | `/categories` | svi |
| GET | `/categories/{id}` | svi |
| POST | `/categories` | admin |
| PATCH | `/categories/{id}` | admin |
| DELETE | `/categories/{id}` | admin |
| GET | `/vehicles?category_id=` | svi |
| GET | `/vehicles/{id}` | svi |
| POST | `/vehicles` | admin |
| PATCH | `/vehicles/{id}` | admin |
| DELETE | `/vehicles/{id}` | admin |
| GET | `/reservations` | prijavljeni (kupac samo svoje) |
| GET | `/reservations/{id}` | vlasnik ili admin |
| POST | `/reservations` | prijavljeni |
| POST | `/reservations/{id}/cancel` | vlasnik ili admin |
| PATCH | `/reservations/{id}/status` | admin |

Svi popisi primaju `limit` (zadano 20, najviše 100) i `offset` (zadano 0) i vraćaju `items`, `total`, `limit` i `offset`.

## Format grešaka

Svaka greška vraća tijelo istog oblika:

```json
{"code": "VEHICLE_NOT_AVAILABLE", "message": "Vozilo je već rezervirano u tom terminu."}
```

Greška 422 uz to sadrži `errors`, popis polja koja nisu prošla provjeru (`field`, `message`).

| Status | Kod | Značenje |
|---|---|---|
| 400 | `INVALID_DATE_RANGE` | datum povratka nije nakon datuma preuzimanja |
| 400 | `START_DATE_IN_PAST` | rezervacija počinje u prošlosti |
| 401 | `INVALID_CREDENTIALS` | pogrešan email ili lozinka (isti odgovor u oba slučaja) |
| 401 | `NOT_AUTHENTICATED` | zahtjev nema token |
| 401 | `INVALID_TOKEN` | token nije valjan, istekao je ili je pogrešne vrste |
| 403 | `FORBIDDEN` | uloga nema ovlasti za radnju |
| 404 | `NOT_FOUND` | putanja ne postoji |
| 404 | `CATEGORY_NOT_FOUND` | kategorija ne postoji |
| 404 | `VEHICLE_NOT_FOUND` | vozilo ne postoji |
| 404 | `RESERVATION_NOT_FOUND` | rezervacija ne postoji ili nije korisnikova |
| 405 | `METHOD_NOT_ALLOWED` | metoda nije dopuštena na putanji |
| 409 | `CATEGORY_NAME_TAKEN` | kategorija s tim imenom već postoji |
| 409 | `CATEGORY_HAS_VEHICLES` | kategorija ima vozila pa se ne može obrisati |
| 409 | `LICENSE_PLATE_TAKEN` | vozilo s tom registracijom već postoji |
| 409 | `VEHICLE_HAS_RESERVATIONS` | vozilo ima rezervacije pa se ne može obrisati (može se deaktivirati) |
| 409 | `VEHICLE_INACTIVE` | vozilo nije u ponudi |
| 409 | `VEHICLE_NOT_AVAILABLE` | vozilo je zauzeto u traženom terminu |
| 409 | `INVALID_STATUS_TRANSITION` | prijelaz statusa nije dopušten |
| 409 | `CANCELLATION_DEADLINE_PASSED` | rok za otkazivanje je prošao |
| 422 | `VALIDATION_ERROR` | neispravan unos |

## Testovi

`pytest` pokreće 52 testa nad zasebnom bazom `rentacar_test`; tablice se prazne prije svakog testa. Pokriveni su prijava i obnova tokena, uloge, vlasništvo nad zapisom, straničenje, provjera ulaza i poslovna pravila. Rok otkazivanja testira se sa zamrznutim vremenom (freezegun), svaka granica zasebno.
