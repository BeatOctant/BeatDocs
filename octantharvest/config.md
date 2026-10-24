# OctantHarvest の設定

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。値の正本はコード（`defaults.json`）です。

OctantHarvest の設定は 1 つの JSON ファイルです。`$OCTANTHARVEST_SETTINGS` で指定した場所、なければカレントディレクトリの `octantharvest.json` を読みます。書かなかった項目は既定値になり、知らない項目があるとエラーで止まります。相対パスは設定ファイルのフォルダからの位置です。設定ファイルには書いた人が決めた値だけを書き、個人のパスを含むのでリポジトリには入れません。

- 項目と既定値: [`src/octantharvest/defaults.json`](https://github.com/BeatOctant/OctantHarvest/blob/main/src/octantharvest/defaults.json)。値はそこにしか書きません。`crawl.catalogue` と `crawl.download` の数はそこでは null で、収集のスクリプトの既定（`--help` に出る）を使う意味です
- 各項目の意味: [`src/octantharvest/settings.py`](https://github.com/BeatOctant/OctantHarvest/blob/main/src/octantharvest/settings.py) の冒頭と、[OctantHarvest の README](https://github.com/BeatOctant/OctantHarvest/blob/main/README.md)（使い方の順に説明しています）
- `octantvector` の中身は OctantVector の生成側の関数に渡す `params` で、名前は [OctantVector の設定](../octantvector/config.md)と同じです。パスの設定（`archive`、`catalogue`、`store`、`artists`、`models_dir`）は `paths` から渡すので、ここには書けません

## 決まっていること

項目の中身のうち、メンテナーが決めたことと、外のサービスの決まりから来るものです。

- **収集は差分で、全体は `crawl.fullWalkDays` ごと。** 各取得は、いちばん新しい完了した取得を起点に、その後に変わった分だけを取ります。未完了や失敗した取得は起点にしません（2026-10-14、OctantHarvest #33）。カタログ全体をたどり直すのは、完了した取得がないとき、最後の全体の取得から `crawl.fullWalkDays` 日たったとき、`octantharvest crawl --full` のときだけです。投票以外の統計（プレイ数など）と、`updatedAt` の変わらない変化は、このときに直ります（間隔は 2026-10-16 決定。値は `defaults.json`）。`crawl.keepCaptures` で古い取得を消すときも、次の起点になるいちばん新しい完了した取得は残します
- **`crawl.artists.minDelay` は 1 秒以上。** MusicBrainz と ListenBrainz は 1 秒に 1 回までなので、1 未満は断ります（OctantHarvest #31）。`crawl.artists.userAgent` は必須で既定はありません。MusicBrainz が連絡先の入った User-Agent を求めるので、空なら `octantharvest artists` は止まります
- **`views` は必須で、既定の一覧はない。** `daily` と `first-release` は空なら止まります（OctantVector 0.4.0 でエンコーダの段階をやめたため。2026-10-14）。プラグインのビューはそのプラグインを入れたときだけ使えます（[OctantVector のプラグイン](../octantvector/encoders.md#プラグイン)）。関係のビュー `beatsaver_mappers` も名前で書け、計算はせずリリースのときにカタログから作られます（[契約1](../contracts/engine-generation.md)）
- **`presets` の重みはビューの id で書く**（[プリセットの 12 節](../plans/presets.md#12-手札はビューを名指しする2026-10-14)）。毎回の `release` に渡し、OctantVector が新しい DB で使えるかを確かめてマニフェストに書きます（[契約1（OctantCompass・OctantHarvest → OctantVector）の生成側](../contracts/engine-generation.md)）。空なら前の版の手札を引き継ぎます
- **`notice` は DB 全体の利用条件とクレジットのファイル**（OctantHarvest の `DB-NOTICE.md`）。毎回の `release` に渡し、OctantVector がマニフェストの `notice` に書きます（[契約2](../contracts/vector-db.md)）。空なら前の版のものを引き継ぎます。モデルなどのクレジットはビューごとにエンコーダが持つので、ここには書きません（2026-10-18）
- **`paths.models` のモデルは黙って置き換えない。** `octantharvest models` は、記録（`models.json`）と違うファイルがあると止まります（2026-10-16 にこの形を採った。[外部依存](../contracts/external.md)）
- **`signing.key`（承認のときに版に署名する秘密鍵）はメンテナーの PC にだけ置き、リポジトリには入れない。** 空なら承認できません（[署名](../contracts/distribution.md#署名)）。`signing.publicKey` は OctantVector の `build_index` に `trusted_keys` として渡し、空なら OctantVector が同梱する鍵だけを信じます（メンテナーの鍵は同梱なので書かなくてよい。OctantHarvest #33）。`signing.allowUnsigned` は開発用で、非公開（探求中）の段階での使い方は契約5（OctantHarvest → 配布先 → OctantCompass）の[非公開（探求中）の扱い](../contracts/distribution.md#非公開探求中の扱い)にあります
- `publish.partSizeMb` は配布先の 1 ファイルの上限より小さくします（GitHub Releases なら 2 GB）

OctantVector の生成側が断ったこと（`GenerationError`。プラグインの入れ忘れ、モデルのファイルがない、使えない手札など）は、そのコマンドを OctantVector のメッセージで止め、`daily` ではその日の実行の記録（`daily.jsonl`）に残して次の日に続けます（OctantVector 0.4.0）。自分の DB を作って配る手順は OctantHarvest の README にあります。
