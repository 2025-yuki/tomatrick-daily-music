import os, openai, random

def generate_keyword():
    # OpenAI APIを使用して小学生向けのキーワードを生成
    openai.api_key = os.getenv("OPENAI_API_KEY")
    rsp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":"小学生が楽しく歌える日本語キーワードを5つ"}],
        temperature=0.9,
    )
    # 生成されたキーワードからランダムに1つ選択
    return random.choice([
        w.strip(" ·,、") for w in rsp.choices[0].message.content.splitlines() if w.strip()
    ])
