import json
from datasette import hookimpl
from datasette.utils.asgi import Response


def redirect_v1_api(request):
    zipcode = request.url_vars["zipcode"]
    street = request.url_vars["street"].replace("/", "")
    if request.url_vars.get("ical", "").startswith("ical"):
        view = f"pickupdate_street_ical.ics"
    else:
        view = f"pickupdate_street.v1_json"
    return Response.redirect(
        f"/meinsack/{view}?street={street}&zipcode={zipcode}", status=302
    )


@hookimpl
def register_routes():
    return [
        (r"^/v1/(?P<zipcode>\d+)/(?P<street>.+)/(?P<ical>.+)/?$", redirect_v1_api),
        (r"^/v1/(?P<zipcode>\d+)/(?P<street>.+)/?$", redirect_v1_api),
    ]


async def render_v1_json(datasette, columns, rows):
    if not rows:
        return Response.text("no element found", status=404)
    data = {"name": rows[0]["street"], "dates": []}
    for row in rows:
        data["dates"].append(row["start"])
    return Response.json(data)


def can_v1_json(columns):
    return {"zipcode", "street"}.issubset(columns)


@hookimpl
def register_output_renderer(datasette):
    return {
        "extension": "v1_json",
        "render": render_v1_json,
        "can_render": can_v1_json,
    }
