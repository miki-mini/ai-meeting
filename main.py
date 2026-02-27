import os
import random
import datetime
import concurrent.futures
import re
from dotenv import load_dotenv
from openai import OpenAI

# 1. 環境変数の読み込み (.envファイルからAPIキーを取得)
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("エラー: .env ファイルに OPENROUTER_API_KEY が設定されていません。")
    print("      .env.example を .env にリネームし、APIキーを記述してください。")
    exit(1)

# 2. OpenRouter クライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# 3. 参加するAIモデルの定義 (OpenRouterのモデルIDを指定)モデルの金額に注意！
models = {
    "Gemini": {"name": "Gemini", "id": "google/gemini-3.1-pro-preview"},
    "Claude": {"name": "Claude", "id": "anthropic/claude-opus-4.6"},
    "ChatGPT": {"name": "ChatGPT", "id": "openai/gpt-5.2"},
    "Grok": {"name": "Grok", "id": "x-ai/grok-4"},
    "Gemma": {"name": "Gemma", "id": "google/gemma-3-27b-it"},
    "Mistral": {"name": "Mistral", "id": "mistralai/mistral-large-2512"},
}
participants = [m["name"] for m in models.values()]

# 議論のテーマ
theme = "誰が一番優しい？"
# 何回発言を回すか
max_rounds = 2

# 保存用ログファイル名
log_filename = f"meeting_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

# 4. ログファイルの初期化
with open(log_filename, "w", encoding="utf-8") as f:
    f.write(f"# AI 6人会議ログ\n\n**テーマ**: {theme}\n\n")

# 共通メモ（これまでのすべての発言を蓄積して全員に渡す）
transcript = ""

def generate_prompt(model_name, current_transcript, unspoke_members):
    prompt = f"""あなたは {model_name} です。
現在、AIたち（{', '.join(participants)}）で以下のテーマについて会議をしています。

【テーマ】
{theme}

【これまでの会議の履歴（共通メモ）】
{current_transcript if current_transcript else "(まだ誰も発言していません。あなたが最初の発言者です。)"}

【あなたへの指示】
・これまでの履歴（共通メモ）を読み、あなたならどう思うか、独自の視点から意見を述べてください。
・発言はなるべく短く、簡潔にお願いします。（目安として1〜2段落程度で、長くても300文字以内）
・「結論を出すこと」や「意見をまとめること」は一切要求されていません。満足するまで議論を続けるため、自由に話を広げたり深掘りしたりしてください。
・他のAIの発言を引用して同意したり、反論したりするのも大歓迎です。
・出力はあなたの発言内容のみとしてください。（Zennの記事に載せるためMarkdown形式でお願いします）
"""

    if model_name == "Gemini" and unspoke_members:
        prompt += f"\n・回答の最後に、「次は誰が話すべきだと思う？」という問いに答える形で、まだ発言していないメンバー（{', '.join(unspoke_members)}）の中から次に意見を聞きたい人を1人指名してバトンを渡してください。必ず「次は〇〇さん、お願いします」のように名前を明確に出してください。\n"

    return prompt

def get_eagerness(model, transcript):
    prompt = f"""あなたは {model['name']} です。
現在、AIたち（{', '.join(participants)}）でテーマ「{theme}」について会議をしています。

【これまでの会議の履歴】
{transcript if transcript else "(まだ誰も発言していません。)"}

【あなたへの指示】
上の履歴を踏まえて、今すぐ次に自分が発言したい度合いを 0〜100 の数値で答えてください。
(例: 反論があるなら100、同意して補足したいなら80、特に言うことがないなら10 など)
出力は数値のみ（例: 85）にしてください。理由やその他の言葉は一切含めないでください。"""

    try:
        response = client.chat.completions.create(
            model=model["id"],
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://github.com/your-repo/ai-meeting",
                "X-Title": "AI 4-Person Meeting Script",
            }
        )
        reply = response.choices[0].message.content.strip()
        match = re.search(r'\d+', reply)
        return int(match.group()) if match else 0
    except Exception:
        return 0

print("=== AI 4人会議を開始します ===")
print(f"テーマ: {theme}")
print(f"ログ保存先: {log_filename}")

for round_num in range(1, max_rounds + 1):
    print(f"\n--- Round {round_num} ---")
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"\n## Round {round_num}\n\n")

    unspoke_members = participants.copy()

    # ラウンドの最初のスピーカーを決める
    if round_num == 1:
        current_speaker_key = list(models.keys())[0] # 最初はGeminiから
    else:
        # # ログを読ませて一番発言したい人をラウンド最初に持ってくる
        # print("\n[次のラウンドの最初の発言者を立候補で決定しています...]")
        # eagerness_scores = {}
        # with concurrent.futures.ThreadPoolExecutor(max_workers=len(unspoke_members)) as executor:
        #     futures = {executor.submit(get_eagerness, models[k], transcript): k for k, v in models.items() if v["name"] in unspoke_members}
        #     for future in concurrent.futures.as_completed(futures):
        #         m_key = futures[future]
        #         score = future.result()
        #         eagerness_scores[m_key] = score
        #         print(f"  - {models[m_key]['name']} の発言意欲: {score}/100")
        # current_speaker_key = max(eagerness_scores, key=eagerness_scores.get)
        # print(f"-> 【{models[current_speaker_key]['name']}】 が一番話したそうなので話し始めます！\n")

        # 代わりにGeminiから開始する
        current_speaker_key = list(models.keys())[0] # 最初はGeminiから

    while unspoke_members:
        model = models[current_speaker_key]
        unspoke_members.remove(model["name"])

        print(f"\n[{model['name']} が思考中...]")

        prompt = generate_prompt(model['name'], transcript, unspoke_members)

        try:
            response = client.chat.completions.create(
                model=model["id"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                # OpenRouterの規約や推奨設定としてReferer等を入れる
                extra_headers={
                    "HTTP-Referer": "https://github.com/your-repo/ai-meeting",
                    "X-Title": "AI 4-Person Meeting Script",
                }
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"APIエラーが発生しました: {e}"
            print(f"エラー: {e}")

        # 全員に渡す共通メモに追加
        transcript += f"\n### {model['name']} の発言\n{reply}\n"

        # Markdownファイルに毎回の発言を追記
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"### {model['name']}\n\n{reply}\n\n")

        print(f"-> {model['name']} の発言が完了しました。")

        # 次のスピーカーを決める
        if unspoke_members:
            if len(unspoke_members) == 1:
                # 最後の1人は自動的に決定
                current_speaker_key = [k for k, v in models.items() if v["name"] == unspoke_members[0]][0]
                print(f"\n-> 残るは {models[current_speaker_key]['name']} なので、そのまま指名します！")
            else:
                next_speaker_name = None
                is_nominated = False

                # Geminiが指名した場合、その文字列を探す
                if model['name'] == "Gemini":
                    # 複数人の名前が出た場合の誤検知を防ぐため、うしろから探すか、
                    # 先に見つかったものにするなどの工夫も可能だが、ひとまず存在確認とする
                    for member in unspoke_members:
                        if member in reply:
                            next_speaker_name = member
                            is_nominated = True
                            break

                # 誰の指名もない場合、またはGeminiが名指ししなかった場合はランダムに次を決める
                if not next_speaker_name:
                    next_speaker_name = random.choice(unspoke_members)

                # キーを探す
                current_speaker_key = [k for k, v in models.items() if v["name"] == next_speaker_name][0] # dictionary keys happen to be names

                if is_nominated:
                    print(f"-> Geminiの指名により、次は 【{models[current_speaker_key]['name']}】 に回します！")
                else:
                    print(f"-> ランダムに選ばれ、次は 【{models[current_speaker_key]['name']}】 に回します！")

                # # --- 前の指名法（立候補制）：コメントアウト ---
                # print("\n[次の発言者を立候補で決定しています...]")
                # eagerness_scores = {}
                # with concurrent.futures.ThreadPoolExecutor(max_workers=len(unspoke_members)) as executor:
                #     futures = {executor.submit(get_eagerness, models[k], transcript): k for k, v in models.items() if v["name"] in unspoke_members}
                #     for future in concurrent.futures.as_completed(futures):
                #         m_key = futures[future]
                #         score = future.result()
                #         eagerness_scores[m_key] = score
                #         print(f"  - {models[m_key]['name']} の発言意欲: {score}/100")
                #
                # # 最高スコアの人を選ぶ
                # current_speaker_key = max(eagerness_scores, key=eagerness_scores.get)
                # print(f"-> 【{models[current_speaker_key]['name']}】 が一番話したそうなので、次に指名します！")
                # # ----------------------------------------------

print(f"\n会議終了。ログを {log_filename} に保存しました。")
