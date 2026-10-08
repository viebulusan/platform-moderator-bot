# Telegram Group Moderator Bot (@platforminvest101bot)

A lightweight, zero-dependency 24/7 Telegram Group Moderator Bot written in Python 3.

---

## ✨ Features

1. **Auto-Removes Join & Leave Service Messages**:
   - Cleans up `"User joined the group"` notifications immediately.
   - Cleans up `"User left the group"` notifications immediately.
   - Welcomes the group when invited, then cleans up its welcome message after 30 seconds.

2. **Strict Anti-Link Protection (Admins Only)**:
   - Blocks all links sent by regular group members (URLs, `t.me` links, markdown hyperlinks, invite codes, etc.).
   - Monitors both **new messages** and **edited messages** (stops spammers who send innocent messages and edit them later).
   - Deletes links embedded in media captions (photos, videos, documents).
   - **Administrators and group owners can share links freely without restriction.**

3. **Zero External Dependencies**:
   - Runs on standard Python 3.8+ using built-in libraries.
   - Minimal resource footprint (< 20MB RAM).

4. **Multi-Platform Cloud Ready**:
   - Supports **Koyeb**, **Hugging Face Spaces**, **Vercel (Serverless Webhook)**, **Docker**, and **Linux Systemd**.

---

## 🚀 Telegram Setup Instructions

For the bot to work properly in your Telegram group:

1. Open Telegram and search for **`@platforminvest101bot`**.
2. **Add the bot to your group chat.**
3. Go to group settings ➔ **Administrators** ➔ **Add Administrator**.
4. Select **`@platforminvest101bot`** and give it the following permissions:
   - ✅ **Delete Messages** (Mandatory)
5. Save changes.

---

## 🌐 24/7 Cloud Deployment Options (Laptop Can Be Off)

### 🥇 Option 1: Koyeb (100% Free - Recommended)
Koyeb provides free continuous hosting with zero sleep for Docker/Python apps:
1. Go to **[app.koyeb.com](https://app.koyeb.com)** (sign in with GitHub).
2. Click **Create App** ➔ select **GitHub**.
3. Choose repository: **`viebulusan/platform-moderator-bot`**.
4. Select **Dockerfile** or Buildpack (Port: `8000`).
5. Click **Deploy**. Koyeb will run the bot 24/7 continuously!

---

### 🥈 Option 2: Hugging Face Spaces (100% Free - Never Sleeps)
Hugging Face offers 2 vCPUs & 16GB RAM free container hosting with no credit card required:
1. Go to **[huggingface.co/spaces](https://huggingface.co/spaces)** and click **Create new Space**.
2. Name your space (e.g. `platform-bot`).
3. Select **Docker** as Space SDK.
4. Clone the space repo or connect your GitHub repo `viebulusan/platform-moderator-bot`.
5. Hugging Face will build the Docker container and keep the bot running 24/7 forever.

---

### 🥉 Option 3: Vercel (Instant Serverless Webhook)
Vercel hosts serverless webhooks for free without server management:
1. Go to **[vercel.com](https://vercel.com)** and click **Add New...** ➔ **Project**.
2. Import **`viebulusan/platform-moderator-bot`**.
3. Click **Deploy**.
4. Once deployed, open your Vercel URL in your browser with `?set_webhook=1`:
   ```
   https://your-project.vercel.app?set_webhook=1
   ```
   This automatically activates the Telegram Webhook!

---

### 🖥️ Option 4: Local 24/7 Linux Background Service
The bot is also configured as a systemd service on this Linux machine:
```bash
systemctl --user status platform-moderator-bot.service
```
