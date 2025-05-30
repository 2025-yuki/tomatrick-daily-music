# windsurf/scripts/generate_upload.py

import os
import json
import random
import tempfile
import requests
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from pick_keyword import generate_keyword
from dk_upload import upload

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def generate_track():
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
    audio_resp.raise_for_status()
    audio_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with open(audio_path, "wb") as f:
        f.write(audio_resp.content)

    # 6. 曲タイトルを決定
    title = f"{keyword} - tomatrick"

    # 7. カバーアート一時ファイル（必要に応じてDALL·E等で生成）
    cover_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

    # 8. DistroKid へアップロード
    upload(audio_path, cover_path, title, "Pop")


def main():
    try:
        generate_track()
        print("✅ Track generation succeeded")
    except RetryError as re:
        print(f"⚠️ Suno.ai generation failed after retries: {re}")
    except requests.HTTPError as he:
        print(f"⚠️ HTTP error during generation: {he}")
    except Exception as e:
        print(f"⚠️ Unexpected error in generate_upload.py: {e}")


if __name__ == "__main__":
    main()
