import json
import time

from pull_boxes import reQuester, URLs

boxes = {}

with open("public/boxes.json", "r") as boxes_local:
    boxes = json.load(boxes_local)

# fetch tags
print("[+] Downloading Tags")


def tag_fetcher(box_id):
    fetched_res = reQuester(url=URLs["tags"].format(box_id))
    tags = []
    if fetched_res.status_code == 200:
        for tag_obj in fetched_res.json()["info"]:
            tags = tags + [tag_obj["name"]]
        print("    [-] Adding", tags, "to", box_id)
        boxes[box_id]["tags"] = tags
    elif fetched_res.status_code == 401:
        print("    [*] Unauthorised. Check API key")
        exit(0)
    elif fetched_res.status_code == 404:
        print("    [-] Not Found {}".format(box_id))
    elif fetched_res.status_code == 400:
        print("    [-] VIP only {}".format(box_id))
    else:
        # 429 Too Many Requests, sleep for 50 sec
        print(
            "    [*] #{} sleeping for 50 sec code {}".format(
                box_id, fetched_res.status_code
            )
        )
        time.sleep(50)


bk = boxes.keys()
for box_id in bk:
    tags = []
    try:
        assert boxes[box_id]["tags"] != []
    except KeyError:
        tag_fetcher(box_id)
    except AssertionError:
        tag_fetcher(box_id)
with open("public/boxes.json", "w") as boxes_local:
    # save the boxes file
    json.dump(boxes, boxes_local, indent=4)
print("[+] Done!")
