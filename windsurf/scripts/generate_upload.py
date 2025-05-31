# windsurf/scripts/generate_upload.py

import os
import json
import random
import tempfile
import requests
import openai
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_fixed
from pick_keyword import generate_keyword
from dk_upload import upload

# 環境変数から OpenAI API キーをセット
openai.api_key = os.getenv("OPENAI_API_KEY")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def main():
    # 1. キーワード生成
    keyword = generate_keyword()

    # 2. ジャンル選択
    genre = random.choice([
        "Japanese Pop",
        "Japanese Hip-Hop",
        "Japanese Pop-Rock"
    ])

    # 3. プロンプトテンプレートを読み込み & レンダリング
    tpl = Template(
        open("windsurf/prompts/suno_prompt.j2", encoding="utf-8").read()
    )
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

    # 5. ファイルとしてオーディオをダウンロード
    audio_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    audio_resp = requests.get(audio_url, timeout=120)
    audio_resp.raise_for_status()
    with open(audio_path, "wb") as f:
        f.write(audio_resp.content)

    # 6. 曲タイトルを決定
    title = f"{keyword} - tomatrick"

    # 7. カバーアート一時ファイル（DALL·E で生成）
    cover_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

    # 7a. DALL·E に投げて画像 URL を取得
    dalle_resp = openai.Image.create(
        prompt=f"Album cover art for a {genre} song titled '{title}', vibrant, modern style",
        n=1,
        size="512x512"
    )
    image_url = dalle_resp["data"][0]["url"]

    # 7b. 画像をダウンロードして保存
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    with open(cover_path, "wb") as f:
        f.write(img_resp.content)

    # 8. DistroKid へアップロード
    #    upload(<audio_file>, <cover_image>, <title>, <genre>)
    upload(audio_path, cover_path, title, genre)

if __name__ == "__main__":
    main()
