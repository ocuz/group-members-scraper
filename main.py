import requests
import csv
import time
import sys
import os

GROUP_URL = "https://groups.roblox.com/v1/groups/{group_id}/users?limit=100&cursor={cursor}&sortOrder=Desc"
CSV_FILE = "members.csv"
CURSORS_FILE = "cursors.txt"

RATE_DELAY = 0

def clean_field(value):
    if isinstance(value, str):
        return value.replace(",", "\\u002c")
    return value

def fetch_page(group_id, cursor):
    url = GROUP_URL.format(group_id=group_id, cursor=cursor)

    while True:
        try:
            r = requests.get(url, timeout=30)

            if r.status_code == 200:
                return r.json()

            if r.status_code == 429:
                print("  rate limited, waiting 5s...")
                time.sleep(5)
                continue

            if r.status_code == 500:
                print("  server error (500), retrying in 1s...")
                time.sleep(1)
                continue

            print(f"  unexpected status {r.status_code}, retrying in 2s...")
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"  request failed ({e}), retrying in 2s...")
            time.sleep(2)

def write_row(writer, user, role):
    writer.writerow([
        user.get("userId", ""),
        clean_field(user.get("username", "")),
        clean_field(user.get("displayName", "")),
        user.get("hasVerifiedBadge", ""),
        role.get("id", ""),
        clean_field(role.get("name", "")),
        role.get("rank", ""),
    ])

def main():
    print("Roblox group member scraper\n")

    group_id = input("group id: ").strip()
    if not group_id.isdigit():
        print("that doesn't look like a valid group id")
        sys.exit(1)

    print("\nstart from:")
    print("  1  beginning")
    print("  2  custom cursor")
    mode = input("choice: ").strip()

    if mode == "1":
        cursor = ""
    elif mode == "2":
        cursor = input("cursor: ").strip()
    else:
        print("invalid choice")
        sys.exit(1)

    print()

    write_header = not os.path.isfile(CSV_FILE) or os.path.getsize(CSV_FILE) == 0
    csv_file = open(CSV_FILE, "a", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)

    if write_header:
        writer.writerow([
            "userId", "username", "displayName",
            "hasVerifiedBadge", "role.id", "role.name", "role.rank"
        ])
        csv_file.flush()

    cursors_file = open(CURSORS_FILE, "a", encoding="utf-8")

    page = 1
    total = 0

    try:
        while True:
            short_cursor = (cursor[:10] + "..") if len(cursor) > 10 else cursor or "(start)"

            data = fetch_page(group_id, cursor)
            members = data.get("data", [])

            for entry in members:
                user = entry.get("user", {})
                role = entry.get("role", {})

                write_row(writer, user, role)

                print(",".join([
                    str(user.get("userId", "")),
                    str(clean_field(user.get("username", ""))),
                    str(clean_field(user.get("displayName", ""))),
                    str(user.get("hasVerifiedBadge", "")),
                    str(role.get("id", "")),
                    str(clean_field(role.get("name", ""))),
                    str(role.get("rank", ""))
                ]))

            csv_file.flush()
            total += len(members)

            print(f"{len(members)} members written | (running total: {total}) | page: {page} | cursor: {short_cursor}")

            next_cursor = data.get("nextPageCursor")
            if not next_cursor:
                print(f"\ndone — {total} members scraped in total")
                break

            cursors_file.write(next_cursor + "\n")
            cursors_file.flush()
            cursor = next_cursor
            page += 1

            time.sleep(RATE_DELAY)

    except KeyboardInterrupt:
        print(f"\nstopped at page {page}, {total} members written so far")
    finally:
        csv_file.close()
        cursors_file.close()

if __name__ == "__main__":
    main()
