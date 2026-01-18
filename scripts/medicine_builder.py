import requests
import json
import os

# -------- FUNCTIONS ---------

def get_openfda_list():
    url = "https://api.fda.gov/drug/ndc.json?limit=50"
    response = requests.get(url)
    data = response.json()

    names = []

    for item in data["results"]:
        name = item.get("brand_name")
        if name:
            names.append(name)

    return list(set(names))


def get_image(name):
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + name
        r = requests.get(url)
        d = r.json()
        return d.get("thumbnail", {}).get("source", "")
    except:
        return ""


def build_page(name):

    image = get_image(name)

    html = f"""
    <html>
    <head><title>{name}</title></head>

    <body>
    <h1>{name}</h1>

    <img src="{image}" width="200">

    <p>Information for {name} collected from open APIs.</p>

    </body>
    </html>
    """

    path = "medicines/" + name.replace(" ", "_") + ".html"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def update_search(names):

    entries = []

    for n in names:
        page = n.replace(" ", "_") + ".html"
        entries.append({"name": n, "page": page})

    js = "var medicines = " + json.dumps(entries)

    with open("search_index.js", "w") as f:
        f.write(js)


# -------- MAIN PROCESS ---------

print("Fetching medicine list...")

medicine_names = get_openfda_list()

print("Building pages...")

for med in medicine_names:
    build_page(med)

print("Updating search index...")

update_search(medicine_names)

print("Done")
