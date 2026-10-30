# 設計方針

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。作りの説明で、正本はコードです。

OctantVector の作りの説明です。実装が守る意味は [OctantVector 法](law.md)にあり、ここでは繰り返しません。

## パッケージの構成

DB生成と推薦の Runtime は、配布物の形式だけを共有し、互いを import しません（[憲法](../constitution.md)の原則 8 の「配布 DB は別系統」を、パッケージの依存で表したもの）。

| パッケージ | 役割 | import してよいもの |
| --- | --- | --- |
| `octantvector.common` | 生成側と Runtime の両方が使うもの。譜面の識別とプレイスタイル、配布物のファイル形式（[契約2（DB 生成 ↔ 推薦コア）](../contracts/vector-db.md)）、手札の検査、推薦の数値の既定値（`params.py`）、版の署名と信頼する公開鍵（[契約5（OctantHarvest → 配布先 → OctantCompass）の署名](../contracts/distribution.md#署名)） | なし |
| `octantvector.runtime` | OctantCompass が呼ぶ側（[契約1（OctantCompass・OctantHarvest → OctantVector）](../contracts/engine-runtime.md#公開する関数)）と、それを組み立てる内部の関数（1 つのビューの検索、差分の適用、好みの判定） | `common` だけ |
| `octantvector.generation` | 契約4（OctantHarvest の収集結果 → OctantVector）の入力から台帳・エンコーダ・作業用の保存先を経て、配布物と索引を書く側（[契約1 生成側（OctantHarvest → OctantVector）の関数](../contracts/engine-generation.md)。OctantHarvest が呼ぶ） | `common` だけ |
| `octantvector.plugin` | エンコーダを足すパッケージ（[OctantVectorPlugins](https://github.com/BeatOctant/OctantVectorPlugins)）が使う唯一の入口（不安定版。[encoders.md のプラグイン](encoders.md#プラグイン)） | `generation` |
| `octantvector.eval`、`cli.py` | 評価と実験、コマンドライン（開発補助ツール） | 何でも |

Runtime は設定ファイルを読まず（契約1（OctantCompass・OctantHarvest → OctantVector））、生成側のモジュールや torch などのモデル系の依存なしで読み込めます。この向きは OctantVector の `tests/test_layers.py` が確かめます。

## データ

- マップ本体はローカルアーカイブ（`maps/<hash[:2]>/<hash>.zip`）から読み取り専用で読みます。ZIP はメモリ上で開き、アーカイブには一切書き込みません。読む順番はダウンロードの記録の順で、HDD 上の連続読み出しになるようにしています。
- マップのメタデータ（キー・タグ・難易度ごとの NPS/NJS など）は BeatSaver カタログのスナップショットから取ります。ZIP 内にはこれらの情報がないためです。
- OctantVector 自身の状態は、保存先の中の SQLite の台帳にだけ書きます。版ごとの状態（公開中・旧版・削除済み）、エンコーダの指紋ごとの計算結果（ok・error・skip）、プールの出入り、メタ情報のダイジェストを持ちます。表の中身は [`generation/ledger.py`](https://github.com/BeatOctant/OctantVector/blob/main/src/octantvector/generation/ledger.py) の冒頭にあります。`octantvector update`（契約1 の `compute`）は台帳だけを見て足りない分を計算するので、途中で止めても続きから進み、続けて 2 回実行すると 2 回目は何も計算しません。失敗した計算は記録し、指紋が変わったときか `--retry-errors` のときだけやり直します。
- 同じマップの新しい版は台帳の新しい行として計算し、古い版は「旧版」にします。旧版のベクトルは配布物に入れませんが、台帳と作業用の保存先には残します（過去のプレイ記録が旧版の hash を指すため。2026-10-02 決定。配布物では旧版から今の版への対応だけを持ちます）。
- メタ情報（タグ、ranked、キュレーションなど）は後から変わるので、メタ情報から作るビューは「版 + エンコーダが宣言したカタログの項目のダイジェスト」を入力として扱い、ダイジェストが変わった行だけ計算し直します。宣言していない項目（upvote 数など）が変わっても計算し直しません。
- アーカイブに zip がまだない版は「メタ情報だけある」状態で台帳に入れ、zip が届いたら音源・譜面のビューを計算します。
- 計算の対象は名前付きのプールで決めます。配布用（`distribution`）は公開中の全件で upvote の下限がなく、試し用（`trial`）は全件から決まった 20,000 マップを抜き取ったものです。音源と譜面のビューは、アーカイブに zip がある版だけを計算します。どのプールを計算するかは呼ぶ側が名指しします（`octantvector update --pool`、契約1 の `compute` の `pool`。校正と `release` は配布用）。エンコーダの段階（実験・候補・配布中・引退）はやめ、どのビューを計算して配るかは呼ぶ側（OctantHarvest の設定 `views`）が決めます（2026-10-14）。プールの定義は設定で変えたり足したりできます（[config.md](config.md)）。
- 同じ版の zip は中身が変わらない前提で、最初に読んだときの SHA-256 を台帳に記録します。同じ hash で中身の違う zip が来たら使わずにエラーとして記録します（法 1.5）。

## 値の版

ベクトルの 1 つの数値の意味は、下の 4 つの層の版がすべてそろって初めて決まります。どれか 1 つでも違えば、同じ値でも別のものです（[OctantVector 法](law.md) 2.1）。

| 層 | 何が変わると意味が変わるか | 版の名前 | 変わったら |
| --- | --- | --- | --- |
| エンコーダ | モデルの重みやリビジョン、前処理（クリップの取り方、サンプルレート）、特徴の並び、設定の数値（`[swing]` など）、元のビュー（derived）、学習済みファイル（スタイルモデルなど） | `id@version` と指紋 | 別の保存先・別のビューとして全件を計算し直す |
| 外部データ | BeatSaver 側の定義（タグの一覧、NPS の計算方法、譜面形式 v2/v3/v4） | カタログの版と入力ダイジェスト | 影響する行だけ計算し直す。定義自体が変わったらエンコーダの版を上げる |
| 座標系（校正） | 正規化に使う平均・標準偏差 | 校正 ID | 全量を配り直す |
| 配布物 | 入っている行（マップの集合） | `dbVersion` | 差分で更新できる。好みと実力は作り直す（契約1（OctantCompass・OctantHarvest → OctantVector）） |

形式の版（`schemaVersion`）はこれとは別で、ファイルの読み方だけを表します（契約2（DB 生成 ↔ 推薦コア））。

## マルチエンコーダ

- エンコーダごとに `id@version` のフォルダへ別々に保存し、キーはマップのバージョンハッシュです。譜面から作るビューは譜面単位で、キーは `<hash>:<characteristic>:<difficulty>` です。台帳の計算結果は、どちらも版ごとに記録します。新しいエンコーダを追加しても、他のエンコーダを再計算する必要はありません。定義（パラメータ）や元のビューを変えたらバージョンを上げます。上げずに既存フォルダへ書こうとするとエラーになります（指紋で照合します。[encoders.md](encoders.md#エンコーダの追加)）。
- 検索では、各ビューを個別に正規化してから、ビューごとのコサインの重み付き平均を取ります。配布 DB の値も同じ正規化で作ります。全ビューがそろったマップだけを使うとき（`--missing drop`、既定）は、重みをかけて連結したベクトルのコサインと同じなので、1 回の積で計算します。
- 正規化の統計は、校正（`octantvector calibrate`）でプールごとに 1 度だけ計算して固定できます。校正ファイルを `--calibration` で渡すと、マップが増えても既存のマップの座標は動きません。別の定義（指紋）のエンコーダ用の校正と、別の正規化の版で作った校正は使えません。正規化のコードはどの指紋にも入らないので、値が変わる変更をしたら `generation/normalisation.py` の `VERSION` を上げます（法 2.2）。上げると校正を作り直すことになり、校正 ID が変わるので、次の配布は全量になります。
- 開発用の `search` と `eval-neighbours` の `--missing reweight` では、ビューが欠けたマップも残します。持っているビューの重みが、推薦の引数 `params` の `minViewWeight`（既定は `common/params.py`）以上のマップだけを対象にし、どちらかのマップに欠けたビューはコサイン 0 として、重みはそのまま全体で平均します（推薦と同じ。法 3.1）。
- 基本の出力はビューごとの上位（`search --per-view`）で、重み付きの結合はその上の段です。結合の重みは問い合わせごとに変えられます。
- ハブ（多くのマップの近傍に出てしまうマップ）を抑える CSLS は、開発用の `search` と評価コマンドにだけあります（`search` と `eval-personal` は既定で使い `--no-csls` で切る。`eval-neighbours` は `--csls` で使う）。推薦側の `recommend` は使いません（要るかは実験で決める。[open.md の V5](../open.md#octantvector)）。
- 評価コマンド（`eval-neighbours`、`eval-personal`）は `--out` を付けると、問い合わせごとの結果を、使ったビューの `id@version`・指紋・重みと設定と一緒に保存します（形式は `src/octantvector/eval/results.py`）。後からモデル同士を比べるためです。
- 各ビューには、何を表すかの札としての役割名（`role`。music・vocal・chart・meta・artist・genre。[契約2（DB 生成 ↔ 推薦コア）の役割名](../contracts/vector-db.md#役割名)）があります。既定は種類で決まり（`generation/encoders/base.py` の `ROLES`）、派生ビューは元のビューの役割を引き継ぎます。役割は定義に含めないので、変えても版は上げません。重みのキーには使いません（手札と要求はビューの id で名指しする。2026-10-14）。

## 作業用の保存先と配布物

作った PC の中では埋め込みを生のまま持ち、配布するのは検索向けに整えた DB にします（2026-10-02）。検索はどちらでも同じコードが動きます。

|  | 作業用の保存先（生成する PC） | 配布物（利用者の PC） |
| --- | --- | --- |
| 入っている行 | 計算したすべての版（旧版・プール外も） | 配布用プールの公開中の版だけ |
| ビュー | 計算したすべてのエンコーダ | 呼ぶ側（OctantHarvest の設定 `views`）が名指ししたビューだけ |
| 値 | 生の値（float32） | 校正で正規化した値（float16） |
| 形 | `id@version` ごとのフォルダと番号つきのシャード（追記だけ。同じ hash は後のシャードが勝つ。`generation/store.py`） | 契約2（DB 生成 ↔ 推薦コア）の形 |

検索の索引は配布せず、読み込むときに作ります（契約2）。今の規模なら全件との内積で足ります。近似索引（HNSW など）は、読み込みか検索の時間が目標を超えたら入れ、そのときも手元で作ります（今のコードに近似索引はない）。

## 配布物

形は[契約2（DB 生成 ↔ 推薦コア）](../contracts/vector-db.md)、公開と更新の手続きは[契約5（OctantHarvest → 配布先 → OctantCompass）](../contracts/distribution.md)にあります。ここには OctantVector の中の作りだけを書きます。

- 契約1（OctantCompass・OctantHarvest → OctantVector）の `release`（開発用には `octantvector release`）が、作業用の保存先から次の版を作り、呼んだ側が指定したフォルダ（開発用のコマンドでは `<store>/releases/`）に置きます。上書きもアップロードもしません。
  - `<dbVersion>/` はその版の全量で、毎回書きます。次の差分の元になります。
  - `<dbVersion>.diff/` は前の版からの差分で、作れるときだけ書きます。作れるのは、前の版にもあるビューの指紋と校正の統計がすべて変わらず、前の全量からの差分の数が設定 `full_every` 未満のときです。それ以外は全量を配ります。
  - ビューは毎回指定します（`views` は必須）。校正は、指定しなければ前の版のものに新しいビューの統計だけを足して使うので、ビューを足しても他のビューの座標は動きません（法 2.3）。ビューの追加・差し替え・削除も差分で配ります。
- 差分を当てる側（`apply_update` とその中の差分の適用）は、生成側の全量と同じ関数で新しい全量を別のフォルダに書きます。そのため「前の全量 + 差分」と「新しい全量」は同じ中身になります（法 2.4）。失敗しても手元の DB は変えません。`octantvector apply` と `octantvector db <フォルダ> <キー>` で、OctantCompass と同じ手順を試せます。ビューの値は校正で正規化済みなので、検索は内積だけです。
- `build_index` は、渡された承認済みの版のフォルダだけから、版ごとの tar を上限以下に分けたファイルと索引 `index.json` を書きます。アップロードはしません。OctantVector 自身は通信しません。
- ずれ（契約1 の `drift`）は、ビューごとに、今の配布用プールの平均が校正の平均からどれだけ動いたかを、校正の平均のまわりの広がりを 1 として測ります。関係のビューは測りません。前の版のベクトルのビューを計算するエンコーダが入っていなければ（プラグインの入れ忘れ）エラーで止めます。いつ測り、どこから校正し直すか、承認、毎日の実行は OctantHarvest が決めます。
- まだ入っていないもの: `charts.parquet` の Pass と Tech（スイングシミュレーションの値が台帳にまだないので空、`chartMetrics` も空。[open.md の V4](../open.md#octantvector)）、索引の URL（置き場所は契約5 で未決。`build_index` に頭が渡されれば付けます）。
- モデルのファイルは取りに行かず、OctantHarvest の `octantharvest models` が置いたものだけを読みます（契約1 の `models(views)`。2026-10-14）。通信する部品を OctantHarvest に寄せ、取るものを 1 か所で記録するためです。音や画像のモデルを使うビュー（CLAP、MERT、WavLM とその歌声版、Whisper、SigLIP）は [OctantVectorPlugins](https://github.com/BeatOctant/OctantVectorPlugins) のプラグインに分け、使うものだけ入れます（[encoders.md](encoders.md)）。

## 推薦

- `recommend` と `describe`（`src/octantvector/runtime/recommend.py`）は、履歴をそのまま受け取り、毎回その場で計算します。手順の要約はそのファイルの冒頭にあり、難しさの考え方は[推薦の難易度合わせ](../plans/difficulty-fit.md)にあります。
- 履歴の読み方（旧版の置き換え、プレイの単位、素のプレイの判定）は `runtime/history.py`、得意な譜面からの距離としての実力は `runtime/skill.py`、好意の判定（法 4.1）は `runtime/likes.py` の 1 か所だけにあります。
- 数値は `params` で受け取り、既定値は `common/params.py` にだけあります（Runtime のほか、生成側の手札の検査と開発用の検索も使います）。OctantSpecs に既定値がないもの（「最近」の範囲、ジャンルで残す割合など）は仮の値です。コマンドラインの設定の既定値は `src/octantvector/generation/config.py` にあります（[config.md](config.md)）。

## 守る決まり

曲名を特徴にしないこと（法 3.2）、曖昧なシグナルを負例にしないこと（法 4.2）、好意の判定（法 4.1）、本人のデータを持ち出さないこと（法 4.3）は [OctantVector 法](law.md)にあります。

## 個人評価のプロトコル

手順は[実験ログの個人評価の手順](experiments.md#個人評価の手順)に移しました。
