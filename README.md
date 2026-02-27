# AI 4人会議 (AI Meeting Script)
![](images/AI.png)

5つの異なるAIモデル（Gemini, Claude, ChatGPT, Grok, Gemma, Mistralの中から毎回指名制で発言）を会話させ、その内容を自動的にMarkdown形式の議事録として保存するPythonスクリプトです。Zennなどの記事作成のネタ出しや、各モデルの特性・意見の違いを観察するのに最適です。

## 特徴
* **OpenRouter API** を利用し、複数の異なるプロバイダのLLMを1つのスクリプトで呼び出します。
* **Geminiが司会進行**を務めるモードを搭載。Geminiが会話の流れを読んで、次に発言するAIを名指しで指名します。
* 指名がなかった場合は、発言していないAIの中からランダムに次のスピーカーが選ばれるため、予測不能な議論が展開されます。
* 議論のログは実行フォルダに `meeting_log_YYYYMMDD_HHMMSS.md` のようなファイル名で自動保存されます。

## 前提条件
* Python 3.8 以上
* [OpenRouter](https://openrouter.ai/) のアカウントとAPIキー

## セットアップ手順

1. **リポジトリの準備**
このフォルダ一式（または `main.py`, `requirements.txt`, `.env.example`, `.gitignore`）をお手元の環境に配置します。

2. **仮想環境の作成とパッケージのインストール**
```bash
python -m venv .venv

# Windowsの場合
.\.venv\Scripts\activate
# Mac/Linuxの場合
# source .venv/bin/activate

pip install -r requirements.txt
```

3. **環境変数（APIキー）の設定**
フォルダ内にある `.env.example` をコピーして、新しく `.env` という名前のファイルを作成してください。
その `.env` ファイルを開き、取得したOpenRouterのAPIキーを貼り付けます。
```env
OPENROUTER_API_KEY=sk-or-v1-************************
```
※ `.gitignore` により `.env` は除外されているため、GitHubにうっかりAPIキーが公開されることはありません。

## 使い方

1. `main.py` をテキストエディタ等で開き、必要に応じて「議論のテーマ」や「何周させるか（ラウンド数）」を変更します。
```python
# 議論のテーマ
theme = "誰が一番優しい？"
# 何回発言を回すか
max_rounds = 2
```

2. スクリプトを実行します。
```bash
python main.py
```

3. ターミナル上で議論がリアルタイムに進行します。終了後、同じフォルダに `meeting_log_...md` というファイルが生成されています。

## カスタマイズ
`main.py` の `models` 辞書を編集することで、参加させるAIモデルを変更できます。OpenRouterで提供されているお好きなモデルIDを指定してください。

## ライセンス
MIT License (またはご自由にお使いください)
