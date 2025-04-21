# 🌊 Surfbot – Surf Forecasts Posted to Slack

> _“I don’t know about you, but I hate checking Surfline every day just to see if there’s something on the horizon.  
> I’d rather get a notification only when it’s worth paddling out, customized to the kind of surf I actually want. ”_  
> — You, probably 🤙

Surfbot checks Surfline for you and posts only the good surf windows to your Slack channel. You don’t need to know how to code — just follow the steps below and you’ll be up and riding in no time. 🏄

---

## 🛠️ What You’ll Need
- A Linux computer with **Python** installed
- A **Slack workspace** (free account is fine)
- A **Surfline spot** (your local break)

---

## 👣 Step-by-Step Setup

### 1. Download the Files

Download these two files and put them in a folder:
- [surfbot script](surfbot.py)
- [`.env` config file](.env)

(You’ll get the actual download links from the repo.)

---

### 2. Install Python Packages

Type this into your terminal:

```bash
pip install requests pytz python-dotenv
```

This installs everything Surfbot needs.

---

### 3. Get Your Surfline Spot ID

1. Go to [surfline.com](https://surfline.com)
2. Search for your beach
3. Click on the surf report
4. Look at the link — it’ll look like:

```
https://www.surfline.com/surf-report/navarre-beach/5842041f4e65fad6a7708b03
```

Copy that long ID at the end:
```
5842041f4e65fad6a7708b03
```

---

### 4. Set Up the `.env` File

Open the `.env` file in a text editor and paste in your info:

```env
SPOT_ID=5842041f4e65fad6a7708b03   # 👈 replace with your ID
SPOT_NAME=Navarre Beach            # 👈 just a label for Slack
LOCAL_TZ=US/Central                # 👈 your timezone (Google: “pytz timezones”)

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...  # 👈 next step
SLACK_CHANNEL=#surf-reports
SLACK_USERNAME=surfbot
```

---

### 5. Create a Slack Webhook

1. Go to: [Slack Incoming Webhooks](https://my.slack.com/services/new/incoming-webhook/)
2. Choose a channel like `#surf-reports`
3. Click “Add Incoming Webhook”
4. Copy the webhook URL it gives you
5. Paste that into your `.env` file where it says `SLACK_WEBHOOK_URL=`

---

### 6. Run Surfbot!

Now in your terminal, type:

```bash
python3 surfbot.py
```

If there’s good surf coming, you’ll see a message in Slack like:

```
🔥 Tue Apr 23, 06:00 AM to 09:00 AM — Fair to Good
  🌊 2.5–3.5 ft waves
  🌬️ Wind: 4.3 kts @ NW ✅ Offshore
  📈 Swell: 7.5 s
  🌊 Tide: Rising (0.3ft → 1.0ft) ✅ Ideal
```

If there’s nothing worth surfing? Surfbot stays quiet. 🤫

---

### 7. Automate It (Optional)

Want Surfbot to check for you every morning?

In terminal, type:

```bash
crontab -e
```

Then add this line to check at 6 AM:

```
0 6 * * * /usr/bin/python3 /path/to/surfbot.py
```

(Change the path to where you saved the script.)

---

## 🌬️ Customizing Wind Logic

Surfbot is tuned for **Navarre Beach, Florida**, which faces **south**. If your break faces a different direction, use this guide to update the `get_wind_label()` function in `surfbot.py`.

### 📌 Use the table below to calibrate your offshore, onshore, and cross-shore logic:

| Surf Break              | Facing Dir | ✅ Offshore Winds      | ⚠️ Onshore Winds       | ↔️ Cross-Shore Winds    |
|-------------------------|------------|------------------------|------------------------|--------------------------|
| Navarre Beach, FL       | South      | N (0°)                 | S (180°)               | E/W (90° / 270°)          |
| Pipeline, HI            | Northwest  | SE (135°)              | NW (315°)              | NE/SW (45° / 225°)        |
| Ocean Beach, CA         | West       | E (90°)                | W (270°)               | N/S (0° / 180°)           |
| Trestles, CA            | South/SW   | NE (45°–90°)           | SW (210°–240°)         | NW/SE (135° / 315°)       |
| Sebastian Inlet, FL     | East       | W (270°)               | E (90°)                | N/S (0° / 180°)           |

### ✏️ Example Code Adjustment

If your break faces **west** like Ocean Beach, update your wind logic like this:

```python
def get_wind_label(degrees):
    if 60 <= degrees <= 120:      # Offshore from east
        return "✅ Offshore"
    elif 240 <= degrees <= 300:   # Onshore from west
        return "⚠️ Onshore"
    elif (0 <= degrees <= 30) or (150 <= degrees <= 210):
        return "↔️ Cross-shore"
    return ""
```

You can adjust these values based on maps, satellite views, or just standing on the sand and feeling where the wind comes from. 🌬️



---


## 🧼 Troubleshooting

- If you see `ModuleNotFoundError`, run:
  ```bash
  pip install requests pytz python-dotenv
  ```

- If Slack doesn’t post, double-check your webhook URL

- Still stuck? Open an issue on GitHub and I’ll help out 🤙

---

That’s it! You’re done. Now go surf 🏄
