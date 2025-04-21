# 🌊 Surfbot – Slack Surf Forecast for Your Local Break

Surfbot pulls surf conditions from Surfline and posts only the best windows directly to your Slack channel. It filters based on swell quality, wind direction, and tide — so you only get pinged when it's worth it.

## 🔧 Features

- Forecasts next 6 days for your chosen break
- Posts only when surf is **Fair** or better (or long-period **Fair**)
- Labels wind: **Offshore**, **Onshore**, or **Cross-shore**
- Shows tide trend + flags **ideal low-rising tide**
- 🔥 Emoji for the **perfect combo** (offshore + low rising tide + good swell)
- Automatically posts to Slack (only when it’s worth it)

---

## 🚀 Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/surfbot.git
cd surfbot
```

### 2. Install Dependencies
```bash
pip install requests pytz python-dotenv
```

### 3. Configure the `.env` File

Create a `.env` file or copy the template:
```bash
cp .env.example .env
```

Edit `.env` to set up your spot and Slack webhook:
```env
# Surfline Info
SPOT_ID=5842041f4e65fad6a7708b03
SPOT_NAME=Navarre Beach
LOCAL_TZ=US/Central

# Slack Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_CHANNEL=#surf-reports
SLACK_USERNAME=surfbot
```

---

## 🌐 How to Find Your Surfline Spot ID

1. Go to [Surfline.com](https://www.surfline.com)
2. Search for your surf break (e.g., Navarre Beach)
3. Grab the ID from the URL:
   ```
   https://www.surfline.com/surf-report/navarre-beach/5842041f4e65fad6a7708b03
   ```

---

## 💬 How to Create a Slack Webhook

1. Go to [Slack Incoming Webhooks](https://my.slack.com/services/new/incoming-webhook/)
2. Choose a channel (e.g. `#surf-reports`)
3. Click **Add Incoming Webhooks Integration**
4. Copy the generated webhook URL and add it to `.env`

---

## 🕒 Automate It with Cron

To check each morning and post to Slack:

```bash
crontab -e
```

Add:
```
0 6 * * * /usr/bin/python3 /path/to/surfbot.py
```

---

## 🌬️ Customizing Wind Labels for Your Break

The wind labels (offshore/onshore/cross-shore) are currently calibrated for **Navarre Beach, Florida**, which faces **south**.

If your break faces a different direction (like Pipeline — northwest), update this function in `surfbot.py`:

```python
def get_wind_label(degrees):
    if 120 <= degrees <= 240:  # Pipeline: offshore from S
        return "✅ Offshore winds — clean conditions"
    elif 300 <= degrees or degrees <= 60:
        return "⚠️ Onshore winds — likely choppy"
    elif (75 <= degrees <= 105) or (255 <= degrees <= 285):
        return "↔️ Cross-shore winds — moderate drift"
    return ""
```

---

## ✅ Example Slack Message

```
🔥 Tue Apr 23, 06:00 AM to 09:00 AM — Fair to Good (Rating: 3.1)
  🌊 2.5–3.5 ft waves
  🌬️ Wind: 4.3 kts @ 335° ↖️ NW ✅ Offshore winds — clean conditions
  📈 Swell: 7.5 s period
  🌊 Tide: Rising (0.3ft → 1.0ft) ✅ Ideal: Low tide rising
```

---

PRs welcome. Paddle in. 🌊
