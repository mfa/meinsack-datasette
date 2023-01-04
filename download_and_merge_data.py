import csv
import datetime
import hashlib
from collections import defaultdict

import click
import httpx
from ics import Calendar

DISTRICT_MAP = {
    # one known new district name: district id
    "hedelfingen": 1,
    "feuerbach-mitte": 2,
    "moehringen-mitte": 3,
    "rotebuehl": 4,
    "weilimdorf": 5,
    "untertuerkheim": 6,
    "zuffenhausen-mitte": 7,
    "kaltental": 8,
    "gaisburg": 9,
    "vaihingen-mitte": 10,
    "muehlhausen": 11,
    "neckarvorstadt": 12,
    "hauptbahnhof": 13,
    "plieningen": 14,
    "duerrlewang": 15,
}


def download():
    all_dates = {}
    with open("kurz_districts.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        with click.progressbar(list(reader), label="download icals") as bar:
            for row in bar:
                slug = row["slug"]
                r = httpx.get(
                    f"https://www.gelbersack-stuttgart.de/abfuhrplan/export/{slug}",
                    params={"type": 201},
                )
                data = r.text.split("\n")
                # needed for ical file to be rfc compliant
                data.insert(1, "PRODID:-//placeholder//text//EN")
                cal = Calendar("\n".join(data))
                all_dates[slug] = [str(event.begin.date()) for event in cal.timeline]
    return all_dates


def main():
    all_dates = download()

    # group all districts with the same dates
    lookup = {}
    groups = defaultdict(list)
    for k, v in all_dates.items():
        m = hashlib.sha256()
        m.update(str(v).encode())
        _key = m.hexdigest()
        lookup[_key] = v
        groups[_key].append(k)

    assert len(groups) == 15

    year = datetime.date.today().year
    with open(f"data/stuttgart_{year}.csv", "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=["district", "names", "dates"])
        writer.writeheader()
        for name, district_id in DISTRICT_MAP.items():
            for k, names in groups.items():
                if name in names:
                    break
            writer.writerow(
                {
                    "district": district_id,
                    "names": "|".join(names),
                    "dates": "|".join(lookup[k]),
                }
            )


if __name__ == "__main__":
    main()
