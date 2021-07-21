# meinsack-datasette - gelber Sack API

![Run Sanity Tests](https://github.com/mfa/meinsack-datasette/workflows/Run%20Sanity%20Tests/badge.svg)


## about

- Version 1 was using Django/DjangoRestFramework + postgresql: https://github.com/opendata-stuttgart/meinsack
- This version is using [Datasette](https://github.com/simonw/datasette) and Sqlite.


### Why the change to Datasette?

- Django/DRF+Postgres was oversized for a readonly rest-api with ical export
- the maintenance started to become a hastle
- cheaper hosting


## development

```
datasette serve meinsack.db --metadata metadata.yml --plugins-dir plugins --template-dir templates
```

open in browser: http://localhost:8001/

run tests:
```
python -m pytest
```


## deployment on GCR

```
datasette publish cloudrun meinsack.db --service=meinsack -m metadata.yml --plugins-dir plugins --install datasette-ics --template-dir templates
```

(not used anymore - too much cost for egress traffic)


## deployment on fly.io

```
datasette publish fly meinsack.db --app meinsack -m metadata.yml --plugins-dir plugins --install datasette-ics --template-dir templates
```

deployed as: https://meinsack.click


## bootstrap

- tables are imported from Django project using [db-to-sqlite\[postgresql\]](https://github.com/simonw/db-to-sqlite)
- all tables starting with "main_" were used and renamed (prefix removed)
- database view added with:
```sql
create view pickupdate_street as select s.name as street, z.zipcode as zipcode, pickupdate.date as start,
date(pickupdate.date, "+1 day") as end, d.name as district, "Gelber Sack Abholtermin" as summary
from pickupdate join area as a on pickupdate.area_id=a.id join zipcode as z on s.zipcode_id=z.id
join street as s on a.id=s.schaalundmueller_district_id join district as d on s.district_id=d.id;
```


## import new year

- get pdf from schaal+mueller
- copy into txt file (see previous years in `data`)
- run import command, i.e. ``python import_data.py --filename data/stuttgart_2021.txt --year 2021``
