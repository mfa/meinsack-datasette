from pathlib import Path

import httpx
import pytest
import yaml
from datasette.app import Datasette
from datasette.database import Database
from freezegun import freeze_time


@pytest.fixture
def app():
    _path = Path(__file__).parent.parent.absolute()
    _metadata = yaml.load((_path / "metadata.yml").open(), Loader=yaml.Loader)
    _datasette = Datasette(
        [_path / "meinsack.db"], plugins_dir=_path / "plugins", metadata=_metadata
    )
    yield _datasette.app()


@pytest.mark.asyncio
async def test_database_found(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/metadata.json")
        assert 200 == response.status_code
        assert "meinsack" in response.json()["databases"].keys()


@pytest.mark.asyncio
@freeze_time("2020-11-13")
async def test_json_redirect(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/v1/70180/Römerstraße/")
        assert 200 == response.status_code
        assert response.json().get("name") == "Römerstraße"
        _dates = response.json().get("dates")
        assert len([d for d in _dates if d.startswith("2020-")]) == 2


@pytest.mark.asyncio
async def test_ical_redirect(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/v1/70180/Römerstraße/ical/")
        assert 200 == response.status_code
        assert response.text.startswith(
            "BEGIN:VCALENDAR\r\nX-WR-CALNAME:Abholtermine ICAL"
        )


@pytest.mark.asyncio
async def test_zipcode_frontend_search(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/meinsack.json?_shape=array&sql=select+zipcode+from+zipcode+order+by+zipcode"
        )
        assert 200 == response.status_code
        assert len(response.json()) == 34
        assert response.text.startswith('[{"zipcode": "70173"}, {"zipcode": "70174"}, ')


@pytest.mark.asyncio
async def test_street_frontend_search(app):
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            'http://localhost/meinsack.json?_shape=array&sql=select+distinct+street+from+pickupdate_street+where+"zipcode"+%3D+%3Ap0+order+by+street&p0=70327'
        )
        assert 200 == response.status_code
        assert len(response.json()) == 185
        assert response.text.startswith('[{"street": "Abelsberg"}, ')
        assert "Ulmer Straße" in [i["street"] for i in response.json()]
