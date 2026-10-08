# Telegram Group Moderator Bot (@platforminvest101bot)

A lightweight, zero-dependency 24/7 Telegram Group Moderator Bot written in Python 3.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/viebulusan/platform-moderator-bot)

---

## ✨ Features

1. **Auto-Removes Join & Leave Service Messages**:
   - Cleans up `"User joined the group"` notifications immediately.
   - Cleans up `"User left the group"` notifications immediately.
   - Automatically welcomes the group when added and reminds admins to grant permissions, then cleans up its own welcome message after 30 seconds.

2. **Strict Anti-Link Protection (Admins Only)**:
   - Blocks all links sent by regular group members (URLs, `t.me` links, hidden markdown hyperlinks, invite codes, etc.).
   - Monitors both **new messages** and **edited messages** (stops spammers who send innocent messages and edit them later).
   - Deletes links embedded in media captions (photos, videos, documents).
   - **Administrators and group owners can share links freely without restriction.**

3. **Zero External Dependencies**:
   - Runs on standard Python 3.8+ using built-in libraries.
   - Minimal resource footprint (< 20MB RAM).

4. **Built-in Cloud Health Check & Auto Keepalive**:
   - Runs a lightweight HTTP server on port 10000 (or `$PORT`).
   - Automatically pings itself every 5 minutes on Render free-tier so it never goes to sleep.

---

## 🚀 Telegram Setup Instructions

For the bot to work properly in your Telegram group:

1. Open Telegram and search for **`@platforminvest101bot`**.
2. **Add the bot to your group chat.**
3. Go to group settings ➔ **Administrators** ➔ **Add Administrator**.
4. Select **`@platforminvest101bot`** and give it the following permissions:
   - ✅ **Delete Messages** (Mandatory)
5. Save changes.

> **Why must the bot be an Admin?**
> Telegram has Group Privacy Mode enabled by default. Bots cannot view messages sent by regular group members unless the bot is promoted to **Administrator**. Promoting the bot also grants it permission to delete join/leave notices and prohibited links.

---

## 🌐 Deploy to Render (24/7 Cloud - Run When Laptop is Off)

### Option 1: 1-Click Blueprint Deploy
Click this button:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/viebulusan/platform-moderator-bot)

### Option 2: Render Dashboard Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository: `viebulusan/platform-moderator-bot`.
4. Configure:
   - **Name:** `platform-moderator-bot`
   - **Language / Runtime:** `Python`
   - **Build Command:** `echo 'Ready'`
   - **Start Command:** `python3 bot.py`
   - **Instance Type:** `Free`
5. In Environment Variables:
   - `TELEGRAM_BOT_TOKEN`: `8840394969:AAFXsybR9ihgyRqBKe00r8eeILxl-G1mwc4`
   - `PORT`: `10000`
6. Click **Deploy Web Service**.

Render will automatically deploy and host the bot 24/7 in the cloud!
