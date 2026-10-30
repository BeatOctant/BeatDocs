# 契約1 生成側（OctantHarvest → OctantVector）: OctantVector の生成側の関数 API

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。公開（リリース）の前は実装が先で、この文書を後から合わせます。

版 1.1 · 境界: OctantHarvest → OctantVector · 実装する側: OctantVector · 形の正本: この文書の関数の表（JSON で受け渡す値がないため、スキーマはない）

## 公開する関数

OctantHarvest は、収集した入力（[契約4（OctantHarvest の収集結果 → OctantVector）](generation-input.md)。アーカイブのフォルダとカタログのファイル）と作業用の保存先の場所、数値を毎回引数で渡します。生成側も設定ファイルや環境変数を読まず、通信もしません。モデルのファイルも取りに行かず、呼ぶ側が `models(views)` で聞いて `models_dir` に置いたものを読みます。関数は `octantvector.generation` にあります。`params` の名前は [OctantVector の設定](../octantvector/config.md) と同じで、渡さなかったものは既定値になります。計算するビューは呼ぶ側が毎回名指しします（エンコーダの段階による既定はありません。2026-10-14）。

| 関数 | 入力 | 出力 |
| --- | --- | --- |
| `compute(input, store, views, params, pool, models_dir, log)` | 契約4（OctantHarvest の収集結果 → OctantVector）の収集結果、作業用の保存先、計算するビュー（`id` か `id@version`。必須。派生ビューの元も計算する）、数値、プールの名前（既定 `distribution`。[OctantVector の設定](../octantvector/config.md)のプール）、モデルのフォルダ、記録の書き先 | 足りない分だけを計算して保存先と台帳に書いた結果の件数（計算、失敗、飛ばし、後回し。ビューごとにも）。譜面の指標（契約2（DB 生成 ↔ 推薦コア）の `charts.parquet` の Pass と Tech）の元のビューは、名指ししなくても計算する。GPU に空きがないときは一度に渡すマップを減らし、1 つでも入らないマップは書かずに後回し（`deferred`）にして次の呼び出しで計算する。止めても続きから再開でき、続けて呼ぶと 2 回目は何も計算しない |
| `models(views)` | ビュー | そのビュー（と派生の元）が読むモデルの一覧（`repo`、`revision`、`files`、`models_dir` の下の `path`。`hf/<repo>/<revision>`）。呼ぶ側はこれを `compute` の前に `models_dir` へ置く（OctantHarvest の `octantharvest models`） |
| `drift(store, base, params)` | 保存先、比べる配布 DB（全量）、数値 | ビューごとの、校正からのずれ。関係のビューは測らない。`base` に、入っているエンコーダ（プラグインを含む）のどれも計算しないベクトルのビューがあればエラー（プラグインの入れ忘れに気づくため） |
| `calibrate(store, views, params)` | 保存先、ビュー、数値 | 新しい校正（JSON）。プールは `distribution` |
| `release(input, store, views, calibration, base, out, params, full, built_at, log, presets, notice)` | 収集結果、保存先、ビュー（必須。DB に入れるビューの全部）、校正（空なら前の版のものに新しいビューの統計を足す）、前の版の全量（なければ空）、書き出すフォルダ、数値、全量にするか（任意）、`builtAt` の値（任意。試験用）、記録の書き先（任意）、手札（任意。手札の配列か、それを入れた JSON ファイル。省けば前の版の手札を引き継ぐ）、DB 全体の利用条件とクレジット（任意。Markdown の文字列。省けば前の版のものを引き継ぐ。ビューごとのクレジットはエンコーダから書く） | [契約2（DB 生成 ↔ 推薦コア）](vector-db.md) の全量と、作れるときは前の版からの差分。承認と索引に使う「配る方」（差分か全量）のフォルダ |
| `keygen(path)` | 秘密鍵を書き出すファイルの場所（すでにあればエラー） | 公開鍵と `keyId`。公開鍵は OctantVector に同梱する一覧に足すか、`build_index` の `trusted_keys` で渡す（OctantHarvest の設定 `signing.publicKey`）（[署名](distribution.md#署名)） |
| `sign(folder, key_path)` | 「配る方」のフォルダ、秘密鍵のファイル | フォルダに書いた `manifest.sig`（[署名](distribution.md#署名)） |
| `pack(folder, out)` | 全量のフォルダ、書き出すフォルダ | 索引なしで手渡しする tar 1 つ（`<dbVersion>.full.tar`。分ける前の索引のファイルと同じバイト列）。差分は断る。同じ名前のファイルがあればエラー（[契約5 の非公開（探求中）の扱い](distribution.md#非公開探求中の扱い)） |
| `build_index(releases, out, params)` | 承認済みの版の「配る方」のフォルダの一覧、書き出すフォルダ、数値（`part_size_mb`、`publish_url`、`allow_unsigned`、`trusted_keys`） | [契約5（OctantHarvest → 配布先 → OctantCompass）](distribution.md) の索引と、分割したファイル。索引に載せる版の署名を、同梱の鍵か `trusted_keys`（`keyId` から公開鍵の base64 への対応。OctantHarvest は設定の `signing.publicKey` を渡す）で `apply_update` と同じように確かめ、確かめられない版があればエラー。渡されたが索引に載らない古い版は確かめない（`allow_unsigned` が真なら確かめずに載せる。開発用） |

- `release` は、収集結果にアーティストの 2 つのファイル（[契約4（OctantHarvest の収集結果 → OctantVector）](generation-input.md)）があれば、関係のビュー `listenbrainz_artists@<取得日>`（役割 `artist`。[契約2（DB 生成 ↔ 推薦コア）のビューの種類](vector-db.md#ビューの種類)）を書く。なければ前の版のものを引き継ぐ（2026-10-12 決定）
- `views` には、エンコーダのビューのほかに、カタログから作る関係のビュー `beatsaver_mappers`（譜面の作者。役割 `mapper`。[契約2（DB 生成 ↔ 推薦コア）のビューの種類](vector-db.md#ビューの種類)）を名指しできる。計算も校正もしないので、`compute`・`calibrate`・`models` は読み飛ばし、`release` が版を作るたびにカタログから作って入れる。名指ししなければ入れず、前の版のものも引き継がない（2026-10-20 決定）
- `release` は、手札のうち新しい DB で使えないもの（[契約1（OctantCompass・OctantHarvest → OctantVector）の手札が使えるとき](engine-runtime.md#手札が使えるとき)の決まりで外れるもの、同じ `id`）があれば、何も書かずにエラーで止まる。作者がその場で気づけるように、推薦側のように黙って外さない

いつ呼ぶか、どの版を承認して載せるか、配布先へのアップロードは OctantHarvest が決めます。作るものの形は[契約2（DB 生成 ↔ 推薦コア）](vector-db.md)、受け取るものは[契約4（OctantHarvest の収集結果 → OctantVector）](generation-input.md)で、OctantVector の中の手順は [OctantVector の設計](../octantvector/design.md)にあります。

## エラーの種類

生成側の関数が出すエラーは `GenerationError` で、`octantvector.generation` から import できます。プロセスを止める例外（`SystemExit`）は出しません（OctantHarvest がその実行の失敗として記録して続けられるように）。読めない収集結果（[契約4（OctantHarvest の収集結果 → OctantVector）](generation-input.md)）や読めない DB には `VersionError`（`GenerationError` の一種）を出します。意味は[推薦側のエラーの種類](engine-runtime.md#エラーの種類)と同じです。これ以外の例外は想定外のもので、OctantVector の不具合か、契約に合わない引数です。

## 版の付け方

- 生成側の API の版は `octantvector.generation.API_VERSION`（`"1.1"` の形の文字列）で名乗る。推薦側の版とも、OctantVector のパッケージの版とも別に上がる。上げ方と、OctantHarvest が確かめて食い違ったときの扱いは[契約の版と食い違いの知らせ方](README.md#契約の版と食い違いの知らせ方)のとおり
- OctantHarvest は実行の前に、メジャー版が同じで、自分が使う機能のあるマイナー版以上かを確かめる
- OctantHarvest が import するのは `octantvector.generation` だけ。OctantVector は推薦側と同じく git のタグから入れる（[推薦側の版の付け方](engine-runtime.md#版の付け方)）

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 1.0 | 2026-10-09 | 最初の版。パッケージの版から API の版を切り離した（OctantVector 0.3.8 と同じ API） |
| 1.0 | 2026-10-10 | 探求中の形の変更なので版を上げない（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)。以下同じ）。`release` に `presets` を足した（決定、OctantVector 0.3.11） |
| 1.0 | 2026-10-12 | `release` が関係のビュー `listenbrainz_artists@<取得日>`（役割 `artist`）を書くようにした（決定、OctantVector 0.3.26） |
| 1.0 | 2026-10-14 | ビューは呼ぶ側が必ず名指しする。`compute` に `pool`・`models_dir`・`log`、`release` に `full`・`built_at`・`log`、`models(views)` を足し、エラーを `GenerationError` にそろえた（決定、OctantVector 0.4.0） |
| 1.0 | 2026-10-15 | `build_index` に `trusted_keys` を足し、索引に載せる版の署名を確かめるようにした（OctantVector 0.4.1） |
| 1.0 | 2026-10-17 | 全量を tar 1 つで手渡しする `pack` を足した（決定、OctantVector 0.6.0） |
| 1.0 | 2026-10-18 | `release` に `notice` を足し、ビューごとのクレジットをマニフェストに書くようにした（決定、OctantVector 0.7.0） |
| 1.0 | 2026-10-20 | `views` に関係のビュー `beatsaver_mappers` を名指しできるようにした。アーティストのファイルがないとき引き継ぐのは前の版の近いアーティストのビューだけにした（決定、OctantVector 0.8.0） |
| 1.1 | 2026-10-25 | `compute` の結果に後回しの件数 `deferred` を足し、API の版を 1.1 にした |
| 1.1 | 2026-10-29 | `compute` が譜面の指標の元のビューも計算し、`release` が `charts.parquet` の Pass と Tech を埋めるようにした |
