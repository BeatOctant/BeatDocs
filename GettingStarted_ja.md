# BeatOctant をはじめる（Dev 版）

BeatOctant は、Beat Saber で次に遊ぶ曲を、あなたのプレイの記録から推薦する仕組みです。BeatSaver のマップから作った推薦用のデータ（DB）を手元の PC で使い、推薦の計算もすべて手元で行います。

[English](GettingStarted_en.md)

## 既知の問題

これは誰でも取れる Dev 版（不安定版）です。先に、分かっている弱いところを書いておきます。

- **Windows で試せていません。** 手元に Windows の PC がなく、Windows 向けの OctantCompass と OctantPath Desktop はビルドしただけです。Linux（Proton）でしか動かしていません。Windows で動いた・動かなかったを教えてもらえると、とても助かります。
- **推薦の質を確かめきれていません。** 作っている本人が Beat Saber を振りすぎて、手首と右肘を痛めています。次に遊ぶ曲を推薦する道具を作りながら、自分は遊べなくなりました。そのため、長く続けて遊ぶ確かめができていません。合う・合わない、多すぎる・少なすぎるなど、遊んでみた感想を教えてください。
- **推薦の種類（手札）が多めです。** 選ぶ種類がたくさん並びます。使われるもの・使われないものが分かってから絞ります。
- **技術的に難しいところが残っています。** ゲームの中の画面には作れる形に限りがあり、遊んでいる間に曲を足したり消したりする動きも、ゲームとぶつからないか確かめきれていません。DB は読み込むと 2 GB ほどメモリを使います。
- **更新で壊れることがあります。** OctantPath・OctantCompass・OctantPath Desktop・DB は、それぞれの最新の版にそろえて入れてください。更新のたびに、DB の取り込み直しや、ペアリングのし直しが要ることがあります。OctantPath のプレイの記録（`UserData/OctantPath`）は黙って消しません。作り直しが要るときは、その版の説明に先に書きます。

困ったときや気づいたことは、遠慮なく知らせてください。送り先は Discord の [BeatOctant サーバー](https://discord.gg/gx6k3nKZBe)です。バグは `#bug-reports` に、推薦の当たり外れや案は `#feedback-ideas` に書いてください。日本語でも英語でもかまいません（日本語の雑談は `#日本語`）。

BeatOctant のコードは、主に AI のコーディングエージェント（Anthropic の Claude）で書いています。何を作るかは人が決め、変更はすべて人が確かめてから取り込みます。BeatOctant はマップを作りません。BeatSaver にあるマップを推薦するだけです。

## 取るもの

Windows 向けと Linux 向けがあります。ファイルの名前には、版と OS が付いています。OctantPath と OctantPath Desktop は [OctantPath の Releases](https://github.com/BeatOctant/OctantPath/releases) に、OctantCompass と DB は [OctantCompass の Releases](https://github.com/BeatOctant/OctantCompass/releases) に置きます。

| もの | ファイル | 何をするか |
| --- | --- | --- |
| OctantPath | `OctantPath.dll` | Beat Saber の MOD。ゲームの中で推薦を出し、曲を取ってきて入れ替える。Windows と Linux で同じもの |
| OctantCompass | `octantcompass-…`（Windows は `.exe`） | ゲームの外で動く推薦のサーバー。DB を読み、OctantPath に推薦を返す |
| DB | `<版>.full.tar`（ファイル 1 つ） | 推薦に使うデータ。音と譜面から計算した数値で、音や譜面そのものは入っていない |
| OctantPath Desktop | `OctantPath.Desktop-…`（Windows は `.exe`） | ゲームを起動せずに、PC の画面で推薦を見て曲を選ぶ道具。なくても使える |

Quest 版（OctantPathAndroid）は、この手順には入れていません。極めて初期で不安定で、ビルド済みの配布もまだありません。

## 外へ出るもの

- **BeatSaver から取るもの**: 曲の情報、カバー、試聴、マップの zip。OctantPath と OctantPath Desktop が、あなたが選んだ曲や、推薦に出た曲の分だけ取ります。間隔を空けて取り、BeatSaver に負担をかけないようにしています。
- **Desktop が初回に取るもの**: 譜面のプレビューに使う ArcViewer（GPLv3、約 80 MB）。GitHub から、決めた版だけを取ります。
- **プレイの記録**: どこにも送っていません。記録（精度を含む）は、推薦を手元で計算するために、ペアリングした OctantCompass に渡すだけです。
- **スコア**: BeatOctant はスコアを送りません。ScoreSaber や BeatLeader の MOD を入れていれば、推薦の曲を遊んだときも、その MOD がいつもどおり送ります。OctantPath はそれを止めも変えもしません。
- **DB の利用条件**: CC BY-NC-SA 4.0 です。非営利で、同じ条件でなら共有できます。利用条件とクレジットは DB の中に入っていて、OctantCompass の「詳細設定」の DB の欄で読めます。

## 入れ方

### 1. OctantPath（MOD）

1. Beat Saber を **1.40.8** にします。OctantPath はこの版だけで動きます。
2. 次の MOD を入れます。BSManager などで入れられます（Windows は ModAssistant も使えます）。
   - BSIPA（4.3.6 以上）
   - SiraUtil（3.2.1 以上）
   - BeatSaberMarkupLanguage（1.12.5 以上）
   - SongCore（3.15.3 以上）
   - BeatSaberPlaylistsLib（1.7.2 以上）
3. `OctantPath.dll` を、ゲームのフォルダの `Plugins` に置きます。

Linux では、Beat Saber を Steam の Proton で動かします。MOD の入れ方は Windows と同じで、ゲームのフォルダは Steam のライブラリの中にあります（ふつうは `~/.local/share/Steam/steamapps/common/Beat Saber`）。

### 2. OctantCompass と DB

1. OctantCompass の実行ファイルを好きなフォルダに置き、ダブルクリックします。OctantCompass の窓が開きます。
2. 窓の「詳細設定」のタブの「ファイルから取り込む」で、DB のファイル（`.tar`）を「選ぶ…」から選ぶか、パスを入れて、「取り込む」を押します。「選ぶ…」で何も開かないときは、パスを入れてください。OctantCompass が DB を確かめて自分のデータの置き場所に展開するので、データの置き場所のあるディスクに、ファイルの 2 倍ほどの空き容量が要ります。取り込んだあとは、取ったファイルを消してかまいません。
3. 「状態」のタブで「準備完了」になれば、準備はできています。DB は読み込むと 2 GB ほどメモリを使います。使っていない間（既定は 30 分）は手放して「休止中」になり、OctantPath から要求が来るとまた読み込みます。

OctantCompass は、ゲームを起動する前に起動しておきます。毎回起動するのが面倒なら、「詳細設定」の「ログイン時に起動する」を入れます（Windows では未確認です）。入れてもログインのあとに動いていないときは、自分で起動してください。

OctantCompass は、つないだ OctantPath の要求にだけ答えます。OctantCompass が自分から外へつなぐのは、「索引から取り込む」で DB を取るときだけです。Dev 版では使いません。

Linux では、OctantCompass と OctantPath Desktop は Linux 向けのものを、Proton を通さずにそのまま動かします。取ったら、実行の許可を付けます（`chmod +x octantcompass-… OctantPath.Desktop-…`）。端末から OctantCompass を動かすときは、`./octantcompass-… gui` のように `gui` を付けます。「選ぶ…」には zenity か kdialog が要ります。

## ペアリング（最初の 1 回）

OctantPath と OctantCompass は、合言葉で 1 回つなぎます。同じ PC でも必要です。

1. OctantCompass の窓の「状態」のタブで、「ペアリングの合言葉」を押します（6 桁の数字。5 分で無効になります）。
2. Beat Saber を起動し、左のメニューの「OctantPath」を押します。
3. 「OctantCompass との接続」で、合言葉を入れて「ペアリング」を押します。つなぐ先は、同じ PC なら空のままにします。
4. 「接続済」と出ればつながっています。

OctantPath Desktop も、「設定」のタブで同じように合言葉を入れてつなぎます。Desktop は、ゲームとは別の環境としてつながります。

## 使い方

- **ミックス**: 曲選択で曲を選び、「ミックス」を押して種類を選ぶと、その曲を起点にした並びの「下見」が出ます。合わない曲は「⇔」で入れ替えるか「✕」で外し、「曲を足す」で 1 曲ずつ足せます（20 曲まで）。取り終えた曲は「▶」で、曲選択でその曲を選べます（遊び終えて戻ると下見が開き直ります）。よければ「作成」を押すと、並んだ曲を取得してプレイリスト「OctantPath のミックス」を開きます（作るたびに置き換わります）。残したい並びは「保存」で別のプレイリストにします。
- **推薦の板**: 曲選択の上に浮かぶ板で、並びの曲を試聴し、「取得」で取って曲選択で選べます。「自動で次へ」を入れると、遊び終えて戻ったときに並びの次の曲を選びます。
- **遊ぶほど合っていく**: クリア、失敗、お気に入り、Upvote が推薦に効きます。遊び始めは記録が少ないので、推薦は大まかです。
- **取得した曲**: OctantPath が取った曲は、お試しとして `UserData/OctantPath/Levels` に置き、ふだんの `CustomLevels` とは分けています。下見の「↓」や「作成」で取った曲も、お試しです。既定では、ゲームを起動したときに、お気に入りや Upvote にした曲と何度か遊んだ曲を `CustomLevels` へ移し、Downvote にした曲、しばらく（既定は 15 起動日）遊ばなかった曲、「お試しの曲の合計の上限」を超えた分の古い曲を消します。ほかのプレイリストに入っている曲は消しません。消すのは OctantPath が取ったお試しの曲だけで、自分で入れた曲とプレイの記録には触れません。消したくないときは、設定の「お試しの曲を自動で消す」を切ります。切ると、消すことも移すこともせず、そうするはずだった曲をログに書くだけになります。`settings.json` が読めないときや、期限・上限に 0 以下の値が書かれているときは、何も消しません。
- **Desktop**: ゲームを起動せずに、起点の曲と種類を選んで推薦を見られます。試聴して、ArcViewer で譜面を見て、プレイリストを作れます。

## 困ったとき

| 出ること | 確かめること |
| --- | --- |
| 「OctantCompass につながりません」 | OctantCompass が動いているか（窓が開くか）。ゲームを起動する前に OctantCompass を起動しておく |
| 「ペアリングが必要です」「ペアリングを断られました」 | OctantCompass の窓で合言葉を出し直して入れる（5 分で無効、5 回間違えると無効） |
| 「準備中」 | OctantCompass が DB を読み込んでいる。少し待つ |
| 「推薦は使えません」 | OctantCompass の「状態」の理由を見る。DB のファイルを取り込み直す |
| 「版が合いません」 | OctantPath と OctantCompass を、どちらも最新の版にそろえる |
| 推薦が少ない、出ない | 起点の曲が DB にないことがある。ほかの曲で試す |

知らせるときは、[Discord の BeatOctant サーバー](https://discord.gg/gx6k3nKZBe)の `#bug-reports` に、次のものを送ってください。

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
