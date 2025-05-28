import os, json, random, tempfile
from jinja2 import Template
from tenacity import retry, stop_after_attempt, wait_fixed
from suno import Suno
from pick_keyword import generate_keyword
from dk_upload import upload

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def main():
    # キーワードの生成
    keyword = generate_keyword()
    
    # ジャンルの選択
    genre = random.choice([
        "Japanese Pop", "Japanese Hip-Hop", "Japanese Pop-Rock"
    ])
    
    # プロンプトテンプレートの読み込みとレンダリング
    prompt_tpl = Template(
        open("windsurf/prompts/suno_prompt.j2").read()
    )
    prompt = prompt_tpl.render(genre=genre, keyword=keyword)
    
    # Suno APIを使用して曲の生成
    suno = Suno(api_key=os.getenv("SUNO_API_KEY"))
    audio_path, _ = suno.create_song(
        prompt=prompt, duration="full", format="wav"
    )
    
    # 一時的なジャケットアートの作成
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as cover_file:
        # TODO: ジャケットアートの生成実装
        cover_path = cover_file.name
    
    # タイトルの生成
    title = f"{keyword}の歌"
    
    # DistroKidへのアップロード
    upload(audio_path, cover_path, title, genre)
    
    # 一時ファイルのクリーンアップ
    os.unlink(cover_path)

if __name__ == "__main__":
    main()
