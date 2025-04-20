# 🌊 Surfbot – Slack Surf Forecast for Your Local Break

Surfbot pulls surf conditions from Surfline and posts only the best windows directly to your Slack channel. It filters based on swell quality, wind direction, and tide — so you only get pinged when it's worth it.

## 🔧 Features

- Forecasts next 6 days for your chosen break
- Posts only when surf is **Fair** or better (or long-period **Fair**)
- Labels wind: **Offshore**, **Onshore**, or **Cross-shore**
- Shows tide trend + flags **ideal low-rising tide**
- 🔥 Emoji for the **perfect combo** (offshore + low rising tide + good swell)
- Automatically posts to Slack

## 🚀 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/surfbot.git
cd surfbot
```

### 2. Install Dependencies
```bash
pip install requests pytz
```

## 🔗 Configure Your Spot and Slack Channel

Open `surfbot.py` and edit the following values near the top:

```python
SPOT_ID = "YOUR_SPOT_ID"  # Get this from Surfline
webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

## 🌐 How to Find Your Surfline Spot ID

1. Go to [Surfline.com](https://www.surfline.com)
2. Find your surf break (e.g., Navarre Beach)
3. Look at the URL:
   ```
   https://www.surfline.com/surf-report/navarre-beach/5842041f4e65fad6a7708b03
   ```
4. Copy the long alphanumeric ID at the end → that’s your `SPOT_ID`.

## 💬 How to Create a Slack Webhook

1. Go to [Slack Incoming Webhooks](https://my.slack.com/services/new/incoming-webhook/)
2. Choose the channel you want to post in (e.g., `#surf-reports`)
3. Click **Add Incoming Webhooks Integration**
4. Copy the generated webhook URL
5. Paste it into your script:
   ```python
   webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
   ```

## 🕒 Automate with Cron

To check every morning and post if conditions are good:

```bash
crontab -e
```

Add something like:
```
0 6 * * * /usr/bin/python3 /path/to/navarre.py
```

## 🌬️ Customizing Wind Labels for Your Break

Wind classifications like **offshore**, **onshore**, and **cross-shore** are currently calibrated for **Navarre Beach, Florida**, which faces **south**.

If you're using a different surf break (like **Pipeline**, which faces **north/northwest**), you should **adjust the wind direction logic** to match your beach orientation.

### 📍 Example: Pipeline (North/NW facing)

Update this section in `surfbot.py`:

```python
def get_wind_label(degrees):
    if degrees is None:
        return ""
    # Offshore for Pipeline = South winds
    if 120 <= degrees <= 240:
        return "✅ Offshore winds — clean conditions"
    elif 300 <= degrees or degrees <= 60:
        return "⚠️ Onshore winds — likely choppy"
    elif (75 <= degrees <= 105) or (255 <= degrees <= 285):
        return "↔️ Cross-shore winds — moderate drift"
    return ""
```

You’ll need to match:
- **Offshore winds** = coming from land (opposite of wave direction)
- **Onshore winds** = coming from ocean
- **Cross-shore** = parallel to shoreline

Use a map and a compass if needed — or just stand at the break and see which way the wind feels "clean."

## ✅ Example Output in Slack

```
🔥 Tue Apr 20, 06:00 AM to 09:00 AM — Fair to Good (Rating: 3.1)
  🌊 2.5–3.5 ft waves
  🌬️ Wind: 4.3 kts @ 335° ↖️ NW ✅ Offshore winds — clean conditions
  📈 Swell: 7.5 s period
  🌊 Tide: Rising (0.3ft → 1.0ft) ✅ Ideal: Low tide rising
```

Paddle in. 🌊
