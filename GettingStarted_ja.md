# BeatOctant をはじめる（Dev 版）

BeatOctant は、Beat Saber で次に遊ぶ曲を、あなたのプレイの記録から推薦する仕組みです。BeatSaver のマップから作った推薦用のデータ（DB）を手元の PC で使い、推薦の計算もすべて手元で行います。

[English](GettingStarted_en.md)

> - **Dev 版（不安定版）です。** 壊れることがあります。Windows では未確認です。[既知の問題](#既知の問題)も見てください。
> - **非公式です。** Beat Games・Meta とは関係のない、ファンが作った MOD とツールです。
> - **コードは主に AI（Anthropic の Claude）で書いています。** 何を作るかは人が決め、変更はすべて人が確かめてから取り込みます。BeatOctant はマップを作りません。BeatSaver にあるマップを推薦するだけです。
> - 困ったときや感想は、Discord の [BeatOctant サーバー](https://discord.gg/gx6k3nKZBe)へ（日本語でも英語でも）。

## 必要なもの

### システム要件

| 項目 | 要求 |
| --- | --- |
| OS | Windows 10・11（WebView2 を使う。動作は確かめていません）または Linux |
| Beat Saber | OctantPath のリリースの本文の「Works with」に書いた版（動作を確かめた版） |
| メモリ | ゲームのほかに 2 GB 以上の空き（OctantCompass が DB を読み込む） |
| ディスク | DB のファイルの 2 倍ほどの空き（取り込みで展開する） |
| Linux: Beat Saber | Steam の Proton で動かす |
| Linux: OctantCompass | WebKitGTK 4.1 と GTK 3（Debian・Ubuntu は `libwebkit2gtk-4.1-0`、Fedora は `webkit2gtk4.1`、Arch は `webkit2gtk-4.1`）。Ubuntu 24.04 で確認 |
| Linux: OctantPath Desktop | WebKitGTK 4.1 と libnotify（Debian・Ubuntu は `libwebkit2gtk-4.1-0` と `libnotify4`） |
| Linux: ファイルの選択 | zenity または kdialog（なければパスを手で入れる） |

### MOD

どれもゲームの版に合うものを入れます（MOD の管理ツールが選ぶもの）。必須の MOD の下限の版は、OctantPath の MOD の `manifest.json` の `dependsOn` にあります。

| MOD | |
| --- | --- |
| BSIPA | 必須 |
| SiraUtil | 必須 |
| BeatSaberMarkupLanguage | 必須 |
| SongCore | 必須 |
| BeatSaberPlaylistsLib | 必須 |
| BeatSaverVoting | 任意。Upvote・Downvote を推薦と、取った曲を残す・消す判断に使う |

## 取るもの

| もの | 何をするか |
| --- | --- |
| [OctantPath](https://github.com/BeatOctant/OctantPath/releases)（`OctantPath.dll`） | Beat Saber の MOD。ゲームの中で推薦を出し、曲を取ってきて入れ替える |
| [OctantCompass](https://github.com/BeatOctant/OctantCompass/releases) | ゲームの外で動く推薦のサーバー。DB を読み、OctantPath に推薦を返す |
| [DB](https://github.com/BeatOctant/OctantCompass/releases)（`<版>.full.tar`） | 推薦に使うデータ。音と譜面から計算した数値で、音や譜面そのものは入っていない |
| [OctantPath Desktop](https://github.com/BeatOctant/OctantPath/releases) | ゲームを起動せずに、PC の画面で推薦を見て曲を選ぶ道具。なくても使える |

## 入れ方

1. `OctantPath.dll` を、ゲームのフォルダの `Plugins` に置きます。
2. OctantCompass を起動します。Linux では Linux 向けのものを Proton を通さずに動かします（`chmod +x` が要ります。端末からは `./octantcompass-… gui`）。
3. OctantCompass の「詳細設定」→「ファイルから取り込む」で、DB のファイル（`.tar`）を選ぶかパスを入れ、「取り込む」を押します。取り込んだあとは、元のファイルを消してかまいません。
4. 窓の右上の印が塗った丸と「準備完了」になれば使えます。使っていない間（既定は 30 分）は DB を手放して輪と「休止中」になりますが、要求が来るとまた読み込むので、そのまま使えます。ひし形は止まっています。
5. ペアリングします（最初の 1 回。同じ PC でも要ります）。
   1. OctantCompass の「状態」で「ペアリングの合言葉」を押します（6 桁。5 分で無効）。
   2. Beat Saber の左のメニューの「OctantPath」→「OctantCompass との接続」で合言葉を入れ、「ペアリング」を押します。同じ PC なら、つなぐ先は空のままにします。
   3. 「接続済」と出ればつながっています。

OctantCompass は、ゲームより先に起動しておきます。「詳細設定」の「ログイン時に起動する」で自動にできます（Windows では未確認）。

OctantPath Desktop も、「設定」のタブで同じように合言葉を入れてつなぎます。Desktop は、ゲームとは別の環境としてつながります。

## 使い方

- **ミックス**: 曲選択で曲を選び、「ミックス」を押して種類を選ぶと、その曲を起点にした並びの「下見」が出ます。合わない曲は「⇔」で入れ替えるか「✕」で外し、「曲を足す」で 1 曲ずつ足せます（20 曲まで）。取り終えた曲は「▶」で、曲選択でその曲を選べます（遊び終えて戻ると下見が開き直ります）。よければ「作成」を押すと、並んだ曲を取得してプレイリスト「OctantPath のミックス」を開きます（作るたびに置き換わります）。残したい並びは「保存」で別のプレイリストにします。
- **推薦の板**: 曲選択の上に浮かぶ板で、並びの曲を試聴し、「取得」で取って曲選択で選べます。「自動で次へ」を入れると、遊び終えて戻ったときに並びの次の曲を選びます。
- **プレイの記録が推薦に効きます**: クリア、失敗、お気に入り、Upvote を使います。遊び始めは記録が少ないので、推薦は大まかです。記録が増えれば合いやすくなることをねらっていますが、確かめきれていません。
- **Desktop**: ゲームを起動せずに、起点の曲と種類を選んで推薦を見られます。試聴して、ArcViewer で譜面を見て、プレイリストを作れます。

### 取った曲（お試し）の扱い

OctantPath が取った曲は、お試しとして `UserData/OctantPath/Levels` に置き、ふだんの `CustomLevels` とは分けています。下見の「↓」や「作成」で取った曲も、お試しです。

既定では、ゲームを起動したときに、お気に入りや Upvote にした曲と何度か遊んだ曲を `CustomLevels` へ移し、Downvote にした曲、しばらく（既定は 15 起動日）遊ばなかった曲、「お試しの曲の合計の上限」を超えた分の古い曲を消します。ほかのプレイリストに入っている曲は消しません。消すのは OctantPath が取ったお試しの曲だけで、自分で入れた曲とプレイの記録には触れません。

消したくないときは、設定の「お試しの曲を自動で消す」を切ります。切ると、消すことも移すこともせず、そうするはずだった曲をログに書くだけになります。`settings.json` が読めないときや、期限・上限に 0 以下の値が書かれているときは、何も消しません。

## 通信

### 外部のサービスへ送るもの

ありません。プレイの記録（精度を含む）は、外部のサービスへは送りません。BeatOctant はスコアも送りません。ScoreSaber や BeatLeader の MOD を入れていれば、推薦の曲を遊んだときも、その MOD がいつもどおり送ります。OctantPath はそれを止めも変えもしません。

### 曲の取得に伴う通信

- **BeatSaver**: 曲の情報、カバー、試聴、マップの zip。OctantPath と OctantPath Desktop が、あなたが選んだ曲や、推薦に出た曲の分だけ取ります。間隔を空けて取り、BeatSaver に負担をかけないようにしています。
- **GitHub**: OctantPath Desktop が初回に、譜面のプレビューに使う ArcViewer（GPLv3、約 80 MB）を、決めた版だけ取ります。

### OctantPath と OctantCompass の間の通信

プレイの記録は、推薦を手元で計算するために、ペアリングした OctantCompass に渡します。同じ PC なら `127.0.0.1` の中で済みます。ペアリングで別の PC の OctantCompass をつなぐ先にすると、記録はその PC へ LAN で渡ります。OctantCompass はペアリングした OctantPath の要求にだけ答え、自分から外へつなぐのは「索引から取り込む」で DB を取るときだけです（Dev 版では使いません）。

### DB の利用条件

CC BY-NC-SA 4.0 です。非営利で、同じ条件でなら共有できます。利用条件とクレジットは DB の中に入っていて、OctantCompass の「詳細設定」の DB の欄で読めます。

## 既知の問題

- **Windows で試せていません。** Windows 向けの OctantCompass と OctantPath Desktop はビルドしただけで、Linux（Proton）でしか動かしていません。Windows での結果を教えてください。
- **推薦の質を確かめきれていません。** メンテナーが手首と右肘を痛めていて、長く遊んでの確認ができていません。合う・合わない、多すぎる・少なすぎるなどの感想を教えてください。
- **推薦の種類（手札）が多めです。** 使われ方が分かってから絞ります。
- **ゲーム中の曲の追加・削除がゲームとぶつからないか、確かめきれていません。** ゲームの中の画面にも、作れる形に限りがあります。
- **更新で壊れることがあります。** 各部品と DB は最新の版にそろえてください。更新で DB の取り込み直しやペアリングのし直しが要ることがあります。OctantPath のプレイの記録（`UserData/OctantPath`）は黙って消しません。作り直しが要るときは、その版の説明に先に書きます。
- **Quest 版（OctantPathAndroid）は対象外です。** 極めて初期で、ビルド済みの配布もありません。

## 困ったとき

| 出ること | 確かめること |
| --- | --- |
| 「OctantCompass につながりません」 | OctantCompass が動いているか（窓が開くか）。ゲームを起動する前に OctantCompass を起動しておく |
| 「ペアリングが必要です」「ペアリングを断られました」 | OctantCompass の窓で合言葉を出し直して入れる（5 分で無効、5 回間違えると無効） |
| 「準備中」 | OctantCompass が DB を読み込んでいる。少し待つ |
| 「推薦は使えません」 | OctantCompass の「状態」の理由を見る。DB のファイルを取り込み直す |
| 「版が合いません」 | OctantPath と OctantCompass を、どちらも最新の版にそろえる |
| 推薦が少ない、出ない | 起点の曲が DB にないことがある。ほかの曲で試す |

知らせるときは、[Discord の BeatOctant サーバー](https://discord.gg/gx6k3nKZBe)の `#bug-reports` に、次のものを送ってください。ログにはフォルダのパス（ユーザー名を含むことがあります）や遊んだ曲の名前が入ります。送る前に、知られたくないものが入っていないか確かめてください。

- 何をしたら、何が起きたか（スクリーンショットがあると助かります）
- ゲームのフォルダの `Logs/_latest.log`。OctantPath のログは、ゲーム全体のログの中に `OctantPath` と付いた行で入っています。前に起動したときのものは、同じフォルダに日時の名前の `.log.gz` で残っています
- OctantCompass の「状態」とログ（窓からコピー）
- 推薦の感想を送るときは、OctantPath の設定の「推薦のまとめを書き出す」で書いたファイル（`UserData/OctantPath/summaries/`）。中身は種類ごとの数と最近の推薦で、プレイの記録の一部です。送るかは任意です

## やめるとき

- **OctantPath**: `Plugins/OctantPath.dll` を消します。記録を残したくなければ、`UserData/OctantPath` と `Playlists/OctantPath` も消します。OctantPath が取った曲は `UserData/OctantPath/Levels` にあります。
- **OctantCompass**: 「ログイン時に起動する」を入れていたら、先に窓で切ります。「停止」で止めてから、実行ファイルを消します。データは、Windows は `%LOCALAPPDATA%\OctantCompass` に、Linux は `~/.config/OctantCompass`、`~/.local/state/OctantCompass`、`~/.local/share/OctantCompass` にあります。
- **OctantPath Desktop**: 実行ファイルを消します。データは、Windows は `%LOCALAPPDATA%\OctantPath\Desktop` に、Linux は `~/.config/OctantPath/Desktop`、`~/.local/state/OctantPath/Desktop`、`~/.local/share/OctantPath/Desktop`、`~/.cache/OctantPath/Desktop` にあります。使っている場所は Desktop の「設定」のタブに出ます。
- **DB**: OctantCompass のデータ（上の場所の `dbs`）にあります。OctantCompass のデータと一緒に消えます。

OctantPath は、ゲームのほかのファイル（PlayerData、お気に入り、投票の記録、スコア、リプレイ）を読むだけで、書き換えません。
