# プリセット（OctantPath のボタンを OctantCompass の開示から作る）

> 固さ: 後から記録する層（[憲法の原則 10](../constitution.md#10-段階と文書の固さ)）。実装済みの仕組みの説明で、正本はコードと契約3 の OpenAPI です。節の番号はコードが指すので変えません。

2026-10-10 作成（2026-10-11 表示名の言語を足す。2026-10-13 画面での呼び名を足す） · 状態: 実装済み（OctantVector、OctantCompass、OctantPath #30、OctantHarvest の公式の手札）。中身の持ち主と最初の一覧は 7・8 節で決めた。契約の形は憲法の原則 10 の「後から記録する層」で、2026-10-12 に固めた（10 節）

## この文書の役割

課題（2026-10-10）: OctantPath は、推薦の種類を 1 つ足すごとにボタンを作っている。本来は、何をキーにするかを開示し、OctantPath はそれを受け取って描けばよいはず。

この文書は、手札（プリセット）の考え方と、決めたことを置きます。形の正本は[契約3](../contracts/mod-api.md)の [OpenAPI](../contracts/mod-api.openapi.yaml)（`PresetsResponse`）と、[契約1 の手札が使えるとき](../contracts/engine-runtime.md#手札が使えるとき)です。決めることは [open.md のプリセット](../open.md#プリセット)にあります。

## 1. 今の形と困りごと（2026-10-17 に退いた。決定は decisions.md）

2026-10-10 時点の、OctantPath がボタンを BSML に直に書いていたころの記録でした。

## 2. 条件の組み合わせに名前を付け、OctantPath はボタンにするだけ

条件の組み合わせ（起点、狙い、ジャンルの語、重み）に名前を付けたものを **プリセット**（文書とコードでは「手札」）と呼びます。推薦は 1 種類のままで（[推薦の定義](recommendation-definition.md) Q1）、手札を足しても契約3（OctantPath ↔ OctantCompass）は変わらず、一覧が増えるだけです。

| | 手札の中身を持つ側（8 節から配布 DB と OctantVector。OctantCompass は中継） | OctantPath |
| --- | --- | --- |
| 持つもの | 手札の一覧（id、表示名、必要な入力、中の条件） | 推薦の設定（どの手札をどこに出すか・出さないか・並び順、件数、`params`） |
| すること | `GET /v1/presets` で一覧を返す。要求の `preset` を契約1（OctantCompass・OctantHarvest → OctantVector）の条件に変えて推薦する | 一覧をそのままボタンにする。押されたら、id と必要な入力（選んでいる譜面、選んだ語）と自分の事実（件数、除外、`params`）を送る。一覧の結果を描く |
| しないこと | 距離や点数の計算（憲法の原則 4。手札は条件の組み合わせで、計算ではない） | 手札の中身を知ること、並べ替え（憲法の原則 6） |

### OctantPath に残るもの

ボタンを自動で作るのは「推薦の条件を選ぶボタン」だけです。次のものは OctantPath が持ち、今のまま BSML に書きます。

- OctantPath 自身の操作（ミックス、取得、保存、固定）
- ゲーム側の事実での絞り込み（おなじみ・新しい曲）。入っているかは OctantPath だけが知る事実で、推薦の条件ではないため（憲法の原則 5。推薦の順位は変えず、見せる範囲を絞るだけ）

## 3. プリセットの形（2026-10-17 に退いた。決定は decisions.md）

形は契約3 の OpenAPI（`PresetsResponse`、推薦の要求の `preset` と `choices`、`unknown_preset`、`/v1/health` の `presetsRevision`）に入りました。手札を持たない DB の一覧は 12 節（`all` だけ）です。

## 4. OctantPath の描き方

ここは OctantPath の実装で、契約ではありません。

- 起点の要らない手札を曲選択の上の板に、すべての手札を中央の種類の小窓に出す（[OctantPath の画面](octantpath-implementation.md#ミックスの今の形2026-10-10実装に合わせて記録)）
- `seed` が要る手札は、譜面を選んでいない間は押せなくする。起点のない場所では、`seed` が必須の手札を出さない
- `choice` は、押したら modal に選択肢を並べる
- 表示名が長いときは縮めて、`hint` をホバーに出す。表示名の長さの目安は契約に書かない（OctantPath が収まらなければ縮める。2026-10-12）

## 5. 境界への影響（2026-10-17 に退いた。決定は decisions.md）

契約3・契約2・憲法の原則 5・OctantPath と OctantCompass の実装の変更は、どれも済みました。

## 6. 案の外にした形（2026-10-17 に退いた。決定は decisions.md）

OctantCompass が画面の部品まで送る形と、OctantPath が `db.roles` から自分でボタンを作る形は採りませんでした。

## 7. 決まったこと（2026-10-10）

| # | 事柄 | 決定 |
| --- | --- | --- |
| 1 | 推薦の設定とは何か | OctantCompass が手札（プリセット）を OctantPath に渡し、OctantPath は手札を種類ごとに場所を分けてユーザーに見せ、ユーザーは 1 枚をキー（入力）と一緒に返す。推薦の設定は手札を選ばせる側の値（どの手札をどこに出すか・出さないか・並び順、件数、推薦の数値）で、OctantPath にある。手札の一覧と中の条件は推薦の設定ではない。これまで「推薦の設定」の意味はどこにも書かれておらず誤読されやすかったので、[憲法の原則 5](../constitution.md#5-octantpath-は-beat-saber-側とユーザー状態を担う) に書き足した |
| 2 | 最初の一覧 | 最初の一覧の案のとおり（すべて・似た曲・似たマップ・ジャンル・挑戦・久しぶり） |

## 8. 手札の定義を配布 DB に移す（2026-10-10）

2 節の表では手札の一覧と中の条件を OctantCompass が持つとしていましたが、これを変えました。理由は困りごと（2026-10-10）の 2 つです。コミュニティが調教した DB を入れても新しいボタンが出ない（OSS として硬い）。1 つの機能が OctantVector・OctantCompass・OctantPath にまたがり、保守が重くなる。

| 置き場 | 中身 | 例 |
| --- | --- | --- |
| DB の申告 | 各ビューが何の空間で、何と比べられるか（事実だけ。今の `role` と `genres` の延長） | `music` は音の空間。CLAP のビューは語と同じ空間なので語で探せる。`chart` は同じプレイスタイルの譜面どうしでだけ比べる |
| OctantVector の扱い方（コード） | embedding の使い方の種類。それぞれ、要る申告を持つ | 近い順（起点のまわり）、方向（起点から語や難しさの向きへずらす）、語で絞る、絞ってから並べる、知っている曲から選ぶ |
| DB の手札 | 扱い方 1 つと、そのつまみ（どのビュー、重み、語）に、id・表示名・入力を付けたもの | 似た曲 = 近い順・`clap_htsat_unfused` と `mert_v1_95m`。曲調も近いマップ = 音のビューで絞ってから `chart_patterns` で並べる（重みはビューの id で書く。12 節） |

- OctantVector は、DB の手札のうち、要る申告が DB にあり、自分が知っている扱い方のものだけを返す。DB に手札がなければ、OctantVector 同梱の既定の手札（12 節）を使う
- 扱い方の中身（距離の取り方、方向へのずらし方、何件で絞るか）は OctantVector のコードで、DB には書かない。手札が手順を書ける言語に育つと OctantVector を分ける意味が薄れるので、手札に書けるのは OctantVector が定めた語彙だけにする
- OctantCompass は `GET /v1/presets` で OctantVector の一覧をそのまま返し、要求の `preset` と `choices` を中身を見ずに渡す。足すのは session context と難易度の狙いだけ
- OctantPath と契約3（OctantPath ↔ OctantCompass）は変わらない
- 手札のファイルは生成の入力として OctantHarvest やコミュニティの作者が渡し、DB に書き出すのは OctantVector（憲法の原則 4b）
- 一覧の `revision` は、DB の版と一覧の中身から作るハッシュ（12 文字）。要求の `params` と手札の `params` が重なったら、要求のほうを使う

機能の足し方は次のように分かれます。

| 足すもの | 直す場所 |
| --- | --- |
| 今ある扱い方の新しい組み合わせやつまみ（曲の重みを上げる、新しいビューを使う） | DB の手札だけ（コミュニティの DB でもできる） |
| 新しい扱い方（曲調で絞ってから譜面で並べる） | OctantVector と DB の手札。古い OctantVector ではその手札が出ないだけ |
| 新しい入力の種類 | OctantPath（まれ。知らない種類の入力がある手札は出さない。OpenAPI の `inputs`） |
| 新しい事実や session context | OctantCompass |

決めたこと（2026-10-10。実装の前に詰めた 7 つ）:

| # | 事柄 | 決定 |
| --- | --- | --- |
| 1 | 手札に何が要るか | つまみから OctantVector が判断する。書き手の `requires` はなくす |
| 2 | 知らないつまみ | その手札を出さない。扱い方ごとのつまみの一覧はコードで持つ |
| 3 | 最初に入れる扱い方 | 近い順（`near`）と、絞ってから並べる（`narrow_then_rank`）。方向と難易度だけで選ぶ扱い方は後で |
| 4 | 絞ってから並べるのつまみ | DB はどのビューで絞り、どれで並べるかだけを書く。絞る件数は扱い方の中身なのでコード（`narrowTopMaps`） |
| 5 | 選択の入力 | `name` を扱い方のつまみに結び付ける汎用の形。`genre` だけを特別に扱わない |
| 6 | DB の手札と既定の関係 | DB の手札で全部置き換える。壊れた手札はその手札だけ外して、DB は読む |
| 7 | 手札を DB に入れる口 | 生成の `release` の引数。公式の手札の元のファイルは OctantHarvest が持つ（憲法の原則 7） |

### DB に手札を持たせる利点が出る手札（2026-10-10、実装に合わせて記録）

課題（2026-10-10）: 手札を DB に持たせても、既定の手札と同じ中身なら利点がない。DB ごとに中身が変わって初めて意味が出る手札を作る。

- **当たる語だけのジャンル**: 語のビュー（`clap_concepts`、58 語）は、2026-10-10 から役割 `genre` として語の並びごと DB に入る。58 語のうち音で当たるのは一部だけ（spike R1。classical、ambient、metal、instrumental、jazz、folk、speedcore、trance、techno）。公式の手札（OctantHarvest の `presets/official.json`）は、その 9 語だけを英語と日本語の名前付きで選択肢に出す。別のエンコーダの語を持つ DB（たとえば Discogs400）は、自分の語と名前の手札を配れば、コードを直さずにボタンが変わる
- **ジャンルで似た曲**（`song_genre`、公式の手札だけ）: 選んでいる曲を起点のまま、候補を語に近いマップに絞る。要求の `genre` は、起点があるときも絞り込みに効く
- 9 語を選んだ基準（上位 200 で倍率 5 前後より上）は推測で、まだ決めていない。語のビューを DB に入れるには、OctantHarvest の `views` に `clap_concepts` を足して版を作り直す
- 音のビューを増やしたら、使う手札に公式の手札のファイルで書き足す（役割名では名指しできない。12 節）。ビューが DB に入ってから足す（使えない手札があると `release` が止まるため）

## 9. 表示名の言語（2026-10-11）

決定: 英語を読める人の方が多いので、英語を既定にし、日本語を残す。言語ファイルを差し替えるだけで言語を変えられる形にする。

- 手札の表示名（`label`・`group`・`hint`、入力と選択肢の `label`）は、文字列か `{言語: 文字列}` のどちらでもよい。OctantVector は形を確かめて素通しし、OctantCompass は中継し、OctantPath が自分の言語、`en`、最初の値の順に選ぶ（OctantVector #41、OctantPath #6）
- OctantPath が id から表示名を引く形にはしない。案の外にした「役割名と表示名の対応を OctantPath が持ち続ける」形（6 節、decisions.md）に戻るため
- OctantCompass に言語を送って選ばせる形にもしない。表示の判断が OctantCompass に入るため。言語の設定は OctantPath の正本（憲法の原則 7 のゲーム内の動作設定）
- 既定の手札（OctantVector）と公式の手札（OctantHarvest #13）は英語と日本語を持つ。英語は日本語から推測で付けたもので、見直す余地がある
- OctantPath の画面の文は、OctantPath の言語ファイル（`src/OctantPath.Core/Languages/<言語>.json`）にある。Desktop だけの文（サーバーの知らせと、`/api/lang` で配る画面の文）は、Desktop の言語ファイル（`src/OctantPath.Desktop/Languages/<言語>.json`）に分けてある（OctantPath 36d701d）。自前の JSON にしたのは、ファイルを置くだけで差し替えられ、MOD と Desktop で同じ形を使えるため。.NET の resx は差し替えに DLL の作り直しが要り、BSML（Polyglot）の仕組みは Desktop の HTML で使えず、gettext は C# と JS で別の実装が要る
- **画面での呼び名**（2026-10-13）: 「手札」は文書とコードの用語で、画面には出さない。画面（MOD、OctantPath Desktop、OctantCompass の管理画面）では「種類」（英語 Types）と呼ぶ。「手札」は配る DB によって中身が変わる一揃いという意味を持つが、喩えなので設計を読んでいない人には何を指すか分かりにくいため（OctantPath #20、OctantCompass #28）
- **Web の画面どうしの言語**（2026-10-13）: OctantPath Desktop が OctantCompass の管理画面を開くときは、Desktop の画面の言語を URL で渡し、管理画面はその窓でその言語を使う（管理画面の URL の `#` の後ろに `lang=` を足す。OctantPath #20、OctantCompass #28。開く方法は[契約6（つなぐ側 ↔ OctantCompass）の管理画面](../contracts/launch.md#管理画面)）。MOD の言語とは揃えない。OctantCompass が別の PC で動くこともあり、互いの設定ファイルを読みに行く形にはしないため

## 10. 固めたこと（2026-10-12）

探求中に後から記録する層を固めたときに、open.md の残りを決めました。

- 案を採る。契約3（OctantPath ↔ OctantCompass）と OpenAPI の形は今の実装のとおり
- ユーザーが自分のプリセットを作る道と、利用者が手札を手で足す上書きファイルは、今は作らない
- 手札の `group` は任意の項目として固める
- `recommendation` の signal に、元の要求のプリセットの id を任意の `preset` で残す（OctantCompass のキャッシュを失っても分かるように）
- 表示名の長さの目安は契約に書かない
- DB の申告の形は今のまま（役割名とジャンルの語）。方向の扱い方を入れるときに見直す

## 11. 似た曲に近いアーティストを入れる（2026-10-12）

近いアーティストを関係のビュー `listenbrainz_artists@<取得日>`（役割 `artist`。[契約2 のビューの種類](../contracts/vector-db.md#ビューの種類)）として DB に入れることにしたので、「似た曲」の手札にその重みを足します。重みは 2026-10-14 からビューの id で書きます（12 節）。

- 公式の手札（OctantHarvest の `presets/official.json`）の `song` は `weights: {clap_htsat_unfused: 0.5, mert_v1_95m: 0.5, listenbrainz_artists: 0.25}`。試しの「音の近さ + 0.25 × アーティストの近さ」と同じ並びになる（2,000 起点すべてで一致。[実験ログ](../octantvector/experiments.md)）
- `listenbrainz_artists` の重みは、ほかのビューの合計に対して 1 以下で使う。`minViewWeight` の既定（0.5）では、1 を超えるとアーティスト ID のないマップ（試しの DB の 26%）が全部候補から落ちる
- 同じアーティストの上限（`mapsPerArtist`）は手札ではなく `params` で、OctantPath の設定から変えられる（[OctantVector 法](../octantvector/law.md) 3.4）
- 公式の手札に「近いアーティスト」（id `artist`、group は「曲」、「曲調と歌声が似た曲」の次）を足す。`weights: {listenbrainz_artists: 1, clap_htsat_unfused: 0.125, mert_v1_95m: 0.125}` で、アーティストの近さで並べ、同じアーティストの中は音の近さで並べる。アーティストの分からない曲は `minViewWeight` で候補から落ちるので出ない（2026-10-13、OctantHarvest #29）
- 公式の手札「すべて」に `listenbrainz_artists: 0.5` を足す（ほかの `clap_htsat_unfused`・`chart_patterns`・`meta_tags` は 1 ずつ）。0.5 は仮の値で、使ってみて決め直す（2026-10-13、OctantHarvest #29）
- 起点の曲のアーティストが分からないときは、「近いアーティスト」も「すべて」と同じ並びになる。`listenbrainz_artists` を名指しするので、「近いアーティスト」「すべて」「似た曲」は関係のビューのない DB では外れる。そういう DB と一緒に `release` しようとすれば止まって気づける（OctantHarvest #29 の実装に合わせて記録）

## 12. 手札はビューを名指しする（2026-10-14）

決定（2026-10-14、OctantCompass #36）: 重み（`weights`・`narrow`・`rank`）のキーはビューの id か id@version だけにし、役割名は札に戻す。どのビューを DB に入れるかは DB を作る人の選択なので、「役割名で書けば DB にあるビューが自動で使われる」形は、作る人が意図しない組み合わせ（たとえば歌声のビューが `music` に混ざる）を招く。手札は自分がどのビューを使うかを書く。

- 役割名を書いた重みは、DB にない名前として `ignoredWeights` に入る（要求）か、その手札が外れる（手札）
- OctantVector 同梱の既定の手札は `all`（重みなし。DB にある `music`・`chart`・`meta` のビューに同じ重み）だけ。ほかの手札はビューを名指しするので DB を作る側が配る
- 公式の手札は OctantHarvest の [`presets/official.json`](https://github.com/BeatOctant/OctantHarvest/blob/main/presets/official.json)（2026.10.15 の DB に入っている）にあり、ここには写さない。「似た曲」「似たマップ」「挑戦」の起点は任意（起点がなければ履歴から）
- OctantPath のお試しの枠は、手札の id を名指しする（song → `song`、chart → `chart`、difficulty → `for_you`、genre → `genre` と `choices.genre`。OctantPath #30。[実装構想の「似ている」の分け方](octantpath-implementation.md#似ているの分け方)）
- 「DB の申告の形は今のまま（役割名とジャンルの語）」（10 節）は変わらない。役割名は `/v1/health` の `db.roles` で申告し、OctantPath は推薦の理由の表示に使う

## 13. 似た曲に言語・カバー・作者を足す（2026-10-20）

マイナーな曲（upvote 2 以下）の「似た曲」が弱い件で、外の DB に頼らずに足せる手がかりを Spike で比べた（[実験ログ](../octantvector/experiments.md#マイナーな曲の言語カバー作者2026-10-19)）。一番よかった組み合わせを、今の「似た曲」と比べられるように別の手札にする。

- 公式の手札に「似た曲（言語・カバー・作者）」（id `song_plus`、group は「曲」、「似た曲」の次）を足す。`weights: {clap_htsat_unfused: 0.5, mert_v1_95m: 0.5, listenbrainz_artists: 0.5, siglip_cover: 0.25, whisper_language: 0.175, beatsaver_mappers: 0.175}`。Spike の「(音 ＋ 0.5 × 近いアーティスト ＋ 0.25 × カバー) / 1.75 ＋ 0.1 × 同じ言語 ＋ 0.1 × 同じ作者」を重みつきの平均に直したもの（同じ並びになる）
- 譜面の作者の関係のビューは、投稿者か共作者の ID のあるマップ全部（BeatSaver では事実上すべて。2026-10-16 のカタログで 145,178 件すべて）にあるので、`minViewWeight` 0.5 でも音だけの候補は落ちない（持っている重みは少なくとも 1.175 / 2.1）
- `whisper_language`、`siglip_cover`、`beatsaver_mappers` のどれかがない DB では、この手札だけが外れる
- 「似た曲」（`song`）は変えない。使って比べてから、どちらを残すかを決める

入れることと、今の「似た曲」と比べられるように手札を分けることは 2026-10-20 に決めた。id・名前・説明・重みは提案のままで、重みは Spike の最良をそのまま換算したもの。
