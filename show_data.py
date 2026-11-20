import sqlite3

DB_FILE = "google_repos.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# 保存できたか確認する
count = cur.execute("SELECT count(*) FROM repositories").fetchone()[0]
print("保存された件数：", count)

print("\n----- 最初の10件 -----")

for row in cur.execute("SELECT name, language, stars FROM repositories LIMIT 10;"):
    print(row)

print("\n----- Pythonのリポジトリ（最初の5件） -----")

for row in cur.execute(
    "SELECT name, stars FROM repositories WHERE language = ? LIMIT 5;",
    ("Python",),
):
    print(row)

conn.close()