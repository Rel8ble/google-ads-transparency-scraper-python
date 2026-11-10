# Google Ads Transparency Center scraper for Python: competitor Google ads by domain, as JSON or CSV

Get every Google Search, YouTube, Shopping, Maps and Play ad a company runs, straight from the **Google Ads Transparency Center**, from Python or Node. Give it domains (`allbirds.com`), advertiser names (`Nike, Inc.`), advertiser IDs (`AR...`) or Transparency Center URLs; get one row per ad with format, first and last shown dates, days shown, the creative and a link to the ad.

This repo is a small tutorial and a runnable example around the Apify actor [rel8ble/google-ads-transparency-scraper](https://apify.com/rel8ble/google-ads-transparency-scraper).

> I built this actor; it's a paid tool on Apify ($0.045 per 1,000 ads, no start fee). Apify's free plan gives $5 of monthly credit, which covers about 110,000 ads.

## What you can do with it

- **Competitor ad research**: which creatives a rival keeps running longest (`daysShown` is a decent proxy for "this one works").
- **Agency prospecting**: check a list of prospect domains and keep the ones buying Google ads right now.
- **Creative swipe file**: image and video ads for a niche, with links back to the source.
- **Monitoring**: a daily run with `dateFrom` returns only what is new.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/google-ads-transparency-scraper").call(run_input={
    "queries": ["allbirds.com", "gymshark.com"],
    "region": "US",            # or "anywhere"
    "format": "all",           # "text", "image", "video"
    "maxAdsPerQuery": 100,     # 1 ad = 1 billed result
})

for ad in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(ad["advertiserName"], ad["format"], ad["firstShown"][:10], "->",
          ad["lastShown"][:10], f'{ad["daysShown"]}d', ad["adUrl"])
```

## Quick start (Node)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/google-ads-transparency-scraper').call({
    queries: ['Nike, Inc.'],
    format: 'video',
    platform: 'youtube',
    dateFrom: '2026-09-01',
    maxAdsPerQuery: 100,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.length, 'ads');
```

## The example script

`example.py` takes a list of domains, saves every ad to `google_ads.csv`, and prints per company: number of ads, how many were shown in the last N days, the format mix, and the longest-running ad. At the end it lists which companies are running Google ads right now.

```bash
pip install -r requirements.txt
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>
python example.py allbirds.com gymshark.com --region US --days 7
python example.py --file domains.txt --max-ads 50
python example.py --from-json sample.json      # offline, uses the real rows in this repo
```

Output on `sample.json` (3 real rows, `allbirds.com`, all regions, Apify cloud run on 10 Oct 2026):

```
3 ads -> google_ads.csv

query                         ads  live formats                    longest-running
allbirds.com                    3     3 text 2, video 1            534d text since 2025-03-12

Running Google ads in the last 7 days: 1 of 1 queries
   allbirds.com
```

## Input

| field | what it does |
|---|---|
| `queries` | Required. Domains, advertiser names, `AR...` advertiser IDs or Transparency Center URLs, one per item. |
| `region` | Two-letter country (`US`, `GB`, `DE` ...) or `anywhere` (default). |
| `format` | `all`, `text`, `image` or `video`. |
| `platform` | `all`, `search`, `youtube`, `shopping`, `maps` or `play`. |
| `dateFrom` / `dateTo` | `YYYY-MM-DD`; keep ads shown in that window. |
| `maxAdsPerQuery` | Ads saved per query, newest last-shown first. |
| `includeDetails` | One extra request per ad: every creative variant, countries with dates, topic, EU impression ranges. Same price. |
| `maxAdvertisersPerName` | For name queries: how many advertiser accounts with that name to include (default 1, the best match). |

Region, format, platform and dates are applied on Google's side, so you only pay for the rows you want.

## Output (one real row, trimmed)

```json
{
  "position": 1,
  "query": "allbirds.com",
  "queryType": "domain",
  "advertiserId": "AR01371945870127267841",
  "advertiserName": "Allbirds Inc",
  "creativeId": "CR02410131008503414785",
  "format": "text",
  "domain": "allbirds.com",
  "firstShown": "2026-04-07T15:44:46.000Z",
  "lastShown": "2026-10-10T16:50:18.000Z",
  "daysShown": 163,
  "imageUrl": "https://tpc.googlesyndication.com/archive/simgad/14549710068258611529",
  "regionFilter": "anywhere",
  "adUrl": "https://adstransparency.google.com/advertiser/AR01371945870127267841/creative/CR02410131008503414785?region=anywhere"
}
```

## Limits

- **No ad text field.** Google serves text ads to the Transparency Center as rendered images (`imageUrl`); video and shopping ads come as a preview script (`previewUrl`). There is no headline, description or landing-page field in Google's data.
- **No spend or clicks.** Google does not publish them for commercial ads. Impressions exist for EU countries only, as ranges (with `includeDetails`).
- **Names can be ambiguous.** Several advertiser accounts can share a name; use the domain or the `AR...` ID to be exact.
- Ads Google removed for policy reasons are not returned.

## Price

$0.045 per 1,000 ads, no start fee, Apify platform usage and proxies included. Queries with no ads and failed requests cost nothing. Details cost nothing extra. The prefilled input (allbirds.com, 20 ads) costs under a tenth of a cent.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/google-ads-transparency-scraper
- More scraping tutorials on dev.to: https://dev.to/rel8ble
- Other example repos: [alibaba-product-scraper-python](https://github.com/Rel8ble/alibaba-product-scraper-python), [website-tech-stack-detector-python](https://github.com/Rel8ble/website-tech-stack-detector-python), [website-contact-scraper-python](https://github.com/Rel8ble/website-contact-scraper-python)

Not affiliated with Google. Use the data in line with Google's terms and your local law.

Need a custom scraper or a ready dataset? Hire me on Fiverr: https://www.fiverr.com/rel8ble

## License

MIT
