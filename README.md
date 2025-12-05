# inQRedible Website

Landing page for the inQRedible iOS app.

## 📁 Structure

```
website/
├── index.html          # Main landing page
├── privacy.html        # Privacy Policy (required by Apple)
├── terms.html          # Terms of Service
├── styles.css          # All styles
├── script.js           # JavaScript interactions
└── images/
    ├── app-store-badge.svg   # ✅ App Store download button
    ├── app-icon.png          # 🔲 NEEDED: App icon (256x256 or larger)
    ├── favicon.png           # 🔲 NEEDED: Favicon (32x32)
    ├── apple-touch-icon.png  # 🔲 NEEDED: iOS bookmark icon (180x180)
    ├── og-image.png          # 🔲 NEEDED: Social share image (1200x630)
    ├── screenshot-hero.png   # 🔲 NEEDED: Hero screenshot (iPhone mockup)
    ├── screenshot1.png       # 🔲 NEEDED: Content tab screenshot
    ├── screenshot2.png       # 🔲 NEEDED: Design tab screenshot
    ├── screenshot3.png       # 🔲 NEEDED: Logo tab screenshot
    ├── screenshot4.png       # 🔲 NEEDED: Export/result screenshot
    └── download-qr.png       # 🔲 NEEDED: QR code linking to App Store
```

## 📸 Required Images

### 1. App Icon
- File: `app-icon.png`
- Size: 256x256px or larger (square)
- Use the same icon as the app

### 2. Screenshots (4 needed)
- Files: `screenshot1.png` through `screenshot4.png`
- Size: iPhone screenshots (1179x2556 for iPhone 14 Pro)
- Suggested content:
  1. Content tab with URL input
  2. Design tab showing color/shape options
  3. Logo tab with logo placement
  4. Final QR code result

### 3. Hero Screenshot
- File: `screenshot-hero.png`
- Same as one of the above, or a special hero shot
- Will be displayed in the main hero section

### 4. Social/OG Image
- File: `og-image.png`
- Size: 1200x630px
- Used when sharing on social media
- Should show app name + screenshot or mockup

### 5. Download QR Code
- File: `download-qr.png`
- A QR code linking to your App Store page
- You can create this with inQRedible itself! 😉

## 🚀 Deployment to GitHub Pages

1. Create a new repository (e.g., `inqredibleapp.com`)
2. Push this `website` folder contents to the repo
3. Go to Settings → Pages
4. Select "Deploy from a branch" → main → / (root)
5. Add custom domain: `inqredibleapp.com`
6. In your domain registrar, add DNS records:
   - Type: CNAME
   - Name: www (or @)
   - Value: yourusername.github.io

## 🎨 Customization

The color scheme uses CSS variables in `styles.css`:

```css
:root {
    --color-primary: #FF6B9D;      /* Pink */
    --color-secondary: #9C27B0;    /* Purple */
    --gradient-primary: linear-gradient(135deg, #FF6B9D 0%, #C850C0 50%, #9C27B0 100%);
}
```

## ✅ Before Launch Checklist

- [ ] Add all required images
- [ ] Update App Store link in `index.html` (search for "apps.apple.com")
- [ ] Update support email if different from `support@inqredibleapp.com`
- [ ] Test on mobile devices
- [ ] Test all links
- [ ] Verify Privacy Policy is accurate
- [ ] Create download QR code with your actual App Store link
