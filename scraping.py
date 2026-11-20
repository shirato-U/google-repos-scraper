import sqlite3
import time
from playwright.sync_api import sync_playwright

base_url = "https://github.com/orgs/google/repositories?q=sort%3Aname-asc&page="
DB_FILE = "google_repos.db"
START_PAGE = 1  # 途中から再開するときは、ここを変える
END_PAGE = 99

# SQLiteの準備（実習3と同じ形）
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        language TEXT,
        stars TEXT
    );
""")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for n in range(START_PAGE, END_PAGE + 1):
        rows = page.locator("li[id*='list-view-node']")  # 全てのリポジトリ（1件が1行）

        # 表示されなかったら、待ってからやり直す
        for attempt in range(10):
            page.goto(base_url + str(n))
            try:
                rows.first.wait_for(timeout=10000)
                break
            except Exception:
                print(f"{n}ページ目：表示されません。60秒待ってやり直します")
                time.sleep(60)
        else:
            print(f"{n}ページ目を取得できなかったので中断します")
            break

        repos = []
        for i in range(rows.count()):
            row = rows.nth(i)

            name = row.locator("h4").inner_text().strip()

            langs = row.locator("[class*='PrimaryLanguageName']")
            language = langs.nth(0).inner_text().strip() if langs.count() >= 1 else ""

            stars = row.locator("a[href$='/stargazers']").inner_text().strip()

            repos.append((name, language, stars))  # SQLiteに渡すのでtupleにする

        # このページ分をすぐ保存する（名前が重複したものは無視される）
        cur.executemany(
            "INSERT OR IGNORE INTO repositories (name, language, stars) VALUES (?,?,?);",
            repos,
        )
        conn.commit()

        print(f"{n}ページ目：{len(repos)}件を保存しました")
        time.sleep(1)
        if n % 10 == 0:
            time.sleep(30)   # 相手のサーバーに負荷をかけないため

    browser.close()

count = cur.execute("SELECT count(*) FROM repositories").fetchone()[0]
print("保存された件数：", count)

conn.close()