# エンコーダ

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。エンコーダの説明で、版や次元数の正本はコードと `encoder.json` です。

OctantVector 0.8.0 と OctantVectorPlugins の main にあるエンコーダです。版・次元数・パラメータ・使用モデルのリビジョンは、各エンコーダのコードと、保存先の `encoder.json` に記録されています。ここには役割と既知の問題だけを書きます。

OctantVector 本体に入っているのは、譜面とメタ情報のエンコーダです。音や画像のモデルを使うビュー（CLAP、MERT、WavLM、Whisper、SigLIP）は [OctantVectorPlugins](https://github.com/BeatOctant/OctantVectorPlugins) のプラグインにあり、使うものだけを OctantVector と同じ環境に入れます（OctantVector 0.4.0、2026-10-14。入れ方は OctantVectorPlugins の README、決まりは下の[プラグイン](#プラグイン)）。

| id | 役割 | 種類 | 内容 | コード |
|---|---|---|---|---|
| `chart_patterns` | chart | zip（譜面単位） | 全プレイスタイルの全譜面のパターン統計（密度・方向・角度変化・交差・レーン・間隔など）。譜面は `swing/chart.py` で読むので、譜面形式 v2/v3/v4、BPM の変化、Noodle / Mapping Extensions、触れないオブジェクトを扱う | `generation/encoders/chart_patterns.py` |
| `swing_flow` | chart | zip（譜面単位） | Standard の全譜面のスイングシミュレーションの特徴量（速さ・リズム・手首の角度・パリティ・移動・壁と爆弾・Pass/Tech など。説明は [swing.md](swing.md)）。シミュレーションが Standard 用なので、ほかのプレイスタイルの譜面にはベクトルを作らない | `generation/encoders/swing.py` |
| `swing_style` | chart | derived（譜面単位） | `swing_flow` から計算したスタイルタグ（BeatSaver タグの学習確率と、acc / tech などを細分したタグのスコア。[swing.md](swing.md)） | `generation/encoders/swing.py` |
| `swing_hazards` | chart | derived（譜面単位） | `swing_flow` から計算した壁・爆弾のタグのスコア（アートの壁、運動になる壁、リズムに乗る壁、よける爆弾など。[swing.md](swing.md)） | `generation/encoders/swing.py` |
| `npsnjs_std` | chart | map | Standard 各難易度の NPS/NJS と、各難易度の有無を 1 本にまとめたもの。譜面の値を版単位にまとめているので実験専用で、配布物には入れられない（譜面ごとの NPS・NJS は配布物の `charts.parquet` にある） | `generation/encoders/catalogue_features.py` |
| `meta_tags` | meta | map | タグ・年・長さ・BPM・各種フラグ（人気度とマッパーは意図的に含めていません。譜面から計算する値も含めません。マッパーは別の関係のビュー `beatsaver_mappers` にしました） | `generation/encoders/catalogue_features.py` |

OctantVectorPlugins のビュー:

| id | 役割 | 種類 | 内容 | パッケージ |
|---|---|---|---|---|
| `clap_htsat_unfused` | music | audio | LAION CLAP（`laion/clap-htsat-unfused`）の音声埋め込み（3 か所の 10 秒クリップの平均） | `octantvector-clap`（`clap/`） |
| `vocal_clap_htsat_unfused` | vocal | audio | 同じモデルを、Demucs で分けた歌声に当てたもの（声の種類） | `octantvector-clap`（`[vocal]`） |
| `clap_concepts` | genre | derived | `clap_htsat_unfused` と、ジャンル・ムード・ボーカル・楽器などのテキスト概念とのコサイン類似度（58 語。語の並びは配布物のビューの `genres`） | `octantvector-clap` |
| `mert_v1_95m` | music | audio | MERT-v1-95M の中間層の平均 | `octantvector-mert`（`mert/`。CC BY-NC 4.0） |
| `vocal_mert_v1_95m` | vocal | audio | 同じモデルを歌声に当てたもの（歌い方と声色） | `octantvector-mert`（`[vocal]`） |
| `vocal_wavlm_sv` | vocal | audio | WavLM の話者照合の x-vector を歌声に当てたもの（声そのもの。クリップごとに L2 正規化してから平均） | `octantvector-wavlm`（`wavlm/`） |
| `whisper_language` | language | audio | Whisper large-v3 で判定した歌の言語（100 言語。norm `none`）。曲全体を、曲の長さ ÷ 30 秒（切り上げ）か所の 30 秒で始まりから終わりまで等間隔に覆って判定し（箇所どうしは均等に少しずつ重なる）、歌のある箇所のうち各言語の箇所の数を L2 正規化する（1 言語の曲は one-hot、2 言語の曲は両方を割合で持つ）。言語の確率のエントロピーが 1.95 を超える箇所、km など歌のない曲が出やすい 18 言語になった箇所、1 位の確率が 0.5 未満の箇所は歌なしとし、歌のある箇所がない曲はベクトルなし | `octantvector-whisper`（`whisper/`） |
| `siglip_cover` | cover | image | SigLIP so400m のカバー画像の埋め込み（L2 正規化。norm `none`）。カバーのないマップはベクトルなし | `octantvector-siglip`（`siglip/`） |

カタログから作る関係のビュー: `beatsaver_mappers@1`（役割 mapper。譜面の作者の BeatSaver のアカウント ID。OctantVector 本体の `generation/mappers.py`。計算せず、`views` に名指しすると `release` が入れる）。

0.4.0 で消したエンコーダ: `mert_v1_330m`、`ast_audioset_emb`、`ast_audioset_labels`（exp07 で足してもよくならなかった）、`audio_stats`（librosa の手作りの特徴）。保存先に残っている計算結果は、そのビューを指定しなければ読みません。

種類（kind）と正規化方法（norm）の意味は `generation/encoders/base.py` に書いてあります。

「譜面単位」のビューは 1 譜面に 1 本のベクトルを持ち（キーは `<hash>:<characteristic>:<difficulty>`）、それ以外は 1 版に 1 本です（`rows`。[憲法](../constitution.md)の原則 2）。譜面単位のビューの類似度は同じプレイスタイルの譜面どうしでだけ測ります。配布物に入れられるのは、譜面を表すビュー（役割 chart）なら譜面単位のものだけです（`src/octantvector/generation/dbrelease.py`）。版単位の実験（`search`、`eval-personal` などの索引）では、譜面単位のビューを各版の最難の Standard 譜面で代表させます。

## 既知の問題と対処

- **`laion/larger_clap_music` は使えません。** Hugging Face 版はどんな入力でもテキスト・音声のロジットが均一になります。transformers 5.x でも 4.x でも同じでした。そのため `laion/clap-htsat-unfused` を使っています。
- **MERT は隠れ状態をフックで取ります。** transformers 5.x では、MERT のモデルのコードが `output_hidden_states` を無視します。そのため指定した層の出力を forward hook で取得しています。モデルのコード（`modeling_MERT.py`、`configuration_MERT.py`）は Hugging Face の `trust_remote_code` では読まず、固定した revision からの写しを `octantvector-mert` に含めています（そのためパッケージ全体が CC BY-NC 4.0。`mert/NOTICE`）。
- **モデルは取りに行きません。** 各エンコーダが宣言したモデルを `models_dir` の下の `hf/<repo>/<revision>/` からだけ読みます。ないときはそのビューを使う操作がエラーになり、`octantharvest models` で置くよう出ます（契約1 生成側の `models(views)`。OctantVector 0.4.0）。
- **プラグインの版が合わないと読み込みません。** `octantvector.plugin` の `PLUGIN_API` と違う番号で書かれたプラグインは登録されず、`octantvector check` とそのビューを頼んだときに理由が出ます（[プラグイン](#プラグイン)）。
- **埋め込みワーカーは spawn で起動します。** CUDA やダウンロード用のスレッドを持ったプロセスから fork すると、ワーカーがデッドロックします。
- **埋め込みのワーカーは、数値計算のスレッド 1 つずつで動かします。** 呼び出し側が `OMP_NUM_THREADS` などを決めていればそれを使います。ワーカーが落ちたら待ち続けず、受け持っていた可能性のあるマップを示して止めます。再実行すれば続きから計算します。
- **ワーカーのメモリを見張ります。** 設定 `worker_memory_gb` を超えたワーカーだけを止め、その Map は失敗として記録して、ほかの Map の計算を続けます。比べるのはワーカー自身のメモリで、共有ライブラリの分は数えません（数えると健全なワーカーまで止まり、計算全体が止まった）。ワーカーは 200 Map ごとに入れ替えます。全件の計算でワーカー 1 つが 35GB になり PC が固まったために足しました。
- **30 分より長い曲はデコードしません。** その Map の音声のビューだけを失敗として記録します。曲が読めなくても、同じ zip の譜面のビューは残します。9 時間の曲でデコーダが落ちたために足しました。
- **一部の .dat は UTF-16 です。** 文字コードは `json.loads` に任せ、BOM か、BOM がなければ先頭のバイトで判別して読みます（UTF-8・UTF-16・UTF-32。OctantVector 0.8.1）。
- **曲が音声でないマップがあります。** 音声ファイルの代わりに動画（Ogg Theora）が入っていたり、音声ファイルが無かったりするマップです。デコードに失敗したマップは台帳にエラーとして記録して飛ばし、次の `update` では計算し直しません。ノーツが少なすぎる譜面には `chart_patterns` のベクトルを作りません。

## エンコーダの追加

OctantVector 本体に足すときは `generation/encoders/` にクラスを追加して `@register` を付け、`generation/encoders/__init__.py` で import します。別のパッケージに置くときは、`octantvector.plugin` だけを使って書き、そのパッケージの entry point（グループ名 `octantvector.encoders`）にモジュールを登録します（[プラグイン](#プラグイン)）。どちらも同じ登録簿に入り、`octantvector update <id>` でそのエンコーダの分だけが計算されます。音声モデルのビューは OctantVectorPlugins に置きます（本体には入れない。2026-10-14）。

各エンコーダは次を宣言します。書き方と取りうる値は `generation/encoders/base.py` にあります。

- **入力（`inputs`）**: 値が何に依存するか（音源、譜面、カタログのどの項目、どのビュー、どの学習済みファイル）。宣言のないエンコーダは登録できません。毎日の差分でどの変化から計算し直すかは、この宣言で決めます
- **モデル（`Model`）**: 読む学習済みモデル（Hugging Face のリポジトリ、40 桁の revision、ファイル名）。契約1 の `models(views)` がこれを集め、OctantHarvest が置きます（上の「モデルは取りに行きません」）

エンコーダの段階（実験・候補・配布中・引退）は OctantVector 0.4.0 でやめました（2026-10-14）。どのビューを計算して DB に入れるかは、呼ぶ側（OctantHarvest の設定 `views`）が毎回名指しします。試すときは `trial` プール（[設定](config.md)）で一部だけ計算します。

保存先の `encoder.json` には定義と一緒に指紋（定義と元のビューの指紋をまとめたハッシュ）を記録します。版を上げずに定義か元のビューが変わると、保存先を開くときにエラーで止まります（[OctantVector 法](law.md) 2.2）。`octantvector check` で、エンコーダごとの計算済みの件数と、読み込めなかったプラグインを確認できます。

## プラグイン

プラグイン（エンコーダを足すパッケージ）の形と規約は、[OctantVectorPlugins の README](https://github.com/BeatOctant/OctantVectorPlugins/blob/main/README.md) と、OctantVector の [`src/octantvector/plugin.py`](https://github.com/BeatOctant/OctantVector/blob/main/src/octantvector/plugin.py) の冒頭（公開するもの）にあります。

- **不安定版です。** `octantvector.plugin` が変わるたびに `PLUGIN_API` の番号を上げ、別の番号で書かれたプラグインは読み込みません。契約1（OctantCompass・OctantHarvest → OctantVector）の一部ではなく、OctantVector の中の取り決めです。固まったら、契約の決まりに合わせて書き直します（2026-10-14、OctantVector 0.4.0）
- エンコーダの id は、本体やほかのプラグインと重ねられません。役割（`role`）は[契約2（DB 生成 ↔ 推薦コア）の役割名](../contracts/vector-db.md#役割名)から選びます
- 決まっていないこと: `PLUGIN_API` をいつ固めるか（固めると、変えるときに OctantVector のメジャー版を上げることになる）。プラグインのビューの名前と役割の予約（同じ id を 2 つのパッケージが名乗ったときの扱い。今は同じ id を 2 度登録しようとするとエラーになる）
