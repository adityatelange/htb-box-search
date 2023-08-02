import json
import os
import requests


# from dotenv import load_dotenv

# load_dotenv()

key = os.environ.get("KEY")

URLs = {
    "retired": "https://www.hackthebox.com/api/v4/machine/list/retired/paginated",
    "tags": "https://www.hackthebox.com/api/v4/machine/tags/{}",
}


def reQuester(url, params={}):
    r = requests.get(
        url,
        headers={
            "authority": "www.hackthebox.com",
            "authorization": "Bearer {}".format(key),
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://app.hackthebox.com/",
            "origin": "https://app.hackthebox.com/",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
            "accept-language": "en-US,en;q=0.9",
        },
        params=params,
    )
    return r


if __name__ == "__main__":
    print("[+] Fetching retired boxes...")
    params = {"sort_type": "asc", "per_page": "100"}

    res = reQuester(URLs["retired"], params)

    if res.status_code == 401:
        print("[-] Unauthenticated.")
        exit(0)

    res = res.json()
    start_page = 1
    last_page = res["meta"]["last_page"]
    total = res["meta"]["total"]

    # store all boxes
    boxes = {}

    with open("public/boxes.json", "r") as boxes_local:
        boxes = json.load(boxes_local)

    # iterate over all pages to fetch all boxes
    for current_page in range(start_page, last_page + 1):
        params["page"] = current_page
        print("    [+] Fetching page {}/{}".format(current_page, last_page))

        page_res = reQuester(url=URLs["retired"], params=params)
        data = page_res.json()["data"]

        for box in data:
            box_id = str(box["id"])
            try:
                boxes[box_id]
            except KeyError:
                print("[+]        Adding : {}".format(box_id))
                boxes[box_id] = {
                    "name": box["name"],
                    "os": box["os"],
                    "difficultyText": box["difficultyText"],
                }

    # sort boxes ascending order by id https://stackoverflow.com/a/47017849/8291133
    boxes = dict(sorted(boxes.items(), key=lambda elem: int(elem[0])))

    print("[+] Boxes count matches with total? {}".format(len(boxes) == total))

    with open("public/boxes.json", "w") as boxes_local:
        json.dump(boxes, boxes_local, indent=4)
    print("[+] Done!")
