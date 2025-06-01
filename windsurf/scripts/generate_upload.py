# windsurf/scripts/generate_upload.py

import os
import random
import tempfile
import time
import requests
import openai
from jinja2 import Template
from pick_keyword import generate_keyword
from dk_upload import upload

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- 非同期ジョブでの生成関数 ---
def submit_suno_job(prompt: str, duration: int = 180) -> str:
    """
    Suno にジョブを登録し、job_id を返す
    """
    url = "https://api.suno.ai/v1/jobs"
    headers = {
        "Authorization": f"Bearer {os.getenv('SUNO_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "duration": duration}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["job_id"]  # 例: "abc123"


def poll_suno_job(job_id: str, timeout: int = 300, interval: int = 5) -> str:
    """
    job_id を定期的にポーリングし、完了したら audio_url を返す。
    timeout: 最大待機秒数, interval: ポーリング間隔(秒)
    """
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Suno job {job_id} timed out after {timeout}s")
        url = f"https://api.suno.ai/v1/jobs/{job_id}"
        headers = {"Authorization": f"Bearer {os.getenv('SUNO_API_KEY')}"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status == "completed":
            return data["result"]["audio_url"]
        if status == "failed":
            raise RuntimeError(f"Suno job {job_id} failed: {data.get('error')}")
        # queued or running の場合は interval 秒だけ待って再試行
        time.sleep(interval)


def async_generate_and_download(prompt: str, duration: int = 180) -> str:
    """
    非同期ジョブで生成を実行し、完了したオーディオをダウンロードし、ファイルパスを返す
    """
    job_id = submit_suno_job(prompt, duration)
    # すぐにリクエストを閉じ、ポーリングのみ行うためサーバー負荷が下がる
    audio_url = poll_suno_job(job_id)
    # ダウンロード処理
    audio_resp = requests.get(audio_url, timeout=60)
    audio_resp.raise_for_status()
    audio_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    with open(audio_path, "wb") as f:
        f.write(audio_resp.content)
    return audio_path


# --- メイン処理 ---
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
    tpl = Template(
        open("windsurf/prompts/suno_prompt.j2", encoding="utf-8").read()
    )
    prompt = tpl.render(genre=genre, keyword=keyword)

    # 4. 非同期ジョブで生成＆ダウンロード
    audio_path = async_generate_and_download(prompt, duration=180)

    # 5. 曲タイトルを決定
    title = f"{keyword} - tomatrick"

    # 6. カバーアートを DALL·E で自動生成
    cover_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    dalle_resp = openai.Image.create(
        prompt=f"Album cover art for a {genre} song titled '{title}', vibrant, modern style",
        n=1,
        size="512x512"
    )
    image_url = dalle_resp["data"][0]["url"]
    img_resp = requests.get(image_url, timeout=30)
    img_resp.raise_for_status()
    with open(cover_path, "wb") as f:
        f.write(img_resp.content)

    # 7. DistroKid へアップロード
    print(f"📤 [DistroKid Upload] audio_path = {audio_path}")
    print(f"📤 [DistroKid Upload] cover_path = {cover_path}")
    print(f"📤 [DistroKid Upload] title = {title}")
    print(f"📤 [DistroKid Upload] genre = Pop")
    upload(audio_path, cover_path, title, "Pop")


if __name__ == "__main__":
    try:
        generate_track()
        print("✅ Track generation and upload succeeded")
    except Exception as e:
        print(f"⚠️ Error in generate_upload (skipping): {e}")
