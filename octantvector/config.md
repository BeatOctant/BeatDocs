# 設定

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。値の正本はコード（`config.py` の `DEFAULTS`）です。

OctantVector（0.5.0）の設定の受け取り方です。各設定の名前・既定値・意味は [`src/octantvector/generation/config.py` の `DEFAULTS`](https://github.com/BeatOctant/OctantVector/blob/main/src/octantvector/generation/config.py) にまとめてあり、値はそこにしか書いていません。

## 読み込みの順

開発用のコマンド（`octantvector update`、`search`、`release` など）の設定は、環境変数 → 設定ファイル → 既定値の順に優先して決まります。

- 環境変数は、設定の名前を大文字にして `BV_` を付けたものです（`archive` なら `BV_ARCHIVE`）
- 設定ファイルは TOML 形式で、`$BV_CONFIG` で指定した場所、なければカレントディレクトリの `octantvector.toml` を読みます。キー名は環境変数名から `BV_` を除いて小文字にしたものです
- 設定ファイルは個人のパスを含むので、リポジトリには入れません（`.gitignore` で除外しています）

```toml
archive = "/path/to/archive"
catalogue = "/path/to/catalogue.jsonl.gz"
store = "/path/to/store"
```

設定ファイルのテーブルは、キーと既定値をそれを読むモジュールが持ちます。`[pools.<名前>]` は計算の対象にするプール（既定は公開中の全件の `distribution` と、決まった 20,000 マップを抜き取った `trial`。[`generation/pools.py`](https://github.com/BeatOctant/OctantVector/blob/main/src/octantvector/generation/pools.py)）、`[swing]` はスイングシミュレーションの数値（`generation/swing/params.py`）、`[swing_tags]` は細分タグの条件（`generation/swing/style.py`）です。`[swing]` か `[swing_tags]` を変えると `swing_flow`・`swing_style`・`swing_hazards` の定義が変わるので、既存の保存先を使い続けるにはエンコーダの版を上げます（[OctantVector 法](law.md) 2.2）。

## 生成側の関数は params で受け取る

OctantHarvest が呼ぶ[契約1 生成側（OctantHarvest → OctantVector）の関数](../contracts/engine-generation.md)は、設定ファイルも環境変数も読みません。同じ名前の設定を引数 `params` で受け取り、渡されなかったものは既定値になります（`pools`・`swing`・`swing_tags` のテーブルも同じ名前で渡します）。知らない名前はエラーです。パスの設定（`archive`・`catalogue`・`artists`・`store`・`models_dir`）は `params` には書けず、関数の引数（収集結果、作業用の保存先、`models_dir`）で渡します。

校正をやり直す閾値、索引の 1 ファイルの上限、配布先の URL は OctantHarvest の設定です（[octantharvest/config.md](../octantharvest/config.md)）。
