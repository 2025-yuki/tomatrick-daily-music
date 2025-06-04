# windsurf/scripts/generate_upload.py

import os
import json
import random
import tempfile
import time
import requests
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_fixed
from pick_keyword import generate_keyword
from dk_upload import upload

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def generate_and_upload_one(index: int):
    # 1. キーワード生成
    keyword = generate_keyword()

    # 2. ジャンル選択
    genre = random.choice([
        "Japanese Pop",
        "Japanese Hip-Hop",
        "Japanese Pop-Rock"
    ])

    # 3. プロンプトテンプレートを読み込み & レンダリング
    tpl = Template(open("windsurf/prompts/suno_prompt.j2", encoding="utf-8").read())
    prompt = tpl.render(genre=genre, keyword=keyword)

    # 4. Suno REST API を直接叩いて曲を生成
    url = "https://api.suno.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {os.getenv('SUNO_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "duration": 180  # 3分程度
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # 生成されたオーディオURL と 歌詞
    audio_url = data["audio_url"]
    lyrics = data.get("lyrics", "")

    # 5. ファイルとしてダウンロード
    audio_resp = requests.get(audio_url, timeout=120)
    audio_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with open(audio_path, "wb") as f:
        f.write(audio_resp.content)

    # 6. 曲タイトルを決定（index を付加して同名衝突を防ぐ）
    title = f"{keyword} - tomatrick #{index+1}"

    # 7. カバーアート一時ファイル（必要に応じてDALL·E等で生成）
    cover_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

    # 8. DistroKid へアップロード
    upload(audio_path, cover_path, title, "Pop")

def main():
    # 10回繰り返して一気に10曲を生成＆アップロード
    for i in range(10):
        try:
            print(f"=== Generating & uploading track {i+1}/10 ===")
            generate_and_upload_one(i)
            # Suno・DistroKid への連続リクエストで
            # 過度に短時間に叩かないように少しスリープ（オプション）
            time.sleep(5)
        except Exception as e:
            # 1曲だけ失敗しても残りは回し続ける
            print(f"Error on track {i+1}: {e}")
            continue

if __name__ == "__main__":
    main()
