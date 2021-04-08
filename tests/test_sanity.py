from pathlib import Path

import pytest
import yaml
from datasette.app import Datasette
from freezegun import freeze_time


@pytest.fixture
def instance():
    _path = Path(__file__).parent.parent.absolute()
    db_path = _path / "meinsack.db"
    _metadata = yaml.load((_path / "metadata.yml").open(), Loader=yaml.Loader)
    _datasette = Datasette(
        [db_path], plugins_dir=_path / "plugins", metadata=_metadata
    )
    yield _datasette


@pytest.mark.asyncio
async def test_database_found(instance):
    print(instance)
    response = await instance.client.get("/-/metadata.json")
    assert response.status_code == 200
    assert "meinsack" in response.json()["databases"].keys()


@pytest.mark.asyncio
@freeze_time("2020-11-13")
async def test_json_redirect(instance):
    response = await instance.client.get("/v1/70180/Römerstraße/")
    assert response.status_code == 200
    assert response.json().get("name") == "Römerstraße"
    _dates = response.json().get("dates")
    assert len([d for d in _dates if d.startswith("2020-")]) == 2
    assert len([d for d in _dates if d.startswith("2021-")]) == 18


@pytest.mark.asyncio
async def test_ical_redirect(instance):
    response = await instance.client.get("/v1/70180/Römerstraße/ical/")
    assert response.status_code == 200
    assert response.text.startswith(
        "BEGIN:VCALENDAR\r\nX-WR-CALNAME:Abholtermine ICAL"
    )


@pytest.mark.asyncio
async def test_zipcode_frontend_search(instance):
    response = await instance.client.get(
        "/meinsack.json?_shape=array&sql=select+zipcode+from+zipcode+order+by+zipcode"
    )
    assert response.status_code == 200
    assert len(response.json()) == 34
    assert response.text.startswith('[{"zipcode": "70173"}, {"zipcode": "70174"}, ')


@pytest.mark.asyncio
async def test_street_frontend_search(instance):
    response = await instance.client.get(
        '/meinsack.json?_shape=array&sql=select+distinct+street+from+pickupdate_street+where+"zipcode"+%3D+%3Ap0+order+by+street&p0=70327'
    )
    assert response.status_code == 200
    assert len(response.json()) == 185
    assert response.text.startswith('[{"street": "Abelsberg"}, ')
    assert "Ulmer Straße" in [i["street"] for i in response.json()]
