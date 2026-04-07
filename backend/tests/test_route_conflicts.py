from fastapi.routing import APIRoute
from main import app


def test_http_routes_do_not_conflict():
    seen = {}
    duplicates = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        methods = tuple(sorted(method for method in route.methods if method != "HEAD"))
        key = (route.path, methods)

        if key in seen:
            duplicates.append(
                {
                    "path": route.path,
                    "methods": methods,
                    "first": seen[key].name,
                    "second": route.name,
                }
            )
        else:
            seen[key] = route

    assert duplicates == []
