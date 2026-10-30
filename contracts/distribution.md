# 契約5（OctantHarvest → 配布先 → OctantCompass）: DBの配布と更新

> 固さ: 配布（何を、だれの承認と署名で出すか）は固める核、索引とファイルの形は後から記録する層です（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。

版 1.1 · 境界: OctantHarvest（公開）↔ 配布先 ↔ OctantCompass · 実装する側: OctantVector（索引の形と読み方）と OctantHarvest（置き場所と承認）

配布先に索引ファイルを1つ置き、OctantCompass はそれだけを見て更新を判断します。配布先を変えても、索引の形が同じなら OctantCompass はそのまま動きます。

| 項目 | 案 |
| --- | --- |
| 索引 | 索引の形の版（`indexVersion`）を持つ。最新の全量と、それ以降の差分の鎖を並べる。版ごとに `dbVersion`、`schemaVersion`、`calibrationId`、全量か差分のファイル（URL、サイズ、SHA-256）。ビューパック（ビューの追加）は差分の一種で、差分として載る。ファイルの `url` は null でもよく、そのときは索引と同じ場所からの相対の場所で取る（開発用の索引は URL を持たない）。版ごとの `signature` の項目は使わず null（署名は版の中の `manifest.sig`）（2026-10-12） |
| 公開の承認 | 全量と差分（ビューパックを含む）は、公開前に毎回メンテナーが承認する。承認していないものは索引に載せない。公開（Dev 版）では索引を使わないので、承認は手渡しする版の承認と署名で行う（[非公開（探求中）の扱い](#非公開探求中の扱い)の最後の項目） |
| 更新の判断 | OctantCompass は索引を取得し、自分が読める `schemaVersion` のうち最新の版を選ぶ |
| 差分の使用 | 手元の版から差分の鎖をたどれれば差分を当て、たどれなければ全量を取る |
| 分割 | 1ファイルの上限（GitHub Releases なら 2GB）を超える場合は分割し、索引に順序を書く |
| 取得の決まり | 索引と部品は https の URL からだけ取る。ほかのスキーム（http、file、ローカルのパス）と、https の外への転送は断る（2026-10-16。索引は署名されず部品の SHA-256 を持つので、途中で索引ごと差し替えられないようにするため。OctantCompass #40）。索引の大きさは受け取る側の設定の上限（OctantCompass の `index_max_megabytes`）まで。部品は索引に書かれた大きさまでしか読まず、大きさのない部品は断る（大きさは実質必須）。部品の合計が取得先の空き容量に入らなければ、何も取る前に断る。User-Agent はどの部品か分かるもの（OctantCompass は `OctantCompass/<版> ( https://bsky.app/profile/beatoctant.bsky.social )`）（OctantCompass #38） |
| 失敗時 | ダウンロードか検証に失敗したら、手元の版を使い続ける |
| `dbVersion` の形 | 1 つのパス要素（フォルダ名。`/`・`\\`・`..`・先頭の `.` を含まず、100 文字以内）。`plan_update` は索引の `dbVersion` がこれに合わなければ `DBError` にし、OctantCompass も同じ確かめをしてから手元のフォルダ名に使う（2026-10-14、OctantCompass #35。索引を書き換えられてもデータフォルダの外に書かないため） |
| 更新の反映 | [契約1（OctantCompass・OctantHarvest → OctantVector）](engine-runtime.md) の `plan_update` と `apply_update` で、新しい版を別のフォルダに用意し、検証が通ってから切り替える。OctantCompass は配布物のファイルを自分で組み立てない |

## 署名

2026-10-08 決定。配る版が、承認した人の作ったものから変わっていないことを確かめるためのものです。署名は作者を示すもので、合わない版を止めはしない（2026-10-11 決定）。DB はデータだけで、読んでもコードは動かない（手札もビューも、OctantVector が内蔵する扱い方を名前で選ぶだけ）。壊れたファイルは、索引の SHA-256 との照合で弾く

- 署名するのは、配る方（全量か差分）の版のフォルダの `manifest.json` だけ。マニフェストが全ファイルの SHA-256 を持つので、これで版の中身全体が守られる
- 署名する内容は、`manifest.json` を JSON として読み、JCS（RFC 8785）で正規化したバイト列。ファイルの改行や字下げは署名に関係しない
- 方式は Ed25519。署名は同じフォルダの `manifest.sig` に置く。`manifest.sig` は JSON で、`algorithm`（`"Ed25519"`）、`keyId`（公開鍵 32 バイトの SHA-256 の 16 進の先頭 16 文字）、`signature`（64 バイトの署名の base64）を持つ。`manifest.sig` はマニフェストの `files` には載せない
- 署名するのは公開を承認するメンテナーで、当面はメンテナーの鍵 1 つ。秘密鍵はメンテナーの PC にだけ置き、どのリポジトリにも入れない。OctantHarvest は承認のときに、設定で指定した秘密鍵で OctantVector の `sign` を呼ぶ。`publish` では、その鍵の公開鍵（設定の `signing.publicKey`）を `build_index` の `trusted_keys` に渡す（OctantHarvest #33）。チームで品質を確かめる形にするときの鍵の持ち方は、そのときに決める
- OctantVector は、受け入れる公開鍵の一覧を自分のリポジトリに同梱する。鍵を足すことと外すことは、OctantVector のパッケージの版を上げる変更（契約1（OctantCompass・OctantHarvest → OctantVector）の API の版は変わらない）。いま同梱しているのはメンテナーの鍵（`keyId` `10c26904c2f7bb19`）1 つ
- 確かめるのは、配布物を外から受け取るところ。`apply_update` は展開した各版の `manifest.sig` を同梱の公開鍵と照らし、ない、形が違う、知らない鍵、合わないときは、警告（`SignatureWarning`。Python の warning）を出してその版を使う。`DBError` にはしない。OctantCompass はその版を使い、警告を管理画面とログ、`db update` の出力に出す（OctantCompass #38）。誰の署名かは OctantVector の `signing.inspect` で読める（契約の外）。差分を当ててできた全量は手元で作ったものなので署名を持たず、`open_db` は署名を確かめない。公開（Dev 版）でも警告のままにし、進みや規模が一定に達したら、信頼する鍵の署名が合わない版を使わない形に変える（2026-10-21 決定、時期は未定）
- 開発中は、`apply_update` の `trust` で確かめ方を変えられる。`trust` は `keys`（同梱の鍵に足して信頼する公開鍵。`keyId` から公開鍵の base64 への対応）と `allowUnsigned`（真なら署名のない版で警告を出さない。署名がある版はそれでも照らす）を持つ。どちらも既定は空と偽で、OctantCompass は自分の設定から渡す（[OctantCompass 法の 6.1](../octantcompass/law.md#6-db-の更新)）。生成側の `build_index` も、索引に載せる版の署名を同じように確かめる。`trusted_keys` で同梱の鍵に足す鍵を受け取り（OctantHarvest の `signing.publicKey`）、`allow_unsigned` で署名のない版も載せられる（OctantHarvest の設定。2026-10-15、OctantVector #53）
- 索引（`index.json`）自体には署名しない。索引が書き換えられても、取ったファイルの `manifest.sig` が合わなければ警告が出る

## 非公開（探求中）の扱い

2026-10-10 決定。BeatOctant の段階は「非公開（探求中）」→「公開（Dev 版）」→「公開（リリース）」で、今は公開（Dev 版）です（2026-10-24）。非公開（探求中）では DB をメンテナー以外に渡さないので、この契約の手続き（公開の承認、署名、索引、配布先へのアップロード）を行わない。目安は「実装と試験に困らないこと」だけです。開発用の PC で作る版は、公開（Dev 版）になってからも次の 4 つの項目のとおりに扱い、外に渡す版だけを最後の項目のとおりに扱います。

- 版は OctantVector の `release`（開発用には `octantvector release`、または OctantHarvest の毎日の実行）で作り、そのフォルダを OctantCompass がローカルのフォルダとして使う（[OctantCompass 法の 6.4](../octantcompass/law.md#6-db-の更新)の「ローカルのフォルダを指定して切り替えるコマンド」）。この道は署名を確かめる `apply_update` を通らず、`open_db` は署名を確かめない（[契約1（OctantCompass・OctantHarvest → OctantVector）](engine-runtime.md)）ので、承認も署名も要らない
- 索引と分割したファイルを試すときは、OctantHarvest の `signing.allowUnsigned` と OctantCompass の「署名のない版を受け入れる」を入れて使う（[署名](#署名)の開発中の扱い）。配布先へのアップロードはしない
- 配布物に入れるビューは、呼ぶ側（OctantHarvest の設定 `views`）が毎回名指しする。エンコーダの段階（実験・候補・配布中・引退）と、候補を「配布中」にする承認はやめた（2026-10-14。どのビューを配るかは DB を作る人の選択で、承認は版の承認で行う）
- 版の形（[契約2（DB 生成 ↔ 推薦コア）](vector-db.md)）とこの契約の索引の形は守る。OctantCompass と OctantVector の推薦側がその形で読むため
- 上の表と[署名](#署名)の手続きは、公開のためのもの。公開（Dev 版）では、DB を OctantHarvest の版として出し、公開の承認と署名だけを行う（2026-10-14 から。最初の署名つきの全量は 2026.10.15）。渡すのは承認した版の全量を 1 つにした tar（`<dbVersion>.full.tar`。分ける前の索引のファイルと同じ形）で、OctantHarvest の `handoff` が OctantVector の `pack` で書く。差分で配る版は、このときに全量にも署名する。受け取る人は OctantCompass の「ファイルから取り込む」で取り込み、OctantVector の `import_archive` が `apply_update` と同じに署名を確かめる（2026-10-17。[OctantCompass 法の 6.4](../octantcompass/law.md#6-db-の更新)）。同じ tar を GitHub の Organization の Release にも public で置く（2026-10-17）。置き場所は OctantCompass の Releases（2026-10-23）。索引と配布先へのアップロードは公開（リリース）から行う（2026-10-12）。非公開のうちに作った版は署名を持たないので、署名を求める段階に入るときは、新しく作ってメンテナーが承認・署名した全量から始める（`allow_unsigned` を切った `build_index` は署名のない版も、確かめられない署名の版も載せない。[契約1（OctantCompass・OctantHarvest → OctantVector）の生成側](engine-generation.md)）

## 版ごとの変更

| 版 | 日付 | 変更 |
| --- | --- | --- |
| 1.0 | 2026-10-07 | 最初の版。版の確かめ方を契約どうしでそろえた（決定） |
| 1.1 | 2026-10-08 | 配る版のフォルダに `manifest.sig` を足した（[署名](#署名)。決定） |
| 1.1 | 2026-10-09 | contracts.md から分けた。中身は変わらない |
| 1.1 | 2026-10-10 | [非公開（探求中）の扱い](#非公開探求中の扱い)を足した（決定）。形は変わらない |
| 1.1 | 2026-10-11 | 署名は作者を示すものにし、合わない版を止めずに警告を出すことにした（決定、OctantVector 0.3.25）。探求中の扱い（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）で版は上げない |
| 1.1 | 2026-10-12 | ビューパックは差分の一種、索引の `url` が null のときの読み方、公開（Dev 版）で行う手続きを書いた（決定）。形は変わらない |
| 1.1 | 2026-10-17 | 公開（Dev 版）の手渡しを、全量の tar 1 つにした（決定。OctantVector 0.6.0、OctantHarvest #35、OctantCompass #44）。索引の形は変わらない |
| 1.1 | 2026-10-17 | 公開（Dev 版）の tar を Organization の Release にも置く（決定）。形は変わらない |
| 1.1 | 2026-10-22 | 公開（Dev 版）でも署名は警告のままにすることを書いた（2026-10-21 決定）。形は変わらない |
