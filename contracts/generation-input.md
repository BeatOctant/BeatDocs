# 契約4（OctantHarvest の収集結果 → OctantVector）: 生成の入力形式

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。公開（リリース）の前は実装が先で、この文書を後から合わせます。

版: 下の 2 つの印 · 境界: OctantHarvest の収集結果（書く）→ OctantVector の生成側（読む） · 実装する側: OctantHarvest と OctantVector

版は、カタログの `manifest.json` の `schema`（`octantharvest-beatsaver-catalogue-capture/v1`）と、アーカイブの `archive_meta.json` の `format`（`beatmap-music-identity-beatsaver-archive-v2`）で名乗ります。契約4（OctantHarvest の収集結果 → OctantVector）は番号の版を持たず、この 2 つの印で版を表します。

OctantVector の生成側は、OctantHarvest が収集して書いた「マップのアーカイブ」と「カタログのスナップショット」をそのまま読みます（2026-10-05 決定。V3 の A）。収集の道具は、開発用の PC にある既存の 2 つのスクリプト（アーカイブのダウンローダーとカタログの取得）を OctantHarvest に取り込んだものです。OctantVector は収集の方法を知りません。

| 項目 | 形 |
| --- | --- |
| マップの zip | アーカイブのフォルダの `maps/<hash の先頭 2 文字>/<hash>.zip`。`hash` は BeatSaver の版の hash で、中身は BeatSaver が配る zip のまま（Info.dat と各難易度のファイル、音源）。OctantVector は読むだけで書き込まない |
| ダウンロードの記録 | アーカイブのフォルダの `download.journal.jsonl`。1 行 1 件の JSON で、取得と検証が済んだ zip は `committed` の行に `hash` と `commit_seq`（ディスクに書いた順番）を持つ。OctantVector は `committed` の行だけを使い、`commit_seq` の順に読む |
| カタログ | `catalogue.jsonl.gz`。1 行 1 マップで、BeatSaver API のマップの JSON をそのまま入れたもの。差分の取得では前の取得の行を持ち越し、その後に更新されたマップだけを取り直す。`stats` の `upvotes`・`downvotes`・`score` は `GET /vote` の値に置き換え、ほかの `stats`（`plays` など）はその行を最後に取ったときの値（OctantHarvest #33）（`id`、`metadata`、`stats`、`tags`、`versions[]` の `hash`・`state`・`createdAt`・`diffs[]` の `characteristic`・`difficulty`・`nps`・`njs` など、削除や旧版の情報）。項目の意味は BeatSaver API に従う（外部依存） |
| マップのアーティスト ID（任意） | `map_artists.jsonl.gz`。1 行 1 版で `{hash, mbids}`（MusicBrainz のアーティスト ID の配列。ID が付かなかった版は行を持たない）。名前の分け方と照合は OctantHarvest の `octantharvest artists`（全体に ID が付けば全体の ID、なければ全部の部分に ID が付いたときだけ部分の ID）。名前の文字列は渡さない（[OctantVector 法](../octantvector/law.md) 3.2） |
| 似たアーティスト（任意） | `similar_artists.jsonl.gz`。1 行 1 ID で `{mbid, similar: [[mbid, score], …]}`。点は ListenBrainz の点のまま。ファイルの 1 行目は `{algorithm, fetchedAt}` の見出し。近所のない ID は `similar` が空 |
| 曲名 | カタログには入るが、OctantVector は表示と記録の照合にだけ使い、類似度には使わない（[OctantVector 法](../octantvector/law.md) 3.2） |
| 再現性 | 同じアーカイブ、同じカタログ、同じ設定からは同じ DB ができる。OctantVector は zip を最初に読んだときの SHA-256 を台帳に記録し、同じ hash で中身の違う zip は使わない |

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 上の 2 つの印 | 2026-10-09 | contracts.md から分けた。中身は変わらない |
| 上の 2 つの印 | 2026-10-12 | 探求中の形の変更なので印を変えない（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)。以下同じ）。任意の入力として、マップのアーティスト ID と似たアーティストの 2 つのファイルを足した（決定） |
| 上の 2 つの印 | 2026-10-16 | カタログを差分でも作るようにし、`manifest.json` に `base`・`votesSince`・`source.votes` を足した（OctantHarvest #33） |
