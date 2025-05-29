import os, openai, random

def generate_keyword():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        rsp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",                # ← ここを変更
            messages=[{"role":"user",
                       "content":"小学生が楽しく歌える日本語キーワードを5つ"}],
            temperature=0.9,
        )
        # レスポンスからリスト抽出
        candidates = [w.strip(" ・,、")
                      for w in rsp.choices[0].message.content.splitlines()
                      if w.strip()]
        return random.choice(candidates)
    except Exception:
        # フォールバック用の固定リスト
        fallback = ["星", "虹", "冒険", "友情", "夢"]
        return random.choice(fallback)
