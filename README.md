# Shakespeare-s-Globe-Web-Scraper-Documentation


<img width="945" height="390" alt="image" src="https://github.com/user-attachments/assets/0541927f-5a51-4b02-8745-49b510fa441b" />

## Project Overview

This project is a Python-based web scraper developed to extract structured theatre event data from the official website of [Shakespeare's Globe](https://www.shakespearesglobe.com?utm_source=chatgpt.com).

The scraper collects production and event information from the **What's On** section of the website and exports the cleaned results into standardized CSV datasets suitable for:

* Data analysis
* Event intelligence
* Theatre analytics
* Performance scheduling research
* Data engineering pipelines

The scraper was built using only:

* `requests`
* `BeautifulSoup`
* `pandas`

No Selenium or Playwright was used in the final implementation, following the project submission guidelines for lightweight and ethical scraping.

---

# Features

The scraper automatically extracts:

| Field                   | Description                        |
| ----------------------- | ---------------------------------- |
| `title`                 | Event or production title          |
| `description`           | Event description/meta description |
| `venue`                 | Performance venue                  |
| `capacity`              | Venue seating capacity             |
| `open_date`             | First performance date             |
| `close_date`            | Final performance date             |
| `performance_dates`     | All scheduled performance dates    |
| `performance_times`     | Performance start times            |
| `upcoming_dates`        | Upcoming scheduled dates           |
| `upcoming_performances` | Total upcoming performances        |
| `seat_price`            | Detected seated ticket pricing     |
| `stand_price`           | Standing ticket pricing            |
| `currency`              | Currency used for pricing          |
| `venue_url`             | Event page URL                     |
| `booking_url`           | Booking anchor link                |
| `scrape_datetime`       | Timestamp of scraping              |

---

# Technologies Used

## Python Libraries

* `requests`
* `beautifulsoup4`
* `pandas`
* `numpy`
* `re`
* `datetime`
* `urllib`
* `ast`

---

# Installation

## 1. Clone Repository

```bash
git clone <your-github-repo-url>
cd <repo-folder>
```

---

## 2. Install Dependencies

```bash
pip install requests beautifulsoup4 pandas numpy
```

---

# How the Scraper Works

## Step 1 — Collect Event URLs

The scraper visits:

```python
https://www.shakespearesglobe.com/whats-on/
```

It then extracts all valid production/event links from the page.

---

## Step 2 — Visit Each Event Page

For every event URL, the scraper extracts:

* Title
* Venue
* Dates
* Performance schedules
* Pricing information
* Booking links
* Descriptions

---

## Step 3 — Clean and Standardize Data

The cleaning pipeline includes:

* Removing duplicates
* Standardizing venue names
* Fixing encoding issues
* Cleaning price symbols
* Converting list columns into readable formats
* Filling missing values
* Standardizing capacity values

---

## Step 4 — Export Results

Two CSV files are generated:

### Raw Standardized Dataset

```bash
shakespeares_globe_standardized.csv
```

### Fully Cleaned Dataset

```bash
shakespeares_globe_cleaned.csv
```

---

# Running the Scraper

Run the Python script:

```bash
python scraper.py
```

The terminal will display progress logs such as:

```bash
SCRAPING 1/43
SCRAPING 2/43
SCRAPING 3/43
...
```

---

# Data Cleaning Pipeline

The project includes a secondary cleaning phase that performs:

## Column Standardization

* Lowercase conversion
* Space replacement with underscores

Example:

```python
performance dates → performance_dates
```

---

## Venue Capacity Mapping

Known venue capacities are automatically assigned:

| Venue                   | Capacity |
| ----------------------- | -------- |
| Globe Theatre           | 1570     |
| Sam Wanamaker Playhouse | 340      |

---

## Encoding Corrections

Fixes malformed characters such as:

| Broken Encoding | Correct Character |
| --------------- | ----------------- |
| `Â£`            | `£`               |
| `â€™`           | `'`               |

---

## Duplicate Removal

Duplicate productions are automatically removed.

---

# Target Show Prioritization

The scraper prioritizes specific productions required for analysis:

* As You Like It
* Much Ado About Nothing
* Pinocchio
* A Midsummer Night's Dream
* Mother Courage and Her Children
* Love's Labour's Lost
* A World Elsewhere

These productions are surfaced first in the cleaned dataset.

---

# Output Example

| title                  | venue         | open_date    | close_date        | seat_price      |
| ---------------------- | ------------- | ------------ | ----------------- | --------------- |
| Much Ado About Nothing | Globe Theatre | 15 June 2026 | 20 September 2026 | £15.00 - £75.00 |

---

# Ethical Scraping Compliance

This scraper follows ethical scraping standards:

* Uses lightweight HTTP requests only
* Avoids excessive request rates
* Does not bypass authentication
* Does not scrape private user data
* Only accesses publicly available pages
* Avoids browser automation tools in the final solution

---

# Project Structure

```bash
project/
│
├── scraper.py
├── shakespeares_globe_standardized.csv
├── shakespeares_globe_cleaned.csv
├── README.md
└── requirements.txt
```


# Submission Notes

This project was completed as a structured web scraping exercise focused on:

* Data extraction
* Data cleaning
* Dataset standardization
* Ethical scraping practices
* Reproducible data pipelines

