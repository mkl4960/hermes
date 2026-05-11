---
name: web-element-extraction
description: "Extract specific element attributes (e.g., href) from a webpage, handling Cloudflare and JavaScript challenges via text-only proxies."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web, scraping, extraction, html, cloudflare]
    related_skills: [systematic-debugging, web-search]
---

# Web Element Extraction

## Overview

Extract attribute values (like `href`, `src`, `text`) from specific HTML elements identified by `id`, `class`, or other selectors. This skill addresses common obstacles such as Cloudflare anti‑bot pages, JavaScript‑rendered content, and sites that block automated fetchers.

## When to Use

- Need to retrieve a link, image URL, or text snippet from a known element on a page.
- The site returns a Cloudflare “Just a moment…” challenge or requires JavaScript to render the target.
- You want a reliable, repeatable method that works across sessions without launching a full browser.

## Core Technique: Text‑Only Proxy

Many sites (e.g., `clgnj.org`) serve a challenge page to bots but deliver the real HTML to text‑only fetch services. Using a proxy like `https://r.jina.ai/http://<site>` strips JavaScript and returns the raw HTML as readable text, which can then be searched with standard tools.

**Why it works:**  
Jina.ai’s reader fetches the page with a full browser, executes JavaScript, and returns the cleaned content. If the site still shows a challenge, the reader often bypasses it or provides the underlying HTML after the challenge resolves.

## Step‑by‑Step Procedure

1. **Identify the target URL** (e.g., `https://clgnj.org`).
2. **Fetch the page via a text‑only proxy**:
   ```bash
   curl -s "https://r.jina.ai/http://clgnj.org"
   ```
   Save the output to a temporary file if needed:
   ```bash
   curl -s "https://r.jina.ai/http://clgnj.org" > /tmp/page.txt
   ```
3. **Locate the element** using grep/sed or a lightweight HTML parser.
   - For an element with a known `id`:
     ```bash
     # Extract the whole line containing the id
     grep -i 'id="en-english-yt-link"' /tmp/page.txt
     ```
   - Then pull the attribute value (e.g., `href`):
     ```bash
     grep -i 'id="en-english-yt-link"' /tmp/page.txt | sed -n "s/.*href=\"\([^\"]*\)\".*/\1/p"
     ```
   - If the element is an `<a>` tag, you can also capture the link text similarly.
4. **Validate the result**:
   - Ensure the extracted URL matches expected pattern (e.g., starts with `https://youtube.com/live/`).
   - If empty, consider:
     - The site may still be serving a challenge; try a different proxy (e.g., `https://r.jina.ai/http://www.clgnj.org/`).
     - The element may be loaded via AJAX; inspect network tabs in a browser to find the XHR/JSON endpoint and repeat the proxy request on that endpoint.
5. **Optional: Use `web_extract` tool** (if available) with the proxied URL to get structured content, then search.

## Pitfalls & How to Avoid Them

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Cloudflare challenge still appears in proxied output | Output contains “Just a moment…” or challenge scripts | Wait a few seconds and retry; sometimes the proxy needs a fresh try. Try adding `?` query bypass: `https://r.jina.ai/http://clgnj.org/?nocache=1`. |
| Element rendered by JavaScript after initial HTML | Proxy returns HTML but the target element is missing | Identify the underlying API/XHR call (look for `fetch` or `XMLHttpRequest` in the proxied source) and request that URL directly via the proxy. |
| Multiple elements share same id (invalid HTML) | Extraction returns first match only | Verify uniqueness; if not unique, refine selector to include parent context (e.g., `div#section a#en-english-yt-link`). |
| Relative URLs in `href` | Extracted link like `/live/...` fails to resolve | Prepend the site’s origin: `https://clgnj.org` + relative path. |
| Extraction returns empty due to whitespace/newline issues | Sed/grep pattern fails | Use `grep -o` with Perl regex: `grep -oP '(?<=href=")[^"]*'` or switch to a lightweight parser like `pup` if available. |

## Verification

After extraction, optionally verify by fetching the target URL directly (if permissible) and checking HTTP status:
```bash
curl -I -s "https://youtube.com/live/m-nBdSz7qg0?feature=share" | head -1
```
Expect a `200 OK` or `302` redirect.

## Example: Extracting the English YouTube Live Link from CLGNJ

**Goal:** Get the `href` of `<a id="en-english-yt-link">` on `https://clgnj.org`.

```bash
# 1. Fetch via Jina.ai reader
curl -s "https://r.jina.ai/http://clgnj.org" > /tmp/clgnj.txt

# 2. Find the line with the id
grep -i 'id="en-english-yt-link"' /tmp/clgnj.txt
# → <a id="en-english-yt-link" href="https://youtube.com/live/m-nBdSz7qg0?feature=share"> ...

# 3. Extract the href value
href=$(grep -i 'id="en-english-yt-link"' /tmp/clgnj.txt | sed -n "s/.*href=\"\([^\"]*\)\".*/\1/p")
echo "$href"
# Output: https://youtube.com/live/m-nBdSz7qg0?feature=share
```

The extracted link matches the live stream for the English Sunday worship service.

## Automation within Hermes

You can encapsulate the above in a Hermes skill step using the `terminal` tool for `curl` and `grep`, or leverage the `web_extract` tool with the proxied URL when the site does not require JavaScript.

## References

- See `references/clgnj-example.md` for the exact command log and output from this session.
- For more on bypassing Cloudflare with text‑only proxies, consult the Jina.ai Reader documentation: https://r.jina.ai/

## Related Skills

- `systematic-debugging` – Use when the extraction fails unexpectedly; follow the four‑phase process to isolate whether the issue is the proxy, the selector, or the site’s anti‑bot measures.
- `web-search` – For locating alternative proxies or learning about site‑specific anti‑bot techniques.

---