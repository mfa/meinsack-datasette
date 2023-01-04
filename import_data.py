import csv
import datetime
import re

import click
import sqlite_utils


def import_kurz_data(filename):
    db = sqlite_utils.Database("meinsack.db")
    # this regex requires only one date in the former year!
    with open(filename, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            for _ in row["dates"].split("|"):
                area_id = row["district"]
                dt = datetime.datetime.strptime(_, "%Y-%m-%d").date()
                q = list(
                    db["pickupdate"].rows_where(
                        "date = ? and area_id = ?", [dt, area_id]
                    )
                )
                if not q:
                    db["pickupdate"].insert(
                        {
                            "created": datetime.datetime.utcnow(),
                            "modified": datetime.datetime.utcnow(),
                            "date": dt,
                            "area_id": area_id,
                        }
                    )


def parse_schaal_und_mueller_csv_data(filename, year):
    db = sqlite_utils.Database("meinsack.db")
    # this regex requires only one date in the former year!
    regex = r"(.*)\ ([0-9\.]*)\ (Mo.|Di.|Mi.|Do.|Fr.)\ ([0-9\.\ ]*)"
    with open(filename, "r") as fp:
        for line in fp.readlines():
            if line.startswith("#"):
                continue
            # find weekday and split on it
            area = re.findall(regex, line)[0][0]
            a = list(db["area"].rows_where("description = ?", [area]))
            if not a:
                for in_db, in_csv in (
                    ("Birkach, Botnang, Plieningen", "Birkach, Plieningen, Botnang"),
                    (
                        "Frauenkopf, Hedelfingen (ohne Hafen), Sillenbuch, Riedenberg",
                        "Frauenkopf, Hedelfingen (ohne Hafen) Sillenbuch (mit Riedenberg)",
                    ),
                    (
                        "Stuttgart-West (ohne Kräherwald, Solitude, Wildpark)",
                        "Stuttgart-West (ohne Kräherwald, Solitude,Wildpark)",
                    ),
                    (
                        "Bad Cannstatt I (ohneSteinhaldenfeld), Mühlhausen",
                        "Bad Cannstatt I (ohneSteinhaldenfeld) Mühlhausen",
                    ),
                    (
                        "Büsnau, Degerloch, Dürrlewang, Kräherwald,Solitude, Wildpark",
                        "Büsnau, Degerloch, Dürrlewang,Kräherwald,Solitude, Wildpark",
                    ),
                ):
                    if area == in_csv:
                        a = list(db["area"].rows_where("description = ?", [in_db]))
            if not a:
                assert f"Area not found, {area}"

            area_id = a[0].get("id")
            dates = re.findall(regex, line)[0][3].split()
            # add years
            dates_wyears = [i + str(year) for i in dates[:-1]]
            dates_wyears.append(dates[-1] + str(year + 1))
            for _ in dates_wyears:
                dt = datetime.datetime.strptime(_, "%d.%m.%Y").date()
                q = list(
                    db["pickupdate"].rows_where(
                        "date = ? and area_id = ?", [dt, area_id]
                    )
                )
                if not q:
                    db["pickupdate"].insert(
                        {
                            "created": datetime.datetime.utcnow(),
                            "modified": datetime.datetime.utcnow(),
                            "date": dt,
                            "area_id": area_id,
                        }
                    )


@click.command()
@click.option("--filename")
@click.option("--year", type=int)
def main(filename, year):
    if year <= 2022:
        parse_schaal_und_mueller_csv_data(filename, year)
    else:
        import_kurz_data(filename)


if __name__ == "__main__":
    main()
