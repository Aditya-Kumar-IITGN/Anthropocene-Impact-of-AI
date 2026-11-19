"""Step 1 of O2: build the site table and geocode it.

Run from presentation_slides/:  /Users/aryan/miniforge3/envs/geo/bin/python analysis/geocode_sites.py
Inputs:  data/raw/epoch/data_centers.csv, data/raw/epoch/data_center_timelines.csv
Outputs: data/processed/geocode_cache.csv (one row per query, reused on reruns)
         data/processed/sites.csv        (one row per data centre, with lat/lon and MW)

Geocoder: OpenStreetMap Nominatim, at most 1 request per second, per its usage policy.
"""
import os
import re
import time

import pandas as pd
from geopy.geocoders import Nominatim

RAW, OUT = "data/raw/epoch", "data/processed"
CACHE = f"{OUT}/geocode_cache.csv"

# Sites with no address in Epoch: place names taken from the sources Epoch cites for each site.
MANUAL = {
    "DayOne Nusajaya": "Iskandar Puteri, Johor, Malaysia",
    "Google Mesa": "Mesa, Arizona, USA",
    "Google Kansas City East": "Hunt Midwest Business Center, Kansas City, Missouri, USA",
    "Google Storey County": "McCarran, Storey County, Nevada, USA",
    "Oracle Batam": "Batam, Riau Islands, Indonesia",
    "Nebius Mantsala": "Mäntsälä, Finland",
    "Envision Galaxy Ulanqab": "Ulanqab, Inner Mongolia, China",
    "Southgate Melbourne": "Brooklyn, Victoria, Australia",
    "Anthropic Barber Lake": "Colorado City, Texas, USA",
    "Microsoft Narvik Norway": "Narvik, Norway",
    "OpenAI Stargate Michigan": "Saline Township, Washtenaw County, Michigan, USA",
    "OpenAI Stargate Milam": "Milam County, Texas, USA",
    "OpenAI Stargate New Mexico": "Santa Teresa, Doña Ana County, New Mexico, USA",
    "OpenAI Stargate Wisconsin": "Port Washington, Wisconsin, USA",
    # Epoch addresses that Nominatim cannot parse: town-level place instead
    "Amazon Madison Mega Site": "Canton, Madison County, Mississippi, USA",
    "Google Papillion": "Papillion, Sarpy County, Nebraska, USA",
    "Huawei Horinger": "Horinger County, Hohhot, Inner Mongolia, China",
    "Start Campus Sines Data Campus": "Sines, Setúbal, Portugal",
}


ISO2 = {"United States": "us", "China": "cn", "Malaysia": "my", "Norway": "no",
        "United Kingdom": "gb", "Indonesia": "id", "Finland": "fi", "Australia": "au",
        "Portugal": "pt", "Iceland": "is", "Sweden": "se", "United Arab Emirates": "ae"}
COUNTRY_WORDS = {"usa", "united states", "us", "china", "malaysia", "norway", "norge",
                 "united kingdom", "uk", "indonesia", "finland", "australia", "portugal",
                 "iceland", "sweden", "united arab emirates", "uae"}
US_STATES = {"AL": "Alabama", "AZ": "Arizona", "GA": "Georgia", "IA": "Iowa", "ID": "Idaho",
             "IN": "Indiana", "LA": "Louisiana", "MI": "Michigan", "MN": "Minnesota",
             "MO": "Missouri", "MS": "Mississippi", "NE": "Nebraska", "NM": "New Mexico",
             "NV": "Nevada", "NY": "New York", "ND": "North Dakota", "OH": "Ohio",
             "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "SC": "South Carolina",
             "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VA": "Virginia", "WA": "Washington",
             "WI": "Wisconsin", "WY": "Wyoming", "NC": "North Carolina", "KY": "Kentucky",
             "IL": "Illinois", "KS": "Kansas", "CO": "Colorado", "AR": "Arkansas", "NJ": "New Jersey"}


def fallbacks(address):
    """Full address first, then drop leading parts, but never below 'town, region'."""
    parts = [p.strip() for p in str(address).split(",") if p.strip()]
    while parts and parts[-1].lower() in COUNTRY_WORDS:        # the country is set by countrycodes
        parts = parts[:-1]
    n = len(parts)
    return [", ".join(parts[i:]) for i in range(max(n - 1, 1))]


def expected_state(address):
    """US state named in the address: an abbreviation next to a ZIP or at the end, or a full name."""
    text = str(address)
    m = re.search(r"\b([A-Z]{2})\s+\d{5}\b", text) or re.search(r",\s*([A-Z]{2})\s*(?:,\s*USA)?\s*$", text)
    if m and m.group(1) in US_STATES:
        return US_STATES[m.group(1)]
    for name in US_STATES.values():
        if name.lower() in text.lower():
            return name
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    sites = pd.read_csv(f"{RAW}/data_centers.csv")
    sites["current_mw"] = pd.to_numeric(sites["Current power (MW)"], errors="coerce")

    # Planned power: the largest power reached in the timeline by the end of 2030
    tl = pd.read_csv(f"{RAW}/data_center_timelines.csv", parse_dates=["Date"])
    tl["power_mw"] = pd.to_numeric(tl["Power (MW)"], errors="coerce")
    tl["it_mw"] = pd.to_numeric(tl["IT power (MW)"], errors="coerce")
    by2030 = tl[tl.Date <= "2030-12-31"].groupby("Data center")
    sites = sites.merge(by2030.power_mw.max().rename("planned_2030_mw"),
                        left_on="Name", right_index=True, how="left")
    sites = sites.merge(by2030.it_mw.max().rename("planned_2030_it_mw"),
                        left_on="Name", right_index=True, how="left")

    cache = pd.read_csv(CACHE) if os.path.exists(CACHE) else \
        pd.DataFrame(columns=["query", "lat", "lon", "display_name", "osm_type", "place_rank"])
    done = set(cache["query"])
    geo = Nominatim(user_agent="eh627-course-project (academic, non-commercial)", timeout=20)

    rows = []
    for _, s in sites.iterrows():
        address = MANUAL.get(s.Name, s.Address)
        source = "manual" if s.Name in MANUAL else "epoch"
        hit, level = None, None
        cc = ISO2[s.Country]
        for level, q in enumerate(fallbacks(address)):
            key = f"{q}|{cc}"
            if key not in done:
                time.sleep(1.1)
                r = geo.geocode(q, country_codes=cc)
                new = {"query": key, "lat": r.latitude if r else None, "lon": r.longitude if r else None,
                       "display_name": r.address if r else None,
                       "osm_type": r.raw.get("addresstype") if r else None,
                       "place_rank": r.raw.get("place_rank") if r else None}
                cache = pd.concat([cache, pd.DataFrame([new])], ignore_index=True)
                cache.to_csv(CACHE, index=False)
                done.add(key)
            c = cache[cache["query"] == key].iloc[0]
            if pd.notna(c.lat):
                hit = c
                break
        rows.append({
            "name": s.Name, "country": s.Country, "owner": s.Owner, "address_used": address,
            "address_source": source,
            "lat": hit.lat if hit is not None else None, "lon": hit.lon if hit is not None else None,
            "matched": hit.display_name if hit is not None else None,
            "match_type": hit.osm_type if hit is not None else None,
            "place_rank": hit.place_rank if hit is not None else None,   # 26+ ~ street, 16 ~ city
            "fallback_level": level if hit is not None else None,
            "expected_state": expected_state(address) if s.Country == "United States" else None,
            "current_mw": s.current_mw, "planned_2030_mw": s.planned_2030_mw,
            "planned_2030_it_mw": s.planned_2030_it_mw,
        })

    out = pd.DataFrame(rows)
    out["state_ok"] = [True if not isinstance(e, str) else (isinstance(m, str) and e in m)
                       for e, m in zip(out.expected_state, out.matched)]
    out.to_csv(f"{OUT}/sites.csv", index=False)
    print(f"{len(out)} sites, {out.lat.notna().sum()} geocoded, {out.lat.isna().sum()} failed")
    print(out.loc[out.lat.isna(), ["name", "address_used"]].to_string() if out.lat.isna().any() else "")
    bad = out[~out.state_ok]
    print(f"state mismatches: {len(bad)}")
    if len(bad):
        print(bad[["name", "address_used", "matched"]].to_string(max_colwidth=60))
    print("precision (place_rank):", out.place_rank.describe()[["min", "50%", "max"]].to_dict())


if __name__ == "__main__":
    main()
