[日本語](README.md) | [English](README_en.md)

# slack-guest-inspection

Slack EnterpriseGrid 環境にあるすべてのワークスペースにおいて、  
「1つ以下のチャンネルにしか所属していないマルチチャンネルゲスト」を探し、一覧化して csv に出力するスクリプトです。

## How to use

### prepare

* SlackApp のトークンを用意してください。必要な permission は以下の通りです。
  * `discovery:read`
* このプロジェクトを clone し、 `config.ini` を作成してください。

### run

* `main.py` を実行してください。
* 標準出力に実行状況を出力しながら実行します。ログファイルは出力しません。
* Slack の WebAPI をループ実行するため、調査対象ユーザ数が多い場合は時間がかかる可能性があります。SlackAPI の RateLimit に到達した可能性がある場合は、最大61秒 Sleep して継続実行しますが、それでも失敗した場合は例外を投げてスクリプトが終了します。
* 精査が完了すると、 `OUTPUT.csv` に結果を出力します。
  * 既に `OUTPUT.csv` ファイルが有る場合、上書きします。過去の実行結果を失いたくない場合は事前に退避させてください。

## information

* このスクリプトは python の外部ライブラリを利用する必要なく動作するように作成されています。SlackSDK も使用していません。
* `inspection` という単語がこの用途に正しいのかちょっと自信ありません。もしよりよい単語があったら教えてください。🙇‍♂️
