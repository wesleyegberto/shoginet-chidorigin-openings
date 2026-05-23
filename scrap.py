import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://shogi-chess.net/senpouzukan/"
TACTICS_PREFIX = "tactics"
OUTPUT_DIR = "scraped_senpouzukan"
REQUEST_DELAY = 0.1       # seconds between requests

DOWNLOAD_IMAGES = False
DOWNLOAD_CSS = False
DOWNLOAD_JS = False
DOWNLOAD_IFRAMES = False
DOWNLOAD_KIFU = True
MAX_IFRAME_DEPTH = 2      # recursive depth limit

TRANSLATE = False
TRANSLATION_MODE = "none"  # "none", "deepl", "openai"

DEEPL_API_KEY = ""
OPENAI_API_KEY = ""

ENCODING = "shift_jis"

downloaded_pages = set()
downloaded_kif = set()

# ============================================================
# ROBOTS.TXT CHECK
# ============================================================

def check_robots_txt(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        r = requests.get(robots_url, timeout=10)
        if r.status_code != 200:
            print("[Warning] robots.txt not found. Proceeding.")
            return True

        rules = r.text.lower()
        if "disallow" in rules and "senpouzukan" in rules:
            print("❌ robots.txt may block scraping of this directory.")
            print(r.text)
            return False

        print("✅ robots.txt checked, apparently allowed.")
        return True

    except Exception as e:
        print(f"[Error] checking robots.txt: {e}")
        return False

# ============================================================
# TRANSLATION (Optional)
# ============================================================

def translate_text(text):
    if TRANSLATION_MODE == "none":
        return text

    if TRANSLATION_MODE == "deepl":
        url = "https://api-free.deepl.com/v2/translate"
        r = requests.post(url, data={
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": "PT"
        })
        return r.json()["translations"][0]["text"]

    if TRANSLATION_MODE == "openai":
        import openai
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Translate from Japanese to English keeping ▲/▽ notations intact."},
                {"role": "user", "content": text}
            ]
        )
        return response["choices"][0]["message"]["content"]

    return text


# ============================================================
# ASSET DOWNLOAD
# ============================================================

def fetch(url):
    """HTTP request returning content with original encoding preserved."""
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = resp.apparent_encoding
        print(f"   ✔ Resource downloaded: {url}")
        return resp
    except Exception as e:
        print(f"   ✖ Failed to download {url}: {e}")
        raise e


def download_file(url, dest_path):
    try:
        r = requests.get(url, timeout=10)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(r.content)
        print(f"   ✔ Resource downloaded: {url}")
    except Exception as e:
        print(f"   ✖ Failed to download {url}: {e}")


def download_assets(soup, base_url, page_dir, iframe_depth=0):
    assets = []

    # ==== IMAGES ==============================================================
    if DOWNLOAD_IMAGES:
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src: continue
            full_url = urljoin(base_url, src)
            filename = os.path.basename(full_url)
            dest = os.path.join(page_dir, "assets/img", filename)
            assets.append((full_url, dest))

    # ==== CSS ================================================================
    if DOWNLOAD_CSS:
        for css in soup.find_all("link", rel="stylesheet"):
            href = css.get("href")
            if not href: continue
            full_url = urljoin(base_url, href)
            filename = os.path.basename(full_url)
            dest = os.path.join(page_dir, "assets/css", filename)
            assets.append((full_url, dest))

    # ==== JS =================================================================
    if DOWNLOAD_JS:
        for js in soup.find_all("script", src=True):
            src = js["src"]
            full_url = urljoin(base_url, src)
            filename = os.path.basename(full_url)
            dest = os.path.join(page_dir, "assets/js", filename)
            assets.append((full_url, dest))

    # ==== IFRAMES ============================================================
    if (DOWNLOAD_IFRAMES or DOWNLOAD_KIFU) and iframe_depth < MAX_IFRAME_DEPTH:
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src")
            if not src: continue

            # Download raw iframe
            if DOWNLOAD_IFRAMES:
                full_url = urljoin(base_url, src)
                filename = os.path.basename(full_url)
                dest = os.path.join(page_dir, "assets/iframe", filename)

                assets.append((full_url, dest))

                # Recursively download iframe content
                try:
                    r = requests.get(full_url, timeout=10)
                    iframe_html = r.text
                    iframe_soup = BeautifulSoup(iframe_html, "html.parser")

                    # recursive call
                    download_assets(iframe_soup, full_url,
                                    os.path.join(page_dir, "assets/iframe"),
                                    iframe_depth + 1)

                except Exception as e:
                    print(f"   ✖ Error processing iframe {full_url}: {e}")

            if DOWNLOAD_KIFU and "kj.html?tactics" in src and src.endswith(".kif"):
                # Exemplo: kj.html?tactics104.kif
                try:
                    part = src.split("tactics")[1]
                    number = part.split(".kif")[0]
                    if number.isdigit():
                        kif_url = f"{BASE_URL}tactics{number}.kif"
                        kif_dest = os.path.join(page_dir, f"tactics{number}.kif")
                        assets.append((kif_url, kif_dest))
                except Exception:
                    pass

    # ==== Execute downloads ==================================================
    for url, dest in assets:
        download_file(url, dest)


# ============================================================
# COLLECT TACTICS LINKS
# ============================================================

def collect_tactics_links():
    print("🔎 Collecting links with prefix 'tactics'…")
    r = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(TACTICS_PREFIX):
            full_url = urljoin(BASE_URL, href)
            links.append(full_url)

    links = sorted(set(links))
    print(f"📌 {len(links)} pages found.")
    return links

# ============================================================
# PAGE SCRAPING
# ============================================================

def scrape_page(url):
    print(f"\n📄 Downloading page: {url}")

    r = requests.get(url, timeout=10)
    # r.encoding = r.apparent_encoding
    r.encoding = "shift_jis"
    soup = BeautifulSoup(r.text, "html.parser")

    # Download assets
    parsed = urlparse(url)
    name = os.path.basename(parsed.path).replace(".html", "").replace(".htm", "")
    page_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(page_dir, exist_ok=True)


    # Save files
    # with open(os.path.join(page_dir, "raw.html"), "w", encoding=ENCODING) as f:
    page_content = r.text.replace("charset=Shift_JIS", "charset=utf-8") \
        .replace("iframe src=\"", "iframe src=\"http://shogi-chess.net/senpouzukan/") \
        .replace("img src=\"", "img src=\"http://shogi-chess.net/senpouzukan/") \
        .replace("image: url('", "image: url('http://shogi-chess.net/senpouzukan/")

    with open(os.path.join(page_dir, "raw.html"), "w") as f:
        f.write(page_content)
    with open(os.path.join(page_dir, f"{name}.html"), "w") as f:
        f.write(page_content)

    download_assets(soup, url, page_dir)

    if TRANSLATE:
        # Extract plain text
        text = soup.get_text("\n")
        text = re.sub(r"\n{2,}", "\n", text).strip()

        translated = translate_text(text)

        with open(os.path.join(page_dir, "original.txt"), "w") as f:
            f.write(text)

        with open(os.path.join(page_dir, "traduzido.txt"), "w") as f:
            f.write(translated)

        md = f"# Page: {url}\n\n## Original\n```\n{text}\n```\n\n## Translation\n{translated}\n"
        with open(os.path.join(page_dir, "page.md"), "w") as f:
            f.write(md)

    print(f"✔ Page saved to {page_dir}")


# ============================================================
# GENERATE INDEX OF SCRAPED PAGES
# ============================================================

def generate_index_md():
    index_path = os.path.join(OUTPUT_DIR, "index.md")
    pages = []

    # iterate generated folders
    for name in sorted(os.listdir(OUTPUT_DIR)):
        page_dir = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(page_dir) and name != "assets":
            page_md = os.path.join(page_dir, "page.md")
            if os.path.exists(page_md):
                pages.append((name, page_md))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Index of scraped pages\n\n")
        f.write("Automatically generated list after scraping.\n\n")

        for name, path in pages:
            rel = os.path.relpath(path, OUTPUT_DIR)
            f.write(f"- [{name}]({rel})\n")

    print(f"📘 Index generated at: {index_path}")

def generate_index_html():
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    pages = []

    # iterate generated folders
    for name in sorted(os.listdir(OUTPUT_DIR)):
        page_dir = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(page_dir) and name != "assets":
            page = os.path.join(page_dir, f"{name}.html")
            if os.path.exists(page):
                pages.append((name, page))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("<h1>Index</h1>\n\n")
        f.write("<ul>")
        for name, path in pages:
            rel = os.path.relpath(path, OUTPUT_DIR)
            f.write(f"<a href=\"{rel}\">{name}</a>\n")
        f.write("</ul>")

    print(f"📘 Index generated at: {index_path}")

# ============================================================
# MAIN
# ============================================================

def main():
    if not check_robots_txt(BASE_URL):
        print("🚫 Scraping blocked by robots.txt.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # links = collect_tactics_links()

    # for url in links:
    #     scrape_page(url)
        # time.sleep(REQUEST_DELAY)

    # gerar índice após o scrape completo
    # generate_index_md()
    generate_index_html()

    print("\n🎉 Finished successfully!")

if __name__ == "__main__":
    main()
