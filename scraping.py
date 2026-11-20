from playwright.sync_api import sync_playwright

url = "https://github.com/orgs/google/repositories?q=sort%3Aname-asc&page=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)

    rows = page.locator("li[id*='list-view-node']")  # 全てのリポジトリ（1件が1行）
    rows.first.wait_for()  # 表示されるまで待つ
    repos = []

    for i in range(rows.count()):
        row = rows.nth(i)

        name = row.locator("h4").inner_text().strip()

        langs = row.locator("[class*='PrimaryLanguageName']")
        language = langs.nth(0).inner_text().strip() if langs.count() >= 1 else ""

        stars = row.locator("a[href$='/stargazers']").inner_text().strip()

        repos.append((name, language, stars))  # SQLiteに渡すのでtupleにする

    browser.close()

print("取得したリポジトリの数：", len(repos))
for repo in repos:
    print(repo)