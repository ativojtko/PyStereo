import csv
from math import isfinite
from pathlib import Path


# Ak sme nahrali csv súbor, odedelovač nastaví ako , inak použije tab
def _delimiter(file_path):
    return "," if Path(file_path).suffix.lower() == ".csv" else "\t"


# Táto funkcia číta súbor podľa delimitra, ktorý sme určili predošlou funkciou.
# Vytvorí zoznam pre platné a chybné dáta.
# Prázdne riadky preskočí a čítanie pokračuje ďalej.
# Overuje tieto chyby:
# Overuje počet údajov merania - presne 4 alebo 5.
# Overuje typ merania - môžeme mať buď P, L, S.
# Overuje, či sú namerané hodnoty čísla.
# Overuje, či sú zadané hodnoty v správnom číselnom rozsahu.
# Pre póly a lineácie môžeme brať do úvahy aj záporný sklon - rozsah je od -90 do 90 stupňov.
def read_data(file_path):
    data = []
    invalid_rows = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=_delimiter(file_path), strict=True)

        for parts in reader:
            line_number = reader.line_num
            if not parts or not any(value.strip() for value in parts):
                continue

            try:
                if len(parts) not in (4, 5):
                    raise ValueError("Expected 4 or 5 columns: ID, type, azimuth, inclination, comment.")

                measurement_type = parts[1].strip().upper()
                if measurement_type not in ("L", "S", "P"):
                    raise ValueError("Measurement type must be L, S, or P.")

                # Convert text to numbers once, at import
                try:
                    record_id = int(parts[0])
                    azimuth = float(parts[2])
                    inclination = float(parts[3])
                except ValueError as error:
                    raise ValueError("ID must be an integer and angles must be numbers.") from error

                if not isfinite(azimuth) or not isfinite(inclination):
                    raise ValueError("Angles must be finite numbers.")
                if azimuth == 360:
                    azimuth = 0.0
                if not 0 <= azimuth < 360:
                    raise ValueError("Azimuth must be at least 0 and less than 360 degrees.")

                # Lineations and poles are directions; plane dip is between 0 and 90
                minimum = 0 if measurement_type == "S" else -90
                if not minimum <= inclination <= 90:
                    raise ValueError(f"Inclination for {measurement_type} must be between {minimum} and 90 degrees.")

                data.append({
                    "id": record_id,
                    "type": measurement_type,
                    "azimuth": azimuth,
                    "inclination": inclination,
                    "comment": parts[4] if len(parts) == 5 else ""
                })

            # Keep the original fields and error for the table, then continue
            except ValueError as error:
                invalid_rows.append({
                    "line_number": line_number,
                    "values": parts,
                    "error": str(error)
                })

    return data, invalid_rows


# Táto funkcia vytvorí alebo prepíše súbor a zapíše celé merania vrátane azimutu a sklonu.
# csv.writer() - nastavíme súbor, oddeľovač a ukončovač riadkov.
# Ak máme údaje o zaokrúhlení, výsledok zaokrúhli.
# +0.0 zabezpečí, aby nám nevyšla hodnota -0.0 pri sklone.
# Pomocou príkazu writerow() zapíšeme údaje po riadkoch.
def write_data(file_path, data, decimal_places=None):
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=_delimiter(file_path), lineterminator="\n")
        for item in data:
            azimuth = item["azimuth"]
            inclination = item["inclination"]
            if decimal_places is not None:
                azimuth = f"{round(azimuth, decimal_places):.{decimal_places}f}"
                inclination = f"{round(inclination, decimal_places) + 0.0:.{decimal_places}f}"
            writer.writerow([
                item["id"], item["type"], azimuth,
                inclination, item["comment"]
            ])


# funkcia na uloženie obrázka
# finally - aj po neúspešnom exporte grafu sa dočasný popis zo stereogramu vymaže
def write_plot(file_path, figure, caption):
    note = figure.text(
        0.98, 0.02, caption,
        ha="right", va="bottom", fontsize=8, color="gray"
    )
    try:
        figure.savefig(file_path, dpi=300, bbox_inches="tight", facecolor="white")
    finally:
        note.remove()
