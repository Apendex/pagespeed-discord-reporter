# PageSpeed Discord Reporter

An automated tool that fetches Google PageSpeed Insights data, generates a beautiful visual dashboard, and sends it to a Discord channel with clickable Lighthouse viewer links.

## 🚀 Features

- **Data Collection**: Fetches full Lighthouse metrics (Performance, Accessibility, Best Practices, SEO) for both Mobile and Desktop.
- **Visual Dashboard**: Generates a high-quality PNG scorecard using Matplotlib.
- **Deep Insights**: Automatically uploads reports to GitHub Gists so you can view the full diagnostic report in the official [Lighthouse Viewer](https://googlechrome.github.io/lighthouse/viewer/).
- **Discord Integration**: Delivers the results directly to your team's Discord via Webhooks.

## 🛠️ Setup

### 1. Prerequisites

- Python 3.8+
- A Google Cloud API Key (with PageSpeed Insights API enabled)
- A GitHub Personal Access Token (for Gist creation)
- A Discord Webhook URL

### 2. Installation

```powershell
# Clone the repository
git clone https://github.com/your-username/pagespeed-discord-reporter.git
cd pagespeed-discord-reporter

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy the `.env.example` file to a new file named `.env` and fill in your details:

```env
PAGESPEED_INSIGHTS_API_KEY=your_key_here
WEBSITE_URL=https://yourwebsite.com/
DISCORD_WEBHOOK_URL=your_webhook_url_here
GITHUB_TOKEN=your_github_token_here
```

## 📈 Usage

Run the scripts in order, or automate them with a task runner:

1. **Fetch Data**:
   ```powershell
   python main.py
   ```
2. **Generate Image**:
   ```powershell
   python generate_image.py
   ```
3. **Send to Discord**:
   ```powershell
   python discord.py
   ```

## 📦 Project Structure

- `main.py`: The engine that talks to Google and GitHub.
- `generate_image.py`: The "designer" that builds the visual scorecard.
- `discord.py`: The "messenger" that puts everything in your Discord channel.

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
