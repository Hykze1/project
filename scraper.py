import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin
from datetime import datetime
import numpy as np
import ast

BASE_URL = "https://www.shakespearesglobe.com"
START_URL = "https://www.shakespearesglobe.com/whats-on/"

headers = {
    "User-Agent": "Mozilla/5.0"
}


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_capacity(venue):

    venue = str(venue).upper()

    capacity_map = {
        "GLOBE THEATRE": 1570,
        "SAM WANAMAKER PLAYHOUSE": 340
    }

    for key, value in capacity_map.items():
        if key in venue:
            return value

    return "N/A"

# =========================
# GET ALL EVENT LINKS
# =========================
response = requests.get(START_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

event_links = set()

for a in soup.find_all("a", href=True):

    href = a["href"]

    if "/whats-on/" in href:

        full_url = urljoin(BASE_URL, href)

        if "#" in full_url:
            full_url = full_url.split("#")[0]

        if full_url.rstrip("/") == START_URL.rstrip("/"):
            continue

        if full_url.count("/") >= 4:
            event_links.add(full_url)

event_links = sorted(list(event_links))

print(f"\nFOUND {len(event_links)} EVENT URLS\n")


# =========================
# SCRAPE EACH EVENT
# =========================
all_data = []

for idx, url in enumerate(event_links, start=1):

    print("=" * 50)
    print(f"SCRAPING {idx}/{len(event_links)}")
    print(url)

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        # -------------------------
        # TITLE
        # -------------------------
        title = ""

        h1 = soup.find("h1")

        if h1:
            title = clean_text(h1.get_text())

        # -------------------------
        # VENUE
        # -------------------------
        venue = ""

        venue_el = soup.find(
            class_=re.compile("venue", re.I)
        )

        if venue_el:
            venue = clean_text(venue_el.get_text())

        # -------------------------
        # CAPACITY
        # -------------------------
        capacity = extract_capacity(venue)

        # -------------------------
        # DESCRIPTION
        # -------------------------
        description = ""

        desc = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if desc:
            description = clean_text(
                desc.get("content")
            )

        # -------------------------
        # BOOKING URL
        # -------------------------
        booking_url = url + "#book"

        # -------------------------
        # DATES + TIMES
        # -------------------------
        performance_dates = []
        performance_times = []

        listings = soup.find_all(
            "div",
            class_="c-event-listing"
        )

        for listing in listings:

            # DATE
            date_el = listing.find(
                "span",
                class_="c-event-listing__date"
            )

            date = clean_text(
                date_el.get_text()
            ) if date_el else ""

            # TIME LINKS
            buttons = listing.find_all("a")

            for a in buttons:

                text = clean_text(
                    a.get_text()
                )

                if not text:
                    continue

                lower_text = text.lower()

                if "sold out" in lower_text:
                    continue

                # EXTRACT TIME
                time_match = re.search(
                    r'(\d{1,2}\.\d{2})\s*(AM|PM)',
                    text,
                    re.I
                )

                if time_match:

                    raw_time = time_match.group(1)
                    meridian = time_match.group(2).upper()

                    formatted_time = (
                        raw_time.replace(".", ":")
                        + f" {meridian}"
                    )

                    performance_dates.append(date)
                    performance_times.append(formatted_time)

        # -------------------------
        # OPEN + CLOSE DATE
        # -------------------------
        open_date = (
            performance_dates[0]
            if performance_dates
            else None
        )

        close_date = (
            performance_dates[-1]
            if performance_dates
            else None
        )

        # -------------------------
        # UPCOMING
        # -------------------------
        upcoming_dates = performance_dates

        # -------------------------
        # PRICES
        # -------------------------
        page_text = soup.get_text(
            " ",
            strip=True
        )

        seat_price = None
        stand_price = None
        currency = "GBP"

        # SEAT PRICE
        price_matches = re.findall(
            r'£\d+\.\d{2}\s*-\s*£\d+\.\d{2}',
            page_text
        )

        if price_matches:
            seat_price = price_matches[0]

        # STANDING PRICE
        standing_match = re.search(
            r'Standing:\s*([£\d\.,\s]+)',
            page_text,
            re.I
        )

        if standing_match:
            stand_price = clean_text(
                standing_match.group(1)
            )

        # -------------------------
        # SCRAPE DATETIME
        # -------------------------
        scrape_datetime = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # -------------------------
        # RECORD
        # -------------------------
        record = {
            "title": title,
            "venue_url": url,
            "venue": venue,
            "capacity": capacity,
            "performance_dates": performance_dates,
            "performance_times": performance_times,
            "upcoming_dates": upcoming_dates,
            "upcoming_performances": len(upcoming_dates),
            "seat_price": seat_price,
            "stand_price": stand_price,
            "currency": currency,
            "open_date": open_date,
            "close_date": close_date,
            "description": description,
            "booking_url": booking_url,
            "scrape_datetime": scrape_datetime
        }

        all_data.append(record)

    except Exception as e:

        print(f"ERROR scraping {url}")
        print(e)

# =====================================================
# DATAFRAME
# =====================================================

df = pd.DataFrame(all_data)

# Standardize column order
COLUMN_ORDER = [

    "title",
    "description",

    "venue",
    "capacity",

    "open_date",
    "close_date",

    "performance_dates",
    "performance_times",
    "upcoming_dates",
    "upcoming_performances",

    "seat_price",
    "stand_price",
    "currency",

    "venue_url",
    "booking_url",

    "scrape_datetime"
]

df = df[COLUMN_ORDER]

# =====================================================
# DISPLAY
# =====================================================

pd.set_option(
    "display.max_columns",
    None
)


print("\n================ FINAL DATAFRAME ================\n")

print(df.head())

# =====================================================
# EXPORT CSV
# =====================================================

df.to_csv(
    "shakespeares_globe_standardized.csv",
    index=False
)

print("\nCSV EXPORTED SUCCESSFULLY")

# ================= FILTER RESULTS =================
filtered_results = []

TARGET_SHOWS = [
    "as you like it",
    "much ado about nothing",
    "pinocchio",
    "a midsummer night's dream",
    "mother courage and her children",
    "love's labour's lost",
    "a world elsewhere"
]

for show in all_data:

    title = str(
        show.get("title", "")
    ).lower()

    if (
        any(t in title for t in TARGET_SHOWS)
        and "talk" not in title
        and "workshop" not in title
        and "course" not in title
        and "tour" not in title
        and "event" not in title.replace("-", " ")
    ):
        filtered_results.append(show)


# ================= DATAFRAME =================
df = pd.DataFrame(filtered_results)

print("\n================ FILTERED DATAFRAME ================\n")
print(df)


# =====================================================
#  DATA CLEANING
# =====================================================


df_1 = pd.read_csv("shakespeares_globe_standardized.csv")

# ================= DELETE SECOND ROW BY POSITION =================

df_1 = df_1.drop(df_1.index[0])

# Reset index
df_1 = df_1.reset_index(drop=True)

print("Second row removed successfully.")


# ================= CLEAN COLUMN NAMES =================
df_1.columns = (
    df_1.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# ================= STANDARDIZE VENUE CAPACITY =================
venue_capacity_map = {
    "Globe Theatre": 1570,
    "Sam Wanamaker Playhouse": 340
}

# Fill capacity based on venue
def fix_capacity(row):
    venue = str(row["venue"]).strip()

    if venue in venue_capacity_map:
        return venue_capacity_map[venue]

    return "N/A"

df_1["capacity"] = df_1.apply(fix_capacity, axis=1)

# ================= FILL BLANKS WITH N/A =================
df_1 = df_1.fillna("N/A")

# ================= FIX ENCODING ISSUES =================
def clean_text(text):
    if not isinstance(text, str):
        return text

    replacements = {
        "Â£": "£",
        "â€“": "£",
        "â€™": "£",
        "â€œ": '"',
        "â€": '"',
        "â€˜": "'"
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text

for col in df_1.columns:
    df_1[col] = df_1[col].apply(clean_text)

# ================= STANDARDIZE VENUE NAMES =================
venue_clean_map = {
    "At Home": "Online"
}

df_1["venue"] = df_1["venue"].replace(venue_clean_map)

# ================= CLEAN PRICE COLUMNS =================
price_columns = ["seat_price", "stand_price"]

for col in price_columns:
    if col in df_1.columns:
        df_1[col] = (
            df_1[col]
            .astype(str)
            .str.replace("Â£", "£", regex=False)
            .str.strip()
        )

# ================= CLEAN LIST COLUMNS =================
list_columns = [
    "performance_dates",
    "performance_times",
    "upcoming_dates"
]

def clean_list_column(value):
    if value == "N/A":
        return "N/A"

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):
            cleaned = [str(x).strip() for x in parsed]
            return " | ".join(cleaned)

        return value

    except:
        return value

for col in list_columns:
    if col in df_1.columns:
        df_1[col] = df_1[col].apply(clean_list_column)

# ================= REMOVE DUPLICATES =================
df_1 = df_1.drop_duplicates()

# ================= STANDARDIZE DATE FIELDS =================
date_columns = ["open_date", "close_date"]

for col in date_columns:
    if col in df_1.columns:
        df_1[col] = (
            df_1[col]
            .astype(str)
            .str.strip()
            .replace("", "N/A")
        )

# ================= STANDARDIZE TIMES =================
if "performance_times" in df_1.columns:
    df_1["performance_times"] = (
        df_1["performance_times"]
        .astype(str)
        .str.replace("11:59 PM", "N/A")
    )

# ================= REORDER COLUMNS =================
preferred_order = [
    "title",
    "description",
    "venue",
    "capacity",
    "open_date",
    "close_date",
    "performance_dates",
    "performance_times",
    "upcoming_dates",
    "upcoming_performances",
    "seat_price",
    "stand_price",
    "currency",
    "venue_url",
    "booking_url",
    "scrape_datetime"
]

existing_columns = [col for col in preferred_order if col in df_1.columns]

df_1 = df_1[existing_columns]


# ================= PRIORITIZE TARGET SHOWS =================

TARGET_SHOWS = [
    "as you like it",
    "much ado about nothing",
    "pinocchio",
    "a midsummer night's dream",
    "mother courage and her children",
    "love's labour's lost",
    "a world elsewhere"
]

# Helper lowercase column
df_1["title_lower"] = (
    df_1["title"]
    .astype(str)
    .str.lower()
)

# Priority shows
priority_df = df_1[
    df_1["title_lower"].apply(
        lambda x: any(
            t in x for t in TARGET_SHOWS
        )
    )
]

# Remaining shows
other_df = df_1[
    ~df_1.index.isin(priority_df.index)
]

# Combine together
df_1 = pd.concat(
    [priority_df, other_df],
    ignore_index=True
)

# Remove helper column
df_1 = df_1.drop(columns=["title_lower"])

print(df_1[["title"]].head(20))

# # ================= SAVE CLEANED CSV =================
output_file = "shakespeares_globe_cleaned.csv"

df_1.to_csv(output_file, index=False)

# print("\n================ CLEANED DATAFRAME ================\n")
print(df_1.head())

print(f"\nCleaned CSV saved as: {output_file}")

