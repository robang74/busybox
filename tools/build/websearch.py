import requests


def search_build_fix(error):

    query = f"{error} busybox build fix"

    url = "https://api.duckduckgo.com"

    r = requests.get(
        url,
        params={
            "q": query,
            "format": "json"
        }
    )

    data = r.json()

    return data.get("AbstractText", "")
