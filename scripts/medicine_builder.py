import requests
import json
import os

# Ensure output folder exists
os.makedirs("medicines", exist_ok=True)

# ---------- DATA FUNCTIONS ----------

def get_medicine_list():
    names = []
    skip = 0

    # Fetch first 200 medicines using pagination
    for i in range(4):
        url = f"https://api.fda.gov/drug/ndc.json?limit=50&skip={skip}"
        try:
            r = requests.get(url)
            data = r.json()

            for item in data.get("results", []):
                name = item.get("brand_name")
                if name:
                    names.append(name)

        except:
            pass

        skip += 50

    return list(set(names))


def get_rxnorm(name):
    try:
        url = "https://rxnav.nlm.nih.gov/REST/drugs.json?name=" + name
        r = requests.get(url)
        data = r.json()
        return data
    except:
        return None


def get_image(name):
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + name
        r = requests.get(url)
        d = r.json()
        return d.get("thumbnail", {}).get("source", "")
    except:
        return ""


# ---------- PAGE BUILDER ----------

def build_page(name):

    image = get_image(name)
    rxnorm_data = get_rxnorm(name)

    rx_info = "Standard information not available"
    if rxnorm_data:
        rx_info = "Data retrieved from RxNorm API"

    html = f"""
    <html>
    <head>
        <title>{name} - PharmaCoMED</title>
    </head>

    <body>

    <h1 align="center">{name}</h1>

    <p align="center">
    <img src="{image}" width="250">
    </p>

    <h3>Basic Information</h3>
    <p>{rx_info}</p>

    <h3>About This Medicine</h3>
    <p>
    This page contains automatically generated information about {name}.
    Detailed medical uses, side effects, overdose information and chemical
    details will be added in the next update cycle.
    </p>

    <p>
    Data Sources: openFDA, RxNorm, Wikimedia
    </p>

    <p>
    <a href="../index.html">Back to Search</a>
    </p>

    </body>
    </html>
    """

    filename = name.replace(" ", "_") + ".html"
    path = os.path.join("medicines", filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------- SEARCH INDEX ----------

def update_search(names):

    entries = []

    for n in names:
        page = n.replace(" ", "_") + ".html"
        entries.append({"name": n, "page": page})

    js = "var medicines = " + json.dumps(entries)

    with open("search_index.js", "w") as f:
        f.write(js)


# ---------- MAIN PROCESS ----------

print("Fetching medicine list...")

medicine_names = get_medicine_list()

print("Total medicines found:", len(medicine_names))

print("Building pages...")

for med in medicine_names:
    build_page(med)

print("Updating search index...")

update_search(medicine_names)

print("Process completed successfully")
