import os, time
from playwright.sync_api import sync_playwright

def upload(audio, cover, title, genre):
    # Playwrightを使用してDistroKidにログインし、アップロードを実行
    with sync_playwright() as p:
        # ヘッドレスモードでブラウザを起動
        b = p.chromium.launch(headless=True)
        page = b.new_page()
        
        # ログインページに移動
        page.goto("https://distrokid.com/login")
        
        # ログイン情報の入力と送信
        page.fill("#email", os.getenv("DK_EMAIL"))
        page.fill("#password", os.getenv("DK_PASSWORD"))
        page.click("button[type=submit]")
        
        # ダッシュボードページの読み込み待ち
        page.wait_for_url("**/dashboard*", timeout=30000)
        
        # アップロードページに移動
        page.goto("https://distrokid.com/newupload")
        
        # アップロード情報の入力
        page.set_input_files("input[type=file][name=artwork]", cover)
        page.fill("input[name='songTitle1']", title)
        page.select_option("select[name='primaryGenre']", label=genre)
        page.set_input_files("input[type=file][name='audioFile1']", audio)
        
        # 利用規約のチェックとアップロード実行
        page.check("#terms")
        page.click("button:has-text('Done')")
        
        # 処理完了待ち
        page.wait_for_selector("text=processing", timeout=120000)
        b.close()
