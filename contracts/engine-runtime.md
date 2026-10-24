# 契約1 推薦側（OctantCompass → OctantVector）: OctantVector の推薦側の関数 API

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。公開（リリース）の前は実装が先で、この文書とスキーマを後から合わせます。

版 1.0 · 境界: OctantCompass → OctantVector · 実装する側: OctantVector · 形の正本: [schemas/engine-runtime/](schemas/engine-runtime/) · 例: [examples/engine-runtime/](examples/engine-runtime/)

項目の形と意味はスキーマにだけ書き、この文書は項目をまたぐ振る舞いだけを書きます（[契約の決まり](README.md)）。関数の名前と引数の並びは、この文書の表が正本です。

OctantVector の推薦側は Python の関数の集まりで、OctantCompass が同じプロセスの中でライブラリとして呼びます。OctantVector はユーザーの状態の正本を持たず、推薦に要る履歴と数値を毎回引数で受け取ります。設定ファイルは読まず、通信もしません。中で作った好みと実力をプロセスの中でキャッシュするのは構いません（正本ではないため。憲法の原則 7）。何を推薦し何を返すかの決定と理由は[推薦の定義](../plans/recommendation-definition.md)にあります。OctantCompass と OctantVector の責任の分け方は[憲法の部品と契約の地図](../constitution.md#部品と契約の地図)にあります。

## 履歴の signal の扱い

OctantCompass は signal を選り分けずに、受け取ったままの粒度で渡します。どの signal を好みと実力の推定にどう使うかは OctantVector が決め、決まりは [OctantVector 法](../octantvector/law.md) 4.1・4.2 にあります。呼ぶ側が頼ってよいのは、観測としての意味だけです。各 signal の意味（`like_removed` が否定の印でないこと、`imported_play` の回数が何を含むかなど）は [event のスキーマ](schemas/common/event.schema.json)の `type` と各項目の `description` にあります。

## 公開する関数

| 関数 | 入力 | 出力 |
| --- | --- | --- |
| `open_db(path)` | DBのフォルダ | DB。中身の情報は `info()` で読める（[info.schema.json](schemas/engine-runtime/info.schema.json)）。ハッシュ・`schemaVersion` の検証に失敗したらエラー。署名は確かめない（[署名](distribution.md#署名)） |
| `recommend(db, history, request, params)` | 履歴、推薦の条件、数値 | 推薦の一覧 |
| `presets(db)` | DB | 手札の一覧。形は[契約3（OctantPath ↔ OctantCompass）の OpenAPI](mod-api.openapi.yaml) の `PresetsResponse` と同じ。DB のマニフェストの手札か、なければ OctantVector 同梱の既定の手札のうち、OctantVector と DB で使えるものだけ（[手札が使えるとき](#手札が使えるとき)） |
| `expand_preset(db, request)` | 推薦の条件（`preset` と `choices` を含んでよい） | `preset` を条件（`weights`・`narrow`・`difficulty`・`genre`・`params` の一部）に展開した条件。呼ぶ側が一緒に送った条件が優先。`preset` がなければ `choices` も含めてそのまま返す |
| `describe(db, history, params)` | 履歴、数値 | 表示用の要約。よく似ている軸は今は返さない（2026-10-12） |
| `plan_update(index, local_version)` | [契約5（OctantHarvest → 配布先 → OctantCompass）](distribution.md) の索引、手元の `dbVersion`（なければ空） | 取るファイルの一覧（全量か差分の鎖、ビューパック） |
| `apply_update(files, base, out, trust)` | 取ったファイル、手元の DB のフォルダ、書き出すフォルダ、署名の確かめ方（省けば同梱の鍵だけを信頼。[署名](distribution.md#署名)） | サイズと SHA-256 を確かめ、展開した各版の署名を照らし（署名がないか合わなければ `SignatureWarning` を出して続ける。[署名](distribution.md#署名)）、差分を当てた新しい DB のフォルダ。失敗したらエラーで、手元の DB は変えない |
| `import_archive(path, out, trust)` | 索引なしで手渡しされた全量の tar 1 つ（生成側の `pack` が書く。[契約5 の非公開（探求中）の扱い](distribution.md#非公開探求中の扱い)）、書き出すフォルダ、署名の確かめ方（`apply_update` と同じ） | 展開してマニフェストの SHA-256 を照らし、全量であることを確かめ、署名を `apply_update` と同じに照らした（合わなければ `SignatureWarning` を出して続ける）新しい DB のフォルダ。失敗したらエラーで、`out` には何も残さない |

引数と戻り値の項目の形と意味は、次のスキーマの `description` にあります。

| 引数か戻り値 | スキーマ |
| --- | --- |
| `info()` | [info.schema.json](schemas/engine-runtime/info.schema.json) |
| `history` | [history.schema.json](schemas/engine-runtime/history.schema.json)（要素は[契約3（OctantPath ↔ OctantCompass）](mod-api.md) の `events` と同じ [event](schemas/common/event.schema.json)） |
| `request` | [recommend.request.schema.json](schemas/engine-runtime/recommend.request.schema.json) |
| `params`（`recommend` と `describe`） | [params.schema.json](schemas/engine-runtime/params.schema.json)。キーごとの既定値の場所は `x-defaultIn` |
| `recommend` の戻り値 | [recommend.output.schema.json](schemas/engine-runtime/recommend.output.schema.json) |
| `describe` の戻り値 | [describe.output.schema.json](schemas/engine-runtime/describe.output.schema.json) |
| `plan_update` の `index` | [契約5（OctantHarvest → 配布先 → OctantCompass）の索引](distribution.md) |
| `apply_update` の `trust` | [契約5（OctantHarvest → 配布先 → OctantCompass）の署名](distribution.md#署名) |

理由を並べ替えに使わないこと、`score` を返さないこと、件数に足りないときの返し方は [recommend.output.schema.json](schemas/engine-runtime/recommend.output.schema.json) の `description` にあります。

- 同じ DB、同じ履歴、同じ条件からは同じ一覧を返します。そのため OctantCompass は、表示の直前でなくても前もって推薦を頼めます
- 難しさは 1 本の数値ではなく、譜面の特性の空間での、その人の得意な譜面からの距離です。距離への変換、選び方と絞り込みの手順は OctantVector の中の決めごとで、考え方は[推薦の難易度合わせ](../plans/difficulty-fit.md)にあります
- 履歴や `seed` が旧版の `hash` を指すときは、同じマップの現行版に置き換えて計算し、置き換えた組を一覧全体に記録します。譜面は現行版の同じ `characteristic` と `difficulty` に置き換えるので、作り直された譜面のことがあります。置き換えた組の形はスキーマの `replacement` にあります

プレイスタイル（[契約2（DB 生成 ↔ 推薦コア）](vector-db.md)）が違う譜面は、特徴の計算方法もユーザーの得意・不得意も違い得るので、同じものとして比べません。あるプレイスタイルのプレイ記録から作った実力を別のプレイスタイルの譜面に使うのは、OctantVector がそれでよいと確かめた場合だけです（憲法の原則 2）。

## エラーの種類

推薦側の関数が出すエラーは次の 6 種類です。呼ぶ側は種類で振る舞いを分け、メッセージの文面には頼りません。

| 種類 | いつ | 出す関数 |
| --- | --- | --- |
| `DBError` | DB が使えない（ハッシュ・`schemaVersion` の検証の失敗、中身の食い違い）、更新のファイルが索引と合わない、差分を当てると知らないものを失う（[契約2（DB 生成 ↔ 推薦コア）の互換性のルール](vector-db.md#互換性のルール)） | `open_db`、`apply_update`、`import_archive` |
| `VersionError` | 読めない版の印（[契約2（DB 生成 ↔ 推薦コア）](vector-db.md) の `schemaVersion`、[契約5（OctantHarvest → 配布先 → OctantCompass）](distribution.md) の `indexVersion`）。`DBError` の一種 | `open_db`、`plan_update` |
| `RequestError` | 要求が DB に合わない（ジャンルの語、狙いの名前） | `recommend` |
| `SeedNotInDBError` | `seed` のマップか譜面が DB にない（旧版として置き換えられる場合を除く）。`RequestError` の一種 | `recommend` |
| `SeedNotEmbeddedError` | `seed` の譜面は DB の目録にあるが、使えるビューのどれにもベクトルがない（比べる基準が作れない）。`SeedNotInDBError` の一種なので、これを知らない呼び側は「DB にない」として扱える | `recommend` |
| `UnknownPresetError` | `preset` が今の手札の一覧にない。`RequestError` の一種 | `expand_preset` |

これ以外の例外は想定外のもので、OctantVector の不具合か、契約に合わない引数です。6 つの種類は `octantvector.runtime` から import できます。

## 版の付け方

- 推薦側の API の版は `octantvector.runtime.API_VERSION`（`"1.0"` の形の文字列）で名乗る。OctantVector のパッケージの版（`octantvector.__version__`）とは別に上がり、API が変わらない実装の変更ではこの版は変わらない。上げ方と、OctantCompass が確かめて食い違いを知らせる方法は[契約の版と食い違いの知らせ方](README.md#契約の版と食い違いの知らせ方)のとおり（`params` のキーの追加もマイナー版）
- OctantCompass は起動時に、メジャー版が同じで、自分が使う機能のあるマイナー版以上かを確かめる
- OctantCompass が import するのは `octantvector.runtime` だけ
- OctantVector のパッケージはセマンティックバージョニングで版を付け、版ごとに OctantVector のリポジトリに git のタグ（`v0.2.1` の形）を付ける。OctantCompass は OctantVector をこのタグから入れる。PyPI には今は出さない（2026-10-06 決定）

## 手札が使えるとき

手札は、契約3（OctantPath ↔ OctantCompass）の `Preset`（[OpenAPI](mod-api.openapi.yaml)）の項目に、扱い方の名前 `handling` とそのつまみ `knobs` を足したものです。扱い方の中身（距離の取り方、絞る件数など）は OctantVector のコードで、手札には書きません（[プリセットの 8 節](../plans/presets.md#8-手札の定義を配布-db-に移す2026-10-10)）。

表示名（`label`・`group`・`hint`、入力と選択肢の `label`）の形は OpenAPI の `LocalizedText` で、OctantVector は形を確かめてそのまま返します。`label` が空なら手札を外し、`group`・`hint` の形が違えばその項目だけ外し、選択肢の `label` の形が違えばその選択肢だけ外します。既定の手札は英語と日本語を持ちます（OctantVector 0.3.19、[プリセットの 9 節](../plans/presets.md#9-表示名の言語2026-10-11)）。

| 扱い方 | つまみ | 展開した条件 |
| --- | --- | --- |
| `near` | `weights`、`difficulty`、`genre`、`params`（どれも任意） | 同じ名前の条件。起点か履歴のまわりを重みで並べる |
| `narrow_then_rank` | `narrow`（必須）、`rank`（必須）、`difficulty`、`params` | `narrow` と `weights`（= `rank`）。`narrow` のビューで近いマップに絞ってから、`rank` のビューで並べる |

手札が一覧に出るのは、次をすべて満たすときだけです。何が要るかはつまみから OctantVector が判断し、手札の書き手の申告には頼りません（2026-10-10）。満たさない手札はその手札だけ外し、ほかの手札と DB は使います。

- 扱い方を OctantVector が知っていて、つまみがすべてその扱い方のもので、値が受け付けられる（`params` のキーは params のスキーマにあるもの、`difficulty` は狙いの名前か見込み）
- つまみが名指しするビューとジャンルの語がすべて DB にある

重み（`weights`、`narrow`、`rank`）のキーは、ビューの id か id@version です。役割名（`music` など）は表示のための札で、重みのキーには使えません。どのビューを DB に入れるかは DB を作る人が決めるので、手札はどのビューを使うかを自分で名指しします（2026-10-14、OctantVector 0.4.0。`common/hands.py` の `view_keys`）。版を付けない id は DB にあるその id のビュー（版が 2 つあればその両方で等分）を指すので、ビューの版が上がっても手札は外れません（OctantVector 0.3.17。2026-10-10）。例: `{"mert_v1_95m": 0.7, "clap_htsat_unfused": 0.3}`、`{"chart_patterns": 1}`。
- 入力がすべて OctantVector の埋められるもの。`seed` か、`name` が扱い方のつまみ（`genre`、`difficulty`）で選択肢が残る `choice`。`genre` の選択肢を省くと DB の語を使う。DB で使えない選択肢は外す。知らない種類の入力は、`optional` なら無視し、そうでなければその手札を外す

DB のマニフェストに手札があれば、それで既定の手札を全部置き換えます。同じ `id` が 2 つあれば先のものを使います。OctantVector 同梱の既定の手札は「すべて」（`all`。重みなし）の 1 枚だけです。ほかの手札はビューを名指しするので、DB を作る側が手札として配ります（OctantHarvest の `presets/official.json`。2026-10-14、OctantVector 0.4.0。[プリセットの 12 節](../plans/presets.md#12-手札はビューを名指しする2026-10-14)）。

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 1.0 | 2026-10-09 | 最初の版。パッケージの版から API の版を切り離した（OctantVector 0.3.8 と同じ API） |
| 1.0 | 2026-10-10 | 探求中の形の変更なので版を上げない（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)。以下同じ）。`presets`、`expand_preset`、`SeedNotEmbeddedError`、`UnknownPresetError`、要求の `narrow`、数値の `narrowTopMaps`、重みのキーのビューの id（版なし）を足した（決定） |
| 1.0 | 2026-10-12 | 実装の今の形を記録した（決定）。`count` は呼ぶ側が必ず送る、置き換えの組の形、狙いの `clearChance`、`describe` はよく似ている軸を今は返さない、など。`params` に `mapsPerArtist`、`info()` のビューに `kind` を足した（決定） |
| 1.0 | 2026-10-14 | 重みのキーをビューの id か id@version だけにした。既定の手札を `all` の 1 枚にした。`expand_preset` は `preset` のない要求を `choices` ごと返す（決定、OctantVector 0.4.0） |
| 1.0 | 2026-10-15 | `describe` の `weakDirections` の要素を `{feature, direction, weight}` にし、`params` に `directionShrinkPlays` を足した。`recommend` は挑戦の狙いで目標のマップを既知の除外から外す（OctantVector 0.5.0） |
| 1.0 | 2026-10-17 | 手渡しされた全量の tar を取り込む `import_archive` を足した（決定、OctantVector 0.6.0） |
| 1.0 | 2026-10-18 | `info()` に DB 全体の `notice` と、ビューごとの `credits` を足した（決定、OctantVector 0.7.0） |
