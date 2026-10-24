# 契約

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。正本: 契約の決まりはこの文書、契約の形は各契約とスキーマ。

コンポーネントの境界ごとの取り決め（外部契約）です。どの境界にどの契約があり、どちらが実装するかは[憲法の部品と契約の地図](../constitution.md#部品と契約の地図)にあります。契約は憲法の下にあり、憲法を変えられません。契約を変えるにはメンテナーの判断が要ります（憲法の原則 9）。

## 契約の決まり

- **1 つの境界に 1 つのファイル。** 契約の文面はこのフォルダだけに置き、ほかの文書はリンクします。
- **スキーマは、別々のリポジトリが同じ JSON を読み書きする契約にだけ置く。** 契約3（OctantPath ↔ OctantCompass。OctantPath の C# と OctantCompass の Python）は [OpenAPI](mod-api.openapi.yaml)、契約3 が運ぶ契約1（OctantCompass・OctantHarvest → OctantVector）の値（`params`、推薦の条件と候補、`describe` の要約）は [JSON Schema](schemas/) です。スキーマのある項目は、形と意味をそのスキーマの `description` にだけ書き、文章には書き写しません。契約3 が契約1 の値を運ぶところは `$ref` で参照し、定義を写しません。
- **ほかの契約は文章が正本。** 契約1（OctantCompass・OctantHarvest → OctantVector）の関数の名前と引数の並び、契約2（DB 生成 ↔ 推薦コア）・契約4（OctantHarvest の収集結果 → OctantVector）・契約5（OctantHarvest → 配布先 → OctantCompass）のファイルの形は、それぞれの文章の表と例が正本です。
- **例はスキーマに合う。** [examples/](examples/) の例は、[examples/schemas.json](examples/schemas.json) に書いたスキーマに合います。両側のリポジトリのテストが同じ例を読みます。
- **ずれは機械で見つける。** [tools/check.py](../tools/check.py) が、スキーマの正しさ、`$ref` の行き先、例とスキーマ、文書のリンク、`description` に書いた文書の場所を確かめます。PR ごとに GitHub Actions で走ります。
- **版はファイルごと。** 各契約のファイルの冒頭に今の版を書き、変えたときは同じ PR でスキーマと例を直し、そのファイルの「版ごとの変更」に版・日付・1 行の変更を足します。決めた理由は「版ごとの変更」に書かず、[決まったことの記録](../decisions.md)に書きます。すでに使った番号と別の意味でぶつからないよう、使った番号を使い直しません。版の上げ方と食い違ったときの知らせ方は、下の[契約の版と食い違いの知らせ方](#契約の版と食い違いの知らせ方)にだけ書きます。

| 契約 | ファイル | 境界 |
| --- | --- | --- |
| 契約1 推薦側（OctantCompass → OctantVector） | [engine-runtime.md](engine-runtime.md) | OctantCompass → OctantVector |
| 契約1 生成側（OctantHarvest → OctantVector） | [engine-generation.md](engine-generation.md) | OctantHarvest → OctantVector |
| 契約2（DB 生成 ↔ 推薦コア） | [vector-db.md](vector-db.md) | 配布 DB（OctantVector が書き、OctantVector が読む） |
| 契約3（OctantPath ↔ OctantCompass） | [mod-api.md](mod-api.md) | OctantPath（MOD）↔ OctantCompass |
| 契約4（OctantHarvest の収集結果 → OctantVector） | [generation-input.md](generation-input.md) | OctantHarvest の収集結果 → OctantVector の生成側 |
| 契約5（OctantHarvest → 配布先 → OctantCompass） | [distribution.md](distribution.md) | OctantHarvest（公開）↔ 配布先 ↔ OctantCompass |
| 契約6（つなぐ側 ↔ OctantCompass） | [launch.md](launch.md) | つなぐ側 ↔ OctantCompass |
| — | [external.md](external.md) | 外部依存（こちらでは決められないもの） |

## 契約の呼び方

契約を番号だけで呼ばず、番号のあとに何と何の取り決めかを括弧で書きます（2026-10-11）。呼び方は次の表だけに定め、ほかの文書とスキーマの `description` はこの表のとおりに書きます。

| 番号 | 呼び方 | コードの中の書き方 |
| --- | --- | --- |
| 1 | 契約1（OctantCompass・OctantHarvest → OctantVector） | `OctantCompass/OctantHarvest to OctantVector` |
| 1 の推薦側 | 契約1 推薦側（OctantCompass → OctantVector） | `OctantCompass to OctantVector` |
| 1 の生成側 | 契約1 生成側（OctantHarvest → OctantVector） | `OctantHarvest to OctantVector` |
| 2 | 契約2（DB 生成 ↔ 推薦コア） | `DB build to recommendation core` |
| 3 | 契約3（OctantPath ↔ OctantCompass） | `OctantPath to OctantCompass` |
| 4 | 契約4（OctantHarvest の収集結果 → OctantVector） | `OctantHarvest crawl to OctantVector` |
| 5 | 契約5（OctantHarvest → 配布先 → OctantCompass） | `OctantHarvest to OctantCompass` |
| 6 | 契約6（つなぐ側 ↔ OctantCompass） | `client to OctantCompass` |

- 矢印は呼ぶ側・書く側から、呼ばれる側・読む側へ向けます。両方が送り合う境界は ↔ にします。
- 同じ段落（表なら同じ行）で同じ契約を 2 度目に呼ぶときは、番号だけでかまいません。
- 「契約1〜4」のような範囲や「契約3・6」のような並びは、1 つずつ呼び方で書きます。
- 補足を足すときは同じ括弧の中に「。」で続けます（例: 契約3（OctantPath ↔ OctantCompass。MOD は観測できたものだけを送ってよい））。
- mermaid の図の矢印の名前は、矢印そのものが両端を示すので番号だけにします。
- 各リポジトリのコードのコメントと README は、記号を打たずに済むよう「コードの中の書き方」を使い、ファイルの中で最初に出てくるときだけ併記します（例: `contract 3 (OctantPath to OctantCompass)`、`契約3（OctantPath to OctantCompass）`）。画面に出る文字列は開発中の確認用なので併記しません（2026-10-11）。

## 契約の版と食い違いの知らせ方

部品は別々のリポジトリで別々に更新されるので、どの契約も版を持ち、受け取る側が使う前に確かめます。食い違いは黙って動き続けず、どの部品をどの版に上げればよいかが分かる形で知らせます（2026-10-07）。

| 契約 | 版を名乗る場所 | 確かめる側と、確かめるとき | 食い違ったとき |
| --- | --- | --- | --- |
| 契約1 推薦側（OctantCompass → OctantVector） | `octantvector.runtime.API_VERSION` | OctantCompass が、起動時に自分の対応する範囲か | OctantCompass は `/v1/health` を `degraded`（`reason: engine_incompatible`）にする |
| 契約1 生成側（OctantHarvest → OctantVector） | `octantvector.generation.API_VERSION` | OctantHarvest が、実行の前に自分の対応する範囲か | OctantHarvest は実行を止めて記録に残す |
| 契約2（DB 生成 ↔ 推薦コア） | 配布物のマニフェストの `schemaVersion` | OctantVector の `open_db` が読み込むとき。OctantCompass が更新する版を選ぶとき（契約5（OctantHarvest → 配布先 → OctantCompass）） | `VersionError`。OctantCompass は `degraded`（`reason: schema_unsupported`） |
| 契約3（OctantPath ↔ OctantCompass） | OctantCompass は `/v1/health` の `apiVersion`。MOD はすべての要求のヘッダ `OctantPath-Api-Version` | MOD は接続したときと `/v1/health` のたび。OctantCompass は要求のたび | [契約3（OctantPath ↔ OctantCompass）の版の食い違い](mod-api.md#版の食い違い) |
| 契約4（OctantHarvest の収集結果 → OctantVector） | カタログの `manifest.json` の `schema`、アーカイブの `archive_meta.json` の `format` | OctantVector の生成側の関数が、入力を読む前に | `VersionError` で止まる。OctantHarvest は実行の記録に残す |
| 契約5（OctantHarvest → 配布先 → OctantCompass） | 索引の `indexVersion` | OctantVector の `plan_update` | `VersionError`。OctantCompass は手元の DB を使い続け、更新できない理由を `/v1/health` に出す（`update.reason: index_unsupported`） |
| 契約6（つなぐ側 ↔ OctantCompass） | なし。ファイルも発見もなく、通信の形は契約3（OctantPath ↔ OctantCompass）の `apiVersion` で確かめる（[契約6](launch.md)） | — | — |

版の上げ方はどの契約も同じで、項目や値の追加はマイナー版、削除や意味の変更はメジャー版を上げます。受け取る側は、メジャー版が違えば使わず、マイナー版が新しければ知らない項目と値を無視して使います。契約1（OctantCompass・OctantHarvest → OctantVector）は、OctantVector のパッケージの版とは別に API の版を持ちます（[推薦側の版の付け方](engine-runtime.md#版の付け方)）。
