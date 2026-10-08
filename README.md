# Telegram Group Moderator Bot (@platforminvest101bot)

A lightweight, zero-dependency 24/7 Telegram Group Moderator Bot running on **Vercel Serverless Webhook** (or background polling).

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/viebulusan/platform-moderator-bot)

---

## ✨ Features

1. **Auto-Removes Join & Leave Service Messages**:
   - Cleans up `"User joined the group"` notifications immediately.
   - Cleans up `"User left the group"` notifications immediately.

2. **Strict Anti-Link Protection (Admins Only)**:
   - Blocks all links sent by regular group members (URLs, `t.me` links, markdown hyperlinks, invite codes, etc.).
   - Monitors both **new messages** and **edited messages** (stops spammers who send innocent messages and edit them later).
   - Deletes links embedded in media captions (photos, videos, documents).
   - **Administrators and group owners can share links freely without restriction.**

3. **100% Free Serverless Hosting on Vercel**:
   - Zero maintenance, zero server management.
   - Responds to events in milliseconds via Telegram Webhooks.
   - Never goes to sleep.

---

## 🚀 1-Click Deploy to Vercel

### Step 1: Deploy to Vercel
Click the button below:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/viebulusan/platform-moderator-bot)

Or import manually:
1. Go to **[vercel.com/new](https://vercel.com/new)**.
2. Select your repository: **`viebulusan/platform-moderator-bot`**.
3. Click **Deploy**.

---

### Step 2: Activate Telegram Webhook
Once Vercel finishes deploying (takes ~20 seconds), you will get your app domain (e.g. `https://platform-moderator-bot-xxx.vercel.app`).

Simply open this link in your browser:
```text
https://<YOUR-VERCEL-DOMAIN>.vercel.app/?set_webhook=1
```

You will see:
```json
{
  "telegram_response": {
    "ok": true,
    "result": true,
    "description": "Webhook was set"
  },
  "message": "Telegram Webhook activated successfully!"
}
```

---

### Step 3: Add Bot to Your Telegram Group
1. Search for **`@platforminvest101bot`** in Telegram.
2. Add it to your group.
3. Promote it to **Administrator** with **Delete Messages** permission.
4. Done! The bot is live 24/7.
