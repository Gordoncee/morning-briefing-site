# Morning Briefing Analytics Worker

This Cloudflare Worker receives pageview events from `analytics.js`, stores them in D1, and exposes an authenticated stats API used by `admin.html`.

## Deploy

1. Install or run Wrangler:
   ```bash
   npm create cloudflare@latest
   ```

2. Create a D1 database:
   ```bash
   wrangler d1 create morning-briefing-analytics
   ```

3. Copy `wrangler.toml.example` to `wrangler.toml`, then replace `database_id`.

4. Apply the schema:
   ```bash
   wrangler d1 execute morning-briefing-analytics --file=./schema.sql
   ```

5. Set secrets:
   ```bash
   wrangler secret put ADMIN_TOKEN
   wrangler secret put IP_HASH_SALT
   ```

6. Deploy:
   ```bash
   wrangler deploy
   ```

7. Put the deployed Worker URL into `analytics-config.js`:
   ```js
   endpoint: "https://morning-briefing-analytics.<your-subdomain>.workers.dev"
   ```

8. Commit and push the updated `analytics-config.js` to GitHub Pages.

## Endpoints

- `POST /api/collect`: receives page events.
- `GET /api/stats?siteId=morning-briefing-site&days=30`: requires `Authorization: Bearer <ADMIN_TOKEN>`.
- `GET /health`: health check.
