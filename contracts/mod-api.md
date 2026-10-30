# 契約3（OctantPath ↔ OctantCompass）: MOD ↔ OctantCompass API

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。公開（リリース）の前は実装が先で、この文書と OpenAPI を後から合わせます。

版 2.0 · 境界: OctantPath（MOD）↔ OctantCompass · 実装する側: OctantPath と OctantCompass · 形の正本: [mod-api.openapi.yaml](mod-api.openapi.yaml) · 例: [examples/mod-api/](examples/mod-api/)

項目の形と意味はスキーマにだけ書き、この文書は項目をまたぐ振る舞いだけを書きます（[契約の決まり](README.md)）。

HTTP + JSON で通信し、パスの `/v1/` でバージョンを分けます。MOD は `/v1/health` だけを見て、接続中か未接続かを判断します。

ユーザーの履歴と推薦の設定の正本は OctantPath にあり、OctantPath の環境（Beat Saber のインストールやプロファイル、別の端末）ごとに分かれます。OctantCompass は環境ごとにキャッシュを持ち、トークンで環境を見分けます（憲法の原則 4・5・7。2026-10-06 決定）。

MOD（OctantPath）と OctantCompass は別々のリポジトリで別々に更新されるため、版の確認で互換性を守ります。要求と応答の JSON の例はこのリポジトリの [examples/mod-api/](examples/mod-api/) に置き、両方のリポジトリのテストが同じ例を読みます。

## 共通ルール

| 項目 | 案 |
| --- | --- |
| トランスポート | HTTP/1.1 + JSON（UTF-8）。既定は 127.0.0.1 だけで待ち受ける。別の端末（別の PC、Android の Beat Saber など）からつなぐときは、OctantCompass の設定で待ち受けるアドレスを広げる。つなぐ先の見つけ方とペアリングは契約6（つなぐ側 ↔ OctantCompass） |
| 設定ファイル | OctantPath と OctantCompass は別々の設定ファイルを持ち、相手のファイルを読み書きしない。OctantPath の設定は環境ごとに `Beat Saber/UserData/OctantPath/` に置き、推薦の設定もここに入る。OctantCompass の設定は OctantCompass の置き場所にあり、待ち受けるアドレスとポート、DB の置き場所など OctantCompass 自身の動作だけを持つ |
| ポート | OctantCompass は既定で決まった番号で待ち受け、設定で変えられる（番号と見つけ方は[契約6（つなぐ側 ↔ OctantCompass）](launch.md)。2026-10-13 決定）。MOD は、つなぐ先（OctantCompass の ID、アドレスとポート）とトークンを、自分の設定の接続情報に持つ |
| バージョン | メジャー版をパスに入れる（`/v1/`）。版の上げ方と確かめ方は[契約の版と食い違いの知らせ方](README.md#契約の版と食い違いの知らせ方)と、下の[版の食い違い](#版の食い違い)のとおり。MOD はすべての要求にヘッダ `OctantPath-Api-Version`（OpenAPI の `OctantPathApiVersion`）を付ける |
| 未知の項目 | 受け取った側は無視する（マイナー版の追加で壊れないため） |
| 認証 | `/v1/health` と `/v1/pair` 以外は、`Authorization: Bearer <トークン>` が要る。トークンはペアリング（契約6（つなぐ側 ↔ OctantCompass））で OctantCompass が環境ごとに発行し、OctantCompass で取り消すまで変わらない。127.0.0.1 でも要る（同じ PC の複数の環境を見分けるため）。この契約が扱うのは `/v1/` の下だけで、OctantCompass の手元の管理 API（`/manage/`）はこの契約の外にあり、トークンではなく、同じ PC からの要求か、ほかのサイトのページからでないかを OctantCompass が確かめて守る（[OctantCompass 法](../octantcompass/law.md#1-守る境界)の 1.10） |
| マップの識別 | BeatSaver の版ごとの hash に統一する（`mapKey` は表示にだけ使う）。難易度は `hash` + `characteristic` + `difficulty`。hash は 40 桁の 16 進。送る側は小文字で送り、受け取る側は大文字でも小文字でも受け付けて、小文字にそろえてから比べる（[OctantPath 法](../octantpath/law.md)の 1.2）。Beat Saber のまわりでは両方が混ざっているため（大文字: SongCore、ゲームの levelID。小文字: BeatSaver の API、OctantCompass の DB）。Quest 版が起点の hash を大文字のまま送り、OctantCompass がそのまま比べて起点の譜面が見つからないと断ったことから決めた（2026-10-21） |
| 日時 | ISO 8601、UTC |
| 数値のパラメータ | 再試行の間隔、タイムアウト、推薦の件数など、数値はすべて設定 JSON で変更できる。MOD と推薦の数値は OctantPath の設定、OctantCompass の動作の数値は OctantCompass の設定にある |

## エンドポイント

要求と応答の項目の形と意味は、[OpenAPI](mod-api.openapi.yaml) の各操作と、そこから参照するスキーマの `description` にあります。

| メソッドとパス | 用途 | OpenAPI の操作 |
| --- | --- | --- |
| `GET /v1/health` | 接続状態の確認 | `getHealth` |
| `POST /v1/pair` | ペアリング（手順は[契約6（つなぐ側 ↔ OctantCompass）](launch.md)） | `pair` |
| `POST /v1/recommendations` | 推薦の要求 | `recommend` |
| `GET /v1/presets` | プリセット（推薦の条件の組み合わせに名前を付けたもの）の一覧。OctantPath はこれをボタンにする | `getPresets` |
| `PUT /v1/signals` | MOD が持つシグナルの正本を丸ごと送り、OctantCompass が持つものを置き換える | `replaceSignals` |
| `POST /v1/signals` | MOD が観測したシグナルと、取り込んだ導入前の記録の送信 | `sendSignals` |
| `POST /v1/profile` | 推定した実力と好みの表示 | `getProfile` |

各操作の振る舞い（順位を変えないこと、前もって頼めること、signal の送り方と受け取り方など）は、OpenAPI の各操作の `description` にあります。ここには、操作をまたぐことと MOD の側の振る舞いだけを書きます。

- 難易度が `auto` のときは、OctantCompass が session context から狙いを選び（[OctantCompass 法](../octantcompass/law.md#2-履歴と-session-context)の 2）、OctantVector が狙いを譜面の距離に変えます（[推薦の定義](../plans/recommendation-definition.md)の Q4）
- プリセットを足しても契約は変わりません。中の条件は OctantVector が持ち（配布 DB の手札か、なければ OctantVector の既定の手札。憲法の原則 5）、OctantCompass は中継します（[プリセット](../plans/presets.md)）
- OctantPath は `/v1/health` の `presetsRevision` が変わったときと、`unknown_preset` を受けたときに一覧を取り直します
- 導入済みのマップも推薦に入ります。MOD は導入済みのものを取り直さずに表示します。出さないものを渡すかは、MOD が場面ごとに決めます（例: お試し枠の自動ダウンロードでは導入済みを除く）
- OctantCompass が受け取らなかった event とその理由は、応答の `rejected`（OpenAPI の `SignalsResponse`）にだけ書きます
- signal の項目（`recommendation` の任意の `preset` など）の形と意味は [event のスキーマ](schemas/common/event.schema.json)に、OctantVector が推定にどう使うかは[契約1（OctantCompass・OctantHarvest → OctantVector）の履歴の signal の扱い](engine-runtime.md#履歴の-signal-の扱い)にあります

## 版の食い違い

MOD と OctantCompass は互いの版を知っているので、どちらを上げればよいかを両方が言えます。

| 状況 | OctantCompass | MOD |
| --- | --- | --- |
| メジャー版が違う | `/v1/health` 以外の要求に 426（`version_mismatch`）を返す。本文に自分の版と要求の版を入れる | 推薦機能を止め、「OctantCompass（X.Y）と OctantPath（Z.W）の版が合いません」と、どちらを上げればよいかを表示する |
| MOD の方がマイナー版が新しい | そのまま答える。知らない `type` の signal は件数に数えて履歴に入れない（`rejected` の理由は `unsupported_type`）。受け取りは止めない | OctantCompass の版にない機能（下の[版ごとの変更](#版ごとの変更)で、その版より後に足したもの）だけを使わない。必要なら「OctantCompass を更新すると使える」と表示する。signal はそのまま送る。OctantCompass が上がれば、起動が変わるので正本を丸ごと送り直し、知らなかった `type` も履歴に入る（2026-10-22 決定。2026-10-08 の「版にない `type` で止める」をやめた） |
| OctantCompass の方がマイナー版が新しい | そのまま答える（MOD が送らない項目は省かれたものとして扱う） | そのまま使う（知らない項目は無視） |

## 失敗時の振る舞い

エラーは HTTP ステータス + `{"error": {"code", "message"}}`（OpenAPI の `ErrorResponse`）で返します。どの操作がいつどの `code` を返すかは、OpenAPI の各操作の `responses` にあります。MOD は `code` で振る舞いを分けます。

| `code` | MOD の振る舞い |
| --- | --- |
| `unauthorized` | ペアリングし直すよう表示する |
| `unknown_preset` | 一覧を取り直す |
| `seed_not_embedded` | 「推薦がありませんでした」に理由を添える |
| `version_mismatch` | [版の食い違い](#版の食い違い)のとおり |
| `internal_error` | 推薦機能を止めず、その要求だけを失敗として扱う |

- MOD は未接続の間 `/v1/health` を一定間隔で再試行し、`ready` になったら連携を始める
- タイムアウト、接続断、`degraded` のときは推薦機能だけを止め、ゲームは通常どおり動かす

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 1.0 | 2026-10-07 | 最初の版。版の確かめ方を契約どうしでそろえた（決定） |
| 1.1 | 2026-10-07 | signal に `like_removed`、推薦の応答に `ignoredWeights` を足した（決定） |
| 1.1 | 2026-10-08 | OctantCompass の版にない `type` の signal は、MOD が送らずに止め、OctantCompass も番号を進めずに受け取りを止める（`unsupported_type`。決定） |
| 1.2 | 2026-10-08 | `/v1/health` の `db` に `roles` を足した（決定） |
| 1.2 | 2026-10-09 | contracts.md から分けた。中身は変わらない |
| 1.2 | 2026-10-10 | 探求中の形の変更なので版を上げない（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)。以下同じ）。`GET /v1/presets`、要求の `preset` と `choices`、手札の `group`、`/v1/health` の `presetsRevision`、エラーの `unknown_preset` と `seed_not_embedded` を足した |
| 1.2 | 2026-10-11 | 認証の行に、管理画面（`/ui/`）はこの契約の外と注記した（決定） |
| 1.2 | 2026-10-12 | 実装の今の形を記録した（決定）。`recommendation` の任意の `preset`、signal の拒否の理由、ヘッダのない要求の 426、`/v1/health` の理由、`/v1/profile` の形、OctantCompass だけが使う `params` など |
| 1.2 | 2026-10-13 | 待ち受けとポートを契約6（つなぐ側 ↔ OctantCompass）2.0 に合わせた（決定）。形は変わらない |
| 1.2 | 2026-10-15 | 例とスキーマから `params.likeMinPlays` と使っていない部品（`Chart`、`Exclusion`）を外し、重みの例をビューの id にした。形は変わらない |
| 2.0 | 2026-10-22 | signal の通し番号をやめた（決定）。OctantCompass は signal を動いている間だけメモリに持ち、OctantPath は `PUT /v1/signals` で正本を丸ごと送って置き換え、あとは `POST` で足す。`/v1/health` の `lastSeq` を `instanceId`（起動を表す値）と `signals`（件数）に、応答の `lastSeq` を `count` に替え、event の `seq`、`rejected` の `sequence_gap` と `invalid_seq`、409 `signal_conflict`、版にない `type` で止める決まりを消した。互換がないのでメジャー版を上げた |
| 2.0 | 2026-10-23 | エンドポイントの表に `PUT /v1/signals` を足し、認証の行の管理画面を管理 API（`/manage/`）にした。形は変わらない |
| 2.0 | 2026-10-24 | `imported_play` に任意の `cleared`（PlayerData にその譜面のスコアがある）を足した。省いても今までどおりで、知らない項目は無視するので版は上げない |
| 2.0 | 2026-10-30 | 手札に任意の `genreLabels`、候補の理由に任意の `hand` と `genre`（契約1（OctantCompass・OctantHarvest → OctantVector）の 1.1）、`recommendation` の event に任意の `hand` を足した。省いても今までどおりで、知らない項目は無視するので版は上げない |
