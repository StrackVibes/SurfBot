import requests
import time
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# === LOAD CONFIG FROM .env ===
load_dotenv()

SPOT_ID = os.getenv("SPOT_ID")
SPOT_NAME = os.getenv("SPOT_NAME", "Your Break")
LOCAL_TZ = pytz.timezone(os.getenv("LOCAL_TZ", "UTC"))
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")
SLACK_USERNAME = os.getenv("SLACK_USERNAME", "surfbot")

BASE_URL = "https://services.surfline.com/kbyg/spots/forecasts"
MIN_RATING = 2.5
DAYS = 6
INTERVAL = 1

params = {
    "spotId": SPOT_ID,
    "days": DAYS,
    "intervalHours": INTERVAL,
    "sds": "true",
    "resources": "all"
}
headers = {
    "User-Agent": "surfbot/1.0 (+https://github.com/surfbot)"
}

def post_to_slack(message):
    slack_data = {
        "channel": SLACK_CHANNEL,
        "username": SLACK_USERNAME,
        "icon_emoji": ":surfer:",
        "text": message
    }
    response = requests.post(WEBHOOK_URL, json=slack_data)
    if response.status_code != 200:
        print(f"[ERROR] Slack post failed: {response.status_code} - {response.text}")

def fetch_json(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(3):
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            try:
                return res.json()
            except requests.exceptions.JSONDecodeError:
                print(f"[ERROR] Invalid JSON from {endpoint}")
                print(res.text[:300])
                return None
        elif res.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"[WARN] Rate limited on {endpoint}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"[ERROR] Failed to fetch {endpoint}: {res.status_code}")
            print(res.text[:300])
            return None
    print(f"[FATAL] Too many 429s or other errors for {endpoint}")
    return None

def get_wind_label(degrees):
    if degrees is None:
        return ""
    if 300 <= degrees or degrees <= 60:
        return "✅ Offshore winds — clean conditions"
    elif 120 <= degrees <= 240:
        return "⚠️ Onshore winds — likely choppy"
    elif (75 <= degrees <= 105) or (255 <= degrees <= 285):
        return "↔️ Cross-shore winds — moderate drift"
    return ""

def get_cardinal_direction(source_deg):
    if source_deg is None:
        return "❓", "Unknown"
    to_deg = (source_deg + 180) % 360
    directions = [
        ("N", "⬆️", 0),
        ("NE", "↗️", 45),
        ("E", "➡️", 90),
        ("SE", "↘️", 135),
        ("S", "⬇️", 180),
        ("SW", "↙️", 225),
        ("W", "⬅️", 270),
        ("NW", "↖️", 315)
    ]
    for name, emoji, center in directions:
        if center - 22.5 <= to_deg < center + 22.5:
            return emoji, name
    return "⬆️", "N"

def get_tide_trend(start_ts, end_ts, tide_data):
    start_tide = next((t for t in reversed(tide_data) if t["timestamp"] <= start_ts), None)
    end_tide = next((t for t in reversed(tide_data) if t["timestamp"] <= end_ts), None)
    if not start_tide or not end_tide:
        return "🌊 Tide: Data unavailable", "Unknown", 0
    trend = "Rising" if end_tide["height"] > start_tide["height"] else "Falling"
    trend_str = f"🌊 Tide: {trend} ({start_tide['height']:.1f}ft → {end_tide['height']:.1f}ft)"
    if start_tide["height"] <= 0.5 and trend == "Rising":
        trend_str += " ✅ Ideal: Low tide rising"
    return trend_str, trend, start_tide["height"]

rating_res = fetch_json("rating")
wave_res = fetch_json("wave")
wind_res = fetch_json("wind")
tide_res = fetch_json("tides")

if not all([rating_res, wave_res, wind_res, tide_res]):
    print("[FATAL] Failed to load Surfline data. Exiting.")
    exit(1)

rating_data = rating_res["data"]["rating"]
wave_data = wave_res["data"]["wave"]
wind_data = wind_res["data"]["wind"]
tide_data = tide_res["data"]["tides"]

combined = []
for rating in rating_data:
    if rating["rating"]["value"] >= MIN_RATING:
        ts = rating["timestamp"]
        wave = next((w for w in wave_data if w["timestamp"] == ts), None)
        wind = next((w for w in wind_data if w["timestamp"] == ts), {}) 
        if wave:
            local_time = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
            swell = wave.get("swells", [{}])[0]
            combined.append({
                "timestamp": ts,
                "local_time": local_time,
                "rating_value": rating["rating"]["value"],
                "rating_key": rating["rating"]["key"],
                "wave_min": wave["surf"]["min"],
                "wave_max": wave["surf"]["max"],
                "period": swell.get("period"),
                "wind_speed": wind.get("speed"),
                "wind_direction": wind.get("direction")
            })

grouped = []
if combined:
    current_block = [combined[0]]
    for r in combined[1:]:
        prev = current_block[-1]
        same_rating = r["rating_key"] == prev["rating_key"]
        one_hour_apart = (r["local_time"] - prev["local_time"]) == timedelta(hours=1)
        if same_rating and one_hour_apart:
            current_block.append(r)
        else:
            grouped.append(current_block)
            current_block = [r]
    grouped.append(current_block)

worthy_blocks = []

print(f"\n🏄 Best Surf Times at {SPOT_NAME} (Next 6 Days)\n")
if not grouped:
    print("No FAIR or better conditions forecasted.")
else:
    for block in grouped:
        start = block[0]["local_time"]
        end = block[-1]["local_time"] + timedelta(hours=1)
        key = block[0]["rating_key"].replace("_", " ").title()
        raw_key = block[0]["rating_key"].upper()
        rating = block[0]["rating_value"]

        avg_min_wave = sum(b["wave_min"] for b in block) / len(block)
        avg_max_wave = sum(b["wave_max"] for b in block) / len(block)
        avg_periods = [b["period"] for b in block if b["period"] is not None]
        avg_wind_speeds = [b["wind_speed"] for b in block if b["wind_speed"] is not None]
        avg_wind_dirs = [b["wind_direction"] for b in block if b["wind_direction"] is not None]

        avg_period = sum(avg_periods) / len(avg_periods) if avg_periods else None
        avg_wind_speed = sum(avg_wind_speeds) / len(avg_wind_speeds) if avg_wind_speeds else None
        avg_wind_dir = sum(avg_wind_dirs) / len(avg_wind_dirs) if avg_wind_dirs else None

        tide_str, tide_trend, tide_start = get_tide_trend(block[0]['timestamp'], block[-1]['timestamp'], tide_data)
        tide_ideal = tide_trend == "Rising" and tide_start <= 0.5
        offshore = avg_wind_dir is not None and (avg_wind_dir <= 60 or avg_wind_dir >= 300)
        good_combo = (raw_key in ["FAIR_TO_GOOD", "GOOD", "GOOD_TO_EPIC", "EPIC"] and avg_period and avg_period >= 7)             or (raw_key == "FAIR" and avg_period and avg_period >= 11)

        is_perfect = offshore and tide_ideal and good_combo
        emoji = "🔥 " if is_perfect else ""

        summary = f"{emoji}{start.strftime('%a %b %d, %I:%M %p')} to {end.strftime('%I:%M %p')} — {key} (Rating: {rating:.1f})\n"
        summary += f"  🌊 {avg_min_wave:.1f}–{avg_max_wave:.1f} ft waves\n"

        if avg_wind_speed and avg_wind_dir is not None:
            wind_label = get_wind_label(avg_wind_dir)
            arrow, label = get_cardinal_direction(avg_wind_dir)
            summary += f"  🌬️ Wind: {avg_wind_speed:.1f} kts @ {avg_wind_dir:.0f}° {arrow} {label} {wind_label}\n"
        else:
            summary += "  🌬️ Wind: Data unavailable\n"

        if avg_period:
            summary += f"  📈 Swell: {avg_period:.1f} s period\n"
        else:
            summary += "  📈 Swell: Data unavailable\n"

        summary += f"  {tide_str}\n"

        print(summary)

        if good_combo:
            worthy_blocks.append(summary)

if worthy_blocks:
    message = "*🏄 Worthy Surf Blocks This Week:*\n" + "\n".join(worthy_blocks)
    post_to_slack(message)
