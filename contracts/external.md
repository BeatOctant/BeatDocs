# 外部依存（こちらでは決められないもの）

> 固さ: 固める核（外へ出るもの: BeatSaver などからの取得の仕方、スコアの送信）。実装と食い違ったら、実装を直さず [open.md](../open.md) に報告します（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。正本: この文書。

どの契約にも属さず、相手の形式に従うしかないものです。

相手の形式に従うしかないので、読み取る部分を差し替えやすい部品にして、上の契約の形に変換します。

## 相手ごとの扱い

### BeatSaver API

- 使う場所: OctantHarvest の収集、MOD の問い合わせとダウンロード、OctantPath Desktop の問い合わせとダウンロード、Desktop の画面のカバーと試聴の中継（`/api/cdn`）、Quest 版 OctantPath の PC のプロキシ（ネットにつながない Quest の MOD の問い合わせ・カバー・試聴・zip を PC が中継する。2026-10-20 決定）
- 変換先: 契約4（OctantHarvest の収集結果 → OctantVector）の入力形式
- 取得の決まり:
  - 公開されたレート制限はない（[API の説明](https://api.beatsaver.com/docs)に記載がなく、応答にも `X-RateLimit-*` や `Retry-After` が付かない。2026-10-03 確認）
  - [利用規約](https://beatsaver.com/policy/tos)（2025-01-06 版）に自動ダウンロードを禁じる条項はないが、サイトに負担をかける使い方とサイトのコンテンツの商用化は禁止（Account Policy）で、BeatSaver はいつでもアクセスを止められる
  - 他人のコンテンツを明示の許可なく再公開・使用することも禁止（Content Policy の Beatmap Rights。主に他人のマップを BeatSaver に上げる場面の条項と読める。推測）なので、zip・譜面・カバー・試聴は配らない
  - 配布 DB（事実と計算した数値の表）を配ることは、運営への問い合わせ（配るのは数値だけ、削除されたマップは消す、と伝えた）への返事「It's an open API」（2026-10-17）を了承とみなした（2026-10-17）
  - そのため、`/maps/ids` と `/maps/hash`（1 回に 50 件まで）でまとめて問い合わせ、キーから 1 件を引くとき（OctantPath Desktop の起点の検索。OctantPath #31）だけ `/maps/id/{key}` を使い、API へのリクエストは直列にして間隔を空ける
  - マップの zip の取得（CDN）は、同時数と 1 秒あたりの開始数に上限を設ければ並べてよく、上限は取る部品の設定で決める（2026-10-06 決定）
  - 429 には間隔を延ばして再試行し、どの部品か分かる User-Agent（OctantPath か OctantHarvest）を付ける
  - zip・カバー・試聴は https の beatsaver.com とその下からだけ取り、転送の先も確かめる
  - Desktop の中継（`/api/cdn`）は、1 つの応答の大きさ・同時数・待ち時間に上限を設ける（設定 `cdnMaxMegabytes`・`cdnConcurrency`・`cdnTimeoutSeconds`。OctantPath #32）
  - Quest 版の PC のプロキシ（OctantPathAndroid の `proxy/`）も、同じく API を直列にして間隔を空け、CDN は同時数と開始数に上限を設け、1 つの応答の大きさと待ち時間に上限を設け、User-Agent は OctantPath（Quest proxy）にする
  - 中継するのは https の beatsaver.com とその下だけで、応答は解釈しない（照会・取得の判断と hash の照合は Quest の MOD がする）
  - ミラーを持つ用途（OctantHarvest のクロール）は、API の説明が勧める `wss://ws.beatsaver.com/maps` の更新通知を使わず、前回の完了した取得を起点に `/maps/latest?sort=UPDATED` と `/maps/deleted` で変わった分だけを取り、投票の変化は `GET /vote?since=` 1 回で直す
  - 全体をたどるのは、完了した取得がないとき、最後の全体の取得から `crawl.fullWalkDays` 日たったとき、`crawl --full` のときだけ（2026-10-14、OctantHarvest #33。この形のままにする: 2026-10-16）
  - 負荷の見積もり（推測。実測していない）: 全体の取得は約 1,450 回（約 14.5 万マップ、1 ページ 100 件、間隔 1 秒以上で 25 分以上）、差分の日は 10 回前後で、`fullWalkDays` が 30 日ならならして 1 日 60 回前後
  - 差分では次の全体の取得まで直らないものがある（推測: `updatedAt` の動かない ranked・qualified などの変化、削除せず非公開にしたマップ、1 ページ 100 件が同じ時刻のときの残り）

### 導入前のプレイの記録

- 相手: 導入前のプレイの記録（SongPlayHistory の `UserData/SongPlayData.json`、DataRecorder の `UserData/DataRecorder/beatsaber.db`）
- 使う場所: OctantPath（導入前の記録の取り込み。憲法の原則 5。取り込み元は 2026-10-03 決定、[過学習の設計の「過去のプレイ記録の取り込み元」](../plans/personal-data-overfitting.md#過去のプレイ記録の取り込み元)）
- 変換先: 契約3（OctantPath ↔ OctantCompass）の `play`（`source` 付き）
- 扱い:
  - ファイルの形は実装するときに、開発の環境のファイルで確かめてここに書く

### Upvote・いいねのローカルファイル

- 使う場所: OctantPath（同上）
- 変換先: 契約1（OctantCompass・OctantHarvest → OctantVector）のシグナル
- 扱い:
  - BeatSaverVoting の投票は `UserData/votedSongs.json`（UTF-8 の JSON）
  - キーは小文字の `hash`、値は `{"hash": キーと同じ hash, "voteType": "Upvote" か "Downvote"}` で、マップキーは入らない
  - 投票し直すと上書きされ、取り消しで消える処理はない（開発の 1.40.8 の環境の BeatSaverVoting 2.4.6 のファイルと逆コンパイルしたソースで 2026-10-03 確認）
  - そのため投票の取り消しの signal はなく、投票し直しは新しい `upvote` か `downvote` として送る

### MusicBrainz と ListenBrainz

- 相手: MusicBrainz（アーティスト ID への照合）と ListenBrainz（似たアーティスト）（[近いアーティスト](vector-db.md#ビューの種類)。2026-10-11 決定）
- 使う場所: OctantHarvest の取り込み（`octantharvest artists`）
- 変換先: 契約2（DB 生成 ↔ 推薦コア）のアーティストの表と近さ（形は未定）
- 扱い:
  - 名前で検索し、上位の点で名前・並べ替え用の名前・別名のどれかが完全に一致したときだけ ID を付ける（違う ID は別のアーティストの近さを持ち込むため、迷ったら付けない）
  - ListenBrainz の API は 1 秒に 1 回までで、連絡先の入った User-Agent が要る（[API の説明](https://listenbrainz.readthedocs.io/en/latest/users/api/index.html)、2026-10-11 確認）
  - MusicBrainz の API も IP ごとに平均 1 秒に 1 回までで、超えると 503 になる（[速度の上限](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting)、2026-10-11 確認）
  - 上限はサービスごとなので、2 つは並べて同時に引いてよい
  - MusicBrainz の中核データは CC0（[データのライセンス](https://musicbrainz.org/doc/About/Data_License)、2026-10-11 確認）
  - ListenBrainz の似たアーティストのデータは CC0（2026-10-17 確認。商用の利用には寄付を求めている。[decisions.md](../decisions.md#近いアーティスト)）

### プレイリスト形式と SongCore

- 使う場所: MOD
- 変換先: 変換なし
- 扱い:
  - 既存の形式に従う

### Hugging Face

- 相手: Hugging Face（配る DB のビューが使うモデルの重み。CLAP、MERT、Demucs など。WavLM は公式の DB に入れない（[決まったこと](../decisions.md#配布)））
- 使う場所:
  - OctantHarvest の `octantharvest models` だけ
  - OctantVector とプラグインは取りに行かず、`models_dir` から読む（[OctantVector の設計](../octantvector/design.md)）
- 変換先: 変換なし
- 扱い:
  - リポジトリと 40 桁の revision を固定して取り、ファイルごとの SHA-256 を `models.json` に記録し、記録と違うファイルは置き換えない（2026-10-16 にこの形を採った）
  - ライセンスはモデルごと
  - MERT は CC BY-NC 4.0 で、`octantvector-mert` はそのモデルのコードの写しを含むので、パッケージ全体も CC BY-NC 4.0（[エンコーダ](../octantvector/encoders.md)）

### ArcViewer

- 相手: [ArcViewer](https://github.com/AllPoland/ArcViewer)（GPLv3）
- 使う場所: OctantPath Desktop の譜面のプレビュー
- 変換先: 変換なし
- 扱い:
  - 初回の起動で、deploy ブランチの決めたコミット（0.8.1）のビルドを raw.githubusercontent.com から取り、ファイルごとに大きさと SHA-256 を照合する
  - 合わなければ何も残さない
  - そのときはプレビューを出さず、公開サイト（allpoland.github.io）には切り替えない（2026-10-16。切り替えると ArcViewer がブラウザから BeatSaver の API と CDN を引き、上の User-Agent と間隔の外になるため）
  - マップは Desktop が手元の zip を渡す

## マップを取る先

MOD がマップを取る先は設定で変えられるようにします。将来、推薦に出そうなマップを前もってローカルに置く仕組みを足すときのためで、試験のあいだ BeatSaver に負担をかけないためでもあります（[推薦の定義](../plans/recommendation-definition.md)の「速さが要る通信」、2026-10-08 決定）。取る先は BeatSaver か、ローカルのフォルダです。フォルダは `<hash の先頭 2 文字>/<hash>.zip` の形で、中身は BeatSaver が配る zip のままです（契約4（OctantHarvest の収集結果 → OctantVector）のアーカイブの `maps/` と同じ形なので、そのまま指せます。hash の大文字と小文字は区別しません）。MOD はフォルダを読むだけです。

## スコアの送信

いまはどこにも送っていません。プレイの記録（精度を含む）は、手元で推薦を計算するために、ペアリングした OctantCompass に渡し、そこから OctantVector に渡すだけです（2026-10-17）。
