# Primela Rose VIP Landing Page (`primelarose.com`)

High-converting, mobile-first VIP bridge landing page designed to safely direct TikTok followers to your **Fanvue** subscription page to monetize 18+ uncensored spicy AI content without getting banned or shadowbanned on TikTok.

---

## 📁 Project Structure

```text
primelarose-vip/
├── index.html         # Complete, high-converting VIP landing page
├── _redirects         # Netlify vanity shortcuts (/vip, /secret, /fanvue)
├── netlify.toml       # Netlify caching and security headers
├── assets/
│   ├── avatar.jpg     # Primela Rose profile avatar
│   ├── teaser1.jpg    # Boudoir silk bedroom teaser
│   ├── teaser2.jpg    # Cyberpunk cosplay teaser
│   └── teaser3.jpg    # Sunset beach resort teaser
└── README.md          # Setup and deployment guide
```

---

## 🚀 How to Deploy to Netlify in 60 Seconds (Zero Code Required)

### Method 1: Netlify Drag-and-Drop (Easiest)
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop) and log into your Netlify account.
2. Drag and drop the **entire `primelarose-vip` folder** into the upload area on Netlify.
3. Your site will instantly go live with a temporary `https://<random-name>.netlify.app` URL!

---

## 🌐 Connecting Your Custom Domain (`primelarose.com`)

1. In your Netlify Site Dashboard, click **Site configuration** → **Domain management** → **Add a custom domain**.
2. Type in: `primelarose.com`.
3. In your domain registrar (where you registered `primelarose.com` as seen in your screenshot):
   - **Option A (Netlify DNS - Recommended):** Change the nameservers to the 4 Netlify nameservers provided by Netlify.
   - **Option B (Standard DNS Records):**
     - **A Record**: Point `@` (root domain) to Netlify's load balancer IP `75.2.60.5`.
     - **CNAME Record**: Point `www` to `<your-site-name>.netlify.app`.
4. Netlify will automatically provision a **free SSL/HTTPS certificate** within a few minutes.

---

## 🔗 Built-in Vanity Redirects (`_redirects`)

Your site includes pre-configured redirects:
- `primelarose.com/vip` → Directly redirects to your Fanvue profile
- `primelarose.com/fanvue` → Directly redirects to your Fanvue profile
- `primelarose.com/tiktok` → Redirects back to your TikTok profile

---

## ⚙️ Customization (Updating Your Fanvue Link & Pricing)

To change your Fanvue URL or monthly subscription price:
1. Open `index.html` in any text editor.
2. Search and replace `https://fanvue.com/primelarose` with your exact Fanvue profile link.
3. If you want to change the price from `$9.99/mo`, search `$9.99` in `index.html` and change it to your desired price.

---

## 📱 TikTok Bio & Funnel Optimization Tips

To maximize conversions from TikTok to Fanvue without risking account penalties:

1. **TikTok Bio Copy**:
   ```text
   AI Model & Cosplayer 🌸
   The spicy shoots & 1-on-1 private DMs too wild for TT 👇
   primelarose.com
   ```
2. **Never type the word "Fanvue", "OnlyFans", or explicit adult terms in TikTok captions or comments**.
3. **Always use verbal/text cues in your TikTok videos**:
   - *"Check my secret page in bio..."*
   - *"The full unfiltered set is on my website..."*
   - *"Link in bio to chat 1-on-1 with me..."*
