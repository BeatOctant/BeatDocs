# 契約2（DB 生成 ↔ 推薦コア）: ベクトルDB形式

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。公開（リリース）の前は実装が先で、この文書を後から合わせます。

版 1.1 · 境界: OctantVector の生成側（書く）↔ OctantVector の推薦側（読む）。配布物として OctantHarvest と OctantCompass の間を渡る · 実装する側: OctantVector

1つの配布物は、マニフェスト（JSON）、メタ情報の表、ビューごとのファイル（ベクトルか関係）、校正ファイルで構成します。入る行は配布用プール（全件。upvote の下限なし）の公開中の版だけで、旧版は入れません。コアはマニフェストの `schemaVersion` で、読めるかどうかを判断します。

## 配布物の構成

| ファイル | 中身 | 行の単位 |
| --- | --- | --- |
| `manifest.json` | 版、ビューの一覧（ビューごとのクレジットを含む）、DB 全体の利用条件とクレジット（`notice`）、各ファイルのハッシュ | — |
| `maps.parquet` | 版単位のメタ情報（`hash`、アーティスト、マッパー、長さ、公開日） | 1行 = 1版 |
| `charts.parquet` | 譜面単位のメタ情報（`hash`、`characteristic`、`difficulty`、NPS、NJS、Pass、Tech、`play_style`） | 1行 = 1譜面 |
| `superseded.parquet` | 旧版の `hash` と、同じマップの現行版の `hash` の対応 | 1行 = 1旧版 |
| `views/<id@version>.npy` | ビューのベクトル（校正で正規化した float16） | そのビューがある行だけ |
| `views/<id@version>.rows.npy` | そのビューがある行の番号（`maps` か `charts` の行） | — |
| `views/<id@version>.members.parquet` | 関係のビューだけ。行が属するもの（`row`: `maps` の行の番号、`member`: 属するものの ID。1 つの行が 2 つ以上に属してよい） | 1行 = 1組 |
| `views/<id@version>.pairs.parquet` | 関係のビューだけ。属するものどうしの点（`a`、`b`、`score`: 0〜1 の float32。向きあり） | 1行 = 1組 |
| `calibration/<calibrationId>.json` | 正規化に使った平均と標準偏差。差分では校正が変わったときだけ入る | — |
| `changed.parquet` | 差分だけ。追加か差し替えをした版の `hash` | 1行 = 1版 |
| `deleted.parquet` | 差分だけ。消えた版の `hash` | 1行 = 1版 |

音源とメタ情報から作るビューは版単位（`maps`）、譜面から作るビューは譜面単位（`charts`）の行に対応します。譜面から作った特徴を版単位の行に入れることはしません（譜面ごとの違いが消えるため）。`play_style` は譜面のプレイスタイルで、当面は `characteristic` と同じ値です。`characteristic` だけで区別できないプレイスタイルが見つかったら、判定を OctantVector の中で足し、列の形は変えません。ジャンルの語（[推薦の定義](../plans/recommendation-definition.md)の Q2。最大 10 語程度）は、`role` が `genre` の版単位のビューとして持ちます。ベクトルの各次元が 1 つの語への近さで、語の並びはそのビューの `genres` に書きます。語の一覧と近さの測り方は未決です。音声が壊れたマップや埋め戻し中のビューでは全行がそろわないので、ビューごとに「ある行」の一覧を持ちます。旧版はベクトルを持たず、現行版に置き換えるための対応（`superseded.parquet`）だけを持ちます。Pass と Tech はスイングシミュレーションで計算した値で、計算できなかった譜面は空にします。どの版のシミュレーションで計算したかは、列ごとにマニフェストの `chartMetrics` に書きます。いまの OctantVector はまだ計算していないので、2 つの列は空で、`chartMetrics` は `{}` です（OctantVector の [dbrelease.py](https://github.com/BeatOctant/OctantVector/blob/main/src/octantvector/generation/dbrelease.py)）。曲名は推薦に使わない方針なので、DBには入れません（表示は MOD が BeatSaver から取ります）。

## ビューの種類

ビューは、マニフェストの `kind` で 2 種類に分かれます（2026-10-12 決定）。`kind` を省いたビューはベクトルのビューです。

| 種類 | 持つもの | 起点との近さ | 例 |
| --- | --- | --- | --- |
| `vector` | 行ごとのベクトル（`file`、`rowsFile`） | cosine | CLAP、MERT、譜面 |
| `relation` | 行が属するもの（`membersFile`）と、属するものどうしの点（`pairsFile`） | 起点と候補が同じものに属せば 1。そうでなければ両方の属するものの組の点の最大（`pairs` の両向きの大きい方）。表にない組は 0 | 近いアーティスト（id `listenbrainz_artists@<取得日>`、役割 `artist`）、同じ譜面の作者（id `beatsaver_mappers@1`、役割 `mapper`。`pairs` は空） |

- 関係のビューも、ほかのビューと同じ重みつきの平均に入ります。持っていない行は 0 として数え、重みを割り直しません（[OctantVector 法](../octantvector/law.md) 3.1）。関係のビューを「持っている」行は、`membersFile` にある行です
- 起点が複数のとき（好意的なマップから推薦するとき）は、起点ごとの点の平均を使います。ベクトルのビューが起点の平均のベクトルを使うのに当たります
- 関係のビューは校正の対象ではなく、`calibrationId` によりません。行の単位は今は `maps` だけです
- 関係のビューは自分のファイルとマニフェストの欄だけで閉じているので、配布 DB を 2 つ以上重ねて使えるようになったら（[open.md の契約の未決点](../open.md#契約の未決点)）、本体の DB から追加の DB に移せます。そのときは `row` を `hash` に替える（推測）

## 役割名

ビューの `role` は、そのビューが何を表すかの名前（札）です。推薦の要求と手札の重み（`weights`・`narrow`・`rank`）のキーはビューの id か id@version で、役割名では付けられません（2026-10-14、OctantVector 0.4.0。[契約1（OctantCompass・OctantHarvest → OctantVector）の手札が使えるとき](engine-runtime.md#手札が使えるとき)）。どの役割のビューが DB にあるかは、OctantCompass が `/v1/health` の `db.roles` で知らせ（[契約3（OctantPath ↔ OctantCompass）](mod-api.md)）、OctantPath は推薦の理由のビューを役割の名前で出すのに使います。役割は OctantVector 法 3.4 の同じ曲の見分け（`music`）、アーティストの上限（`artist`）、ジャンルの語（`genre`）、`weights` を省いたときの既定にも使います。

| 役割名 | 表すもの | 行 | 推薦での使い方 |
| --- | --- | --- | --- |
| `music` | 曲の音（音源から作る。`clap_htsat_unfused`、`mert_v1_95m`） | `maps` | 似ている軸。同じ曲の見分け（OctantVector 法 3.4）にも使う |
| `vocal` | 歌声（Demucs で分けた歌声の音から作る。`vocal_clap_htsat_unfused`、`vocal_mert_v1_95m`、`vocal_wavlm_sv`。OctantVectorPlugins） | `maps` | 似ている軸。歌声のない曲はベクトルを持たない |
| `chart` | 譜面（配置、流れ、密度など、譜面から作る） | `charts` | 似ている軸。同じプレイスタイルの譜面どうしで比べる |
| `meta` | BeatSaver のメタ情報（タグなど） | `maps` | 似ている軸 |
| `artist` | 近いアーティスト（関係のビュー `listenbrainz_artists@<取得日>`。属するものは MusicBrainz のアーティスト ID、点は ListenBrainz の似たアーティストを ID ごとに最大 1 になるよう割った値。元のファイルは[契約4（OctantHarvest の収集結果 → OctantVector）](generation-input.md)） | `maps` | 似ている軸。同じアーティストの上限（[OctantVector 法](../octantvector/law.md) 3.4）にも使う |
| `genre` | ジャンルの語への近さ（各次元が 1 つの語。語の並びはビューの `genres`。今は `clap_concepts` の 58 語） | `maps` | 似ている軸には使わない。推薦の要求の `genre` で絞り込む |
| `language` | 歌の言語（`whisper_language`。Whisper で判定した、歌のある箇所の言語の割合で、`norm` は `none`。OctantVectorPlugins） | `maps` | 似ている軸（同じ 1 つの言語なら 1、違えば 0、2 言語の曲はその間）。言語がはっきりしない曲（歌のない曲など）はベクトルを持たない |
| `cover` | カバー画像（`siglip_cover`。SigLIP の画像の埋め込みで、`norm` は `none`。OctantVectorPlugins） | `maps` | 似ている軸。同じ絵のカバーどうしは 1 近く。画像の中の文字から名前の近さが間接的に入り得る（[open.md](../open.md) V10、法 3.2） |
| `mapper` | 譜面の作者（関係のビュー `beatsaver_mappers@1`。属するものは BeatSaver のアカウント ID（`beatsaver:<id>`。投稿者と、カタログにあれば共作者）。名前は使わない） | `maps` | 似ている軸（同じアカウントの譜面なら 1） |

- 役割名を足すのはマイナー版、意味を変えるか消すのはメジャー版です。知らない役割名のビューは、`weights` でビューを名指しされたときだけ似ている軸に使います
- `weights` を省いたときに使うのは、DB にある `music`、`chart`、`meta` のビューです（各役割に同じ重み。役割の中のビューで等分。OctantVector `runtime/recommend.py` の `TASTE_ROLES`）

## マニフェストの例

値は形を示すための例です。

```json
{
  "schemaVersion": "1.1",
  "kind": "full",
  "dbVersion": "2026.10.02",
  "builtAt": "2026-10-02T00:00:00Z",
  "baseDbVersion": null,
  "diffsSinceFull": 0,
  "calibrationId": "<校正 ID>",
  "calibrationFile": "calibration/<校正 ID>.json",
  "counts": { "maps": 0, "charts": 0, "superseded": 0 },
  "views": {
    "<id@version>": {
      "role": "music",
      "file": "views/<id@version>.npy",
      "rowsFile": "views/<id@version>.rows.npy",
      "rows": "maps",
      "dim": 0,
      "dtype": "float16",
      "norm": "zscore",
      "fingerprint": "<指紋>",
      "sources": [],
      "credits": ["CLAP (LAION), https://github.com/LAION-AI/CLAP, model laion/clap-htsat-unfused, Apache-2.0"]
    },
    "listenbrainz_artists@<取得日>": {
      "kind": "relation",
      "role": "artist",
      "membersFile": "views/listenbrainz_artists@<取得日>.members.parquet",
      "pairsFile": "views/listenbrainz_artists@<取得日>.pairs.parquet",
      "rows": "maps",
      "source": "listenbrainz:<アルゴリズム>",
      "fetchedAt": "2026-10-12T00:00:00Z",
      "perMember": 30,
      "fingerprint": "<指紋>",
      "sources": [],
      "credits": ["MusicBrainz artist IDs, https://musicbrainz.org/, core data under CC0", "ListenBrainz similar artists, …"]
    }
  },
  "chartMetrics": {},
  "presets": [
    { "id": "chart_genre", "group": "譜面", "label": "曲調も近いマップ", "inputs": [{ "kind": "seed" }],
      "handling": "narrow_then_rank", "knobs": { "narrow": { "clap_htsat_unfused": 0.5, "mert_v1_95m": 0.5 }, "rank": { "chart_patterns": 1 } } }
  ],
  "notice": "# BeatOctant 配布 DB の利用条件とクレジット\n…",
  "files": { "maps.parquet": "sha256:<ハッシュ>" }
}
```

- `kind` は `full`（全量）か `diff`（差分）です。`diffsSinceFull` は、最後に公開した全量から差分をいくつ当ててできた中身かで、公開した全量では 0 です。`calibrationFile` は校正ファイルの場所です。ビューの `norm` は作ったときの正規化のしかたです（2026-10-12）。`center`（平均を引いて L2）、`zscore`（標準化して L2）、`none`（L2 だけ。one-hot の言語や画像の埋め込みの cos をそのまま使うため。2026-10-20）があります
- 差分のマニフェストでは、`counts` が `added`、`replaced`、`deleted`、`superseded` の数になり、ビューごとに `change`（`added` はビューの追加で全部の行を持つ、`rows` は変わった行だけ）と、同じエンコーダの別の版を置き換えるときの `replaces` を持ちます。消したビューは `removedViews` に並べます。`calibrationFile` は校正が変わったときだけ持ちます（2026-10-12）
- 関係のビューの `source` は元データとその作り方です。外から取ったビューは `fetchedAt`（取得した時刻）を、組（`pairs`）を持つビューは `perMember`（属するもの 1 つあたりに残す組の数の上限。点の高い順）を持ちます。カタログから作る `beatsaver_mappers@1` はどちらも持ちません
- `presets` は任意で、推薦の手札の配列です。形と、どの手札が使えるかは[契約1（OctantCompass・OctantHarvest → OctantVector）の手札が使えるとき](engine-runtime.md#手札が使えるとき)にあります。書くのは OctantVector の `release` だけです（[契約1 の生成側](engine-generation.md)）。マニフェストは署名の対象なので、手札も署名で守られます
- 手札の表示名は、文字列か `{言語: 文字列}` で書けます（[契約1（OctantCompass・OctantHarvest → OctantVector）の手札が使えるとき](engine-runtime.md#手札が使えるとき)）。公式の手札は英語と日本語を持ちます（OctantHarvest の `presets/official.json`）
- 差分のマニフェストは、手札の配列を全部持ちます（なければ null）。差分を当てた全量の手札はそれになります。手札だけを替えた版は、行の変わらない差分になります
- `notice` は任意で、DB 全体の利用条件とクレジットを 1 つの Markdown の文字列で持ちます（公式の DB では OctantHarvest の `DB-NOTICE.md`）。書くのは OctantVector の `release` だけで、差分のマニフェストも全部持ちます（なければ null）。マニフェストは署名の対象なので、`notice` も署名で守られます（2026-10-18）
- ビューの `credits` は任意で、そのビューが負うクレジット（モデル、移植したコード、データの出所と条件）を文字列の配列で持ちます。OctantVector が、エンコーダの宣言（ボーカルの分離と元のビューの分を含む）から書きます。ビューと一緒に動くので、追加パックや他の作者の DB でも、ビューの出所が一緒に届きます。定義（`fingerprint`）には入らず、変えてもビューの計算し直しは起きません。読む側は文字として扱い、HTML として描きません（署名の合わない DB も警告つきで読めるため。[契約5 の署名](distribution.md#署名)）（2026-10-18）

## 互換性のルール

- `schemaVersion` のメジャー版がコアの対応版と違う場合、コアの `open_db` はエラーを返し、OctantCompass は `/v1/health` で `degraded` を返す
- マイナー版が新しい場合、知らない項目や視点は無視して読む
- 差分を当てるときは、知らない列（`maps.parquet`、`charts.parquet`）、マニフェストの欄、ビューごとの欄を落とさずに持ち越す。「前の全量 + 差分」が新しい全量と同じ中身になるため（[OctantVector 法 2.4](../octantvector/law.md)）。持ち越せないもの（行の単位を知らないビュー、知らないファイル、`superseded.parquet` の知らない列、前の全量にだけある知らない欄、前の全量と差分で違う知らない列）があれば、差分を当てずに `DBError` にし、呼び側はその版の全量を取る。当ててできた全量の `schemaVersion` は、自分の版と差分の版の新しい方にする
- 類似度は、同じ `id@version` で同じ `calibrationId` のベクトル同士でだけ計算する。譜面のビューでは、さらに同じ `play_style` の譜面同士でだけ計算する。同じ役割（`role`）に複数のビューを並べられる

## 差分更新

- 差分は `baseDbVersion` を持ち、追加された行、差し替えた行、削除された `hash` を含む。差分は鎖としてつなぐ
- モデルを足したときや版を上げたときは、そのビューだけの追加パックか差し替えパックを配る
- 関係のビューは行ごとの差分を持たない。差分ごとに、残る関係のビューを全部 `change: added` で丸ごと入れる（小さいため）。同じ id の別の版に替わるときは `replaces` を持つ。`beatsaver_mappers@1` は版を上げずにリリースごとにカタログから作り直す
- 全量が必要なのは校正をやり直したときと、正規化のしかたを変えたとき。校正は、ずれが設定の閾値を超えたときだけ次の全量でやり直す。校正ファイルは任意の `normalisation`（作ったときの正規化の版。ないときは 1）を持ち、版が違う校正どうしは差分にしない
- 差分のマニフェストは、全量のマニフェストの欄（`chartMetrics` を含む）をすべて持つ。全量と差分で意味の違う欄（`kind`、`baseDbVersion`、`counts`、ビューの `change` など）は除く
- 前の版が生成側の知らないものを持つときは、差分を作らず全量にする
- 全量は設定の数の差分ごとにも作り、「全量」と「前の全量 + 差分」は同じ中身になる

## 検証

- マニフェストに全ファイルの SHA-256 を書き、コアは読み込み前に照合する
- マニフェスト自体の署名は配布の決まりで、[契約5（OctantHarvest → 配布先 → OctantCompass）の署名](distribution.md#署名)にある
- 検索用の索引は配布せず、コアが初回読み込み時に作る（索引ライブラリの版に配布物を依存させないため）

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 1.0 | — | 最初の版 |
| 1.1 | — | `charts.parquet` の `play_style` 列と、譜面単位（`charts`）のビューを足した |
| 1.1 | 2026-10-08 | 役割名（`role`）の意味を書いた。形は変わらない（決定） |
| 1.1 | 2026-10-09 | contracts.md から分けた。中身は変わらない |
| 1.1 | 2026-10-10 | 探求中の形の変更なので版を上げない（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)。以下同じ）。マニフェストに任意の `presets` を足した（決定、OctantVector 0.3.11） |
| 1.1 | 2026-10-11 | 差分で知らないものを持ち越すか断る決まり、差分のマニフェストが持つ欄、校正ファイルの任意の `normalisation` を書いた（決定、OctantVector 0.3.23） |
| 1.1 | 2026-10-12 | [ビューの種類](#ビューの種類)（`vector` と `relation`）、関係のビューのファイルと欄、役割名 `artist` を足した（決定、OctantVector 0.3.26）。マニフェストの例と構成の表に、コードが書く項目とファイルを足した（決定） |
| 1.1 | 2026-10-14 | 役割名を札にし、重みはビューの id で書くことにした（決定、OctantVector 0.4.0）。役割名に `vocal` を足した。形は変わらない |
| 1.1 | 2026-10-18 | マニフェストに任意の `notice`（DB 全体の利用条件とクレジット）、ビューに任意の `credits` を足した（決定、OctantVector 0.7.0） |
| 1.1 | 2026-10-20 | 役割名に `language`、`cover`、`mapper` を、関係のビューに `beatsaver_mappers@1` を、`norm` に `none` を足した。形は変わらない（決定、OctantVector 0.8.0） |
