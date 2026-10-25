# OctantSpecs を直すとき

OctantSpecs の文書を書き足したり直したりするときの決まりです。どの文書に何があるかは [README の文書の地図](README.md#文書の地図)にあります。

## 何が起きたら、どこに書くか

| 起きたこと | 書く場所 |
| --- | --- |
| 決まった | いま守る決まりとして、該当する文書に書く。いつ・何を・なぜ決めたかを [decisions.md](decisions.md) の区分に 1 行足す |
| やめた・置き換えた | 該当する文書から消すか書き換え、[decisions.md の「やめたこと・置き換えたこと」](decisions.md#やめたこと置き換えたこと)に 1 行足す（やめた日・やめたこと・理由・代わり）。元の決定の行は消さない |
| 決まっていないことが出た | [open.md](open.md) にだけ書く（番号、問い、いま、いつまでに）。ほかの文書は open.md へリンクする |
| 未決が決まった | open.md から行を消し、上の「決まった」と同じに書く |
| 段階ごとの予定が変わった | [roadmap.md](roadmap.md)。中身は open.md や各文書にリンクし、書き写さない |
| 回数・件数・重みなどの値を変えた | コードに同梱した既定値のファイルだけを直す（下の「値の正本」）。文書には値を書き写さない。値を決めた理由は decisions.md に残す |
| 実装と文書が食い違った | 文書の頭の「固さ」で分ける。固める核なら実装を直さず、open.md に報告として置く。後から記録する層なら、実装に合わせて OctantSpecs を直す PR を出す（まとめて 1 つの PR にしてよい） |
| 確かめずに書いた | 「推測」と書く |

## 文書の決まり

- 憲法と食い違う文書や実装は、憲法に合わせて直します。憲法を変えるときはメンテナーが判断します（[憲法の原則 9](constitution.md#9-ai-が変えてよい範囲と人間の判断が要る範囲)）。
- 主語は書かず、BeatOctant として書きます。決める・承認するなど役割の名前が要るところだけ「メンテナー」と書きます（誰がメンテナーかは [README](README.md#メンテナー)）。考えや課題、手元の環境やデータは、人を主語にせずに書きます（例: 「検討中（日付）」「課題（日付）」「開発用の PC」「開発に使った 1 人分の記録」）。
- このリポジトリはそのまま公開します。人や手元の環境を特定できること（名前、パス、連絡の原文など）と、作業の途中の記録（監査、レビュー、下書き、生のデータ）は書かず、リンクもしません。それらはメンテナーの手元に置き、ここには結論と理由だけを書きます。
- 1 つの事柄は 1 か所にだけ書きます。ほかの文書で必要なときはリンクし、内容を書き写しません。場所によって違うことが書かれているのを防ぐためです。
- 仕様に関わる文書はすべてこのリポジトリに置きます。両方に関わるもの（契約、全体の計画、両方に効く決定）は最上位と `contracts/`、`plans/` に、片方だけに関わるものはリポジトリ名のフォルダ（`octantvector/` など）に置きます。
- 直下の `GettingStarted_ja.md` と `GettingStarted_en.md` は利用者に向けて書き直したもので、仕様の写しとはみなしません。利用者が仕様を読まなくても使えるように書き、仕様へのリンクに頼りません。仕様や画面が変わったら、合わせて直します。「既知の問題」も、直ったものは消し、新しく分かったものは足します。日本語と英語は同じ PR で合わせて直します。
- コードの変更で仕様が変わるときは、コードの PR と一緒にこのリポジトリへの PR も出します。公開（リリース）の前は、契約の形や計画は後から合わせてよい（[憲法の原則 10](constitution.md#10-段階と文書の固さ)）。
- ファイルの場所と、コードが番号で指す節（`plans/presets.md` の節など）は動かしません。消した節は見出しを残します。
- main への変更は PR にし、メンテナーが承認してからマージします。
- BeatOctant に置く公開の写しは PR と Issue を受けません。写しを読んで気づいたことは [Discord の BeatOctant サーバー](https://discord.gg/gx6k3nKZBe)で知らせてもらい、直すのはこのリポジトリの PR で行います。脆弱性の知らせ方は [SECURITY.md](SECURITY.md) にあります。

## 文書の頭の「固さ」と「正本」

各文書の題の下に、次の 1 行があります。

- **固さ**: 固める核（先に決め、実装と食い違ったら報告する）か、後から記録する層（実装が先で、文書を後から合わせる）か。どちらかは[憲法の原則 10](constitution.md#10-段階と文書の固さ)が決めます。
- **正本**: その文書の中身の正本がどこにあるか（この文書、スキーマ、コード）。正本がコードのものは、文書とコードが違えばコードが正しいとみなし、文書を直します。

## 値の正本

回数、件数、重みなどの数値は設定 JSON で変えられるようにします。既定値の正本はコードに同梱した既定値のファイルです。

- OctantPath: `src/OctantPath.Core/Settings/defaults.json`
- OctantCompass: `src/octantcompass/defaults.json`
- OctantHarvest: `src/octantharvest/defaults.json`
- OctantVector: `src/octantvector/common/params.py` と `src/octantvector/generation/config.py`

## 検査

`python3 tools/check.py` が、スキーマ、例、Markdown のリンクと見出しへのリンクを確かめます。PR の CI でも同じものが走ります。

## 公開の写し

Organization BeatOctant の写しは、メンテナーが `python3 tools/mirror.py` で作ります。引数なしは空打ちで、写しを作業フォルダに作り、関所の結果を出すだけです。`--push` を付けたときだけ送ります。外すもの、関所、版のタグの扱い、写しのリポジトリに要る設定は、スクリプトの冒頭に書いています。決めた語の一覧は、どの repo にも入れずに `~/.config/beatoctant/mirror-words.txt` に置きます（[decisions.md](decisions.md#全体と段階) の 2026-10-22・2026-10-23）。

## Release の本文

公開（Dev 版）は、部品ごとの版で出し、形を変えるときはその版の Release の本文に先に書きます（[decisions.md](decisions.md#全体と段階) の 2026-10-22）。写しに `v*` のタグを送ると、写しの CI が実行ファイルを付けた Release の下書きを作ります（OctantPath・OctantCompass・OctantPathAndroid）。下書きの本文は 1 行の決まり文だけなので、メンテナーが公開する前に、次の型で書き直します。

- 本文は英語で書きます。日本語を足すときは、同じ内容を下に続けます。
- 「When you upgrade」は、変わらないものも「no」と書き、空けません。利用者は前の版から上げるときにここだけを読みます。
- 「Pre-release」の印は付けません（探しにくくなるため。Dev 版であることは本文の先頭に書きます）。
- 下書きに付いていないものは、公開する前に手で足します。OctantPath は MOD の DLL（ゲームの入った PC でビルドしたもの。`.pdb` は付けない）、OctantCompass は承認して署名した DB の全量の tar です。

````markdown
**Dev build: unstable, and things may break between versions.** BeatOctant is an unofficial fan project for Beat Saber. It is built mostly with an AI coding agent; people decide and check what goes in. It does not generate maps.

## Works with

- Beat Saber 1.40.8 (PC)  <!-- OctantPathAndroid: Beat Saber <版> (Quest) -->
- The latest release of each other part: OctantPath <vX.Y.Z>, OctantCompass <vX.Y.Z>, DB <dbVersion>

## When you upgrade

- Your OctantPath play records: kept  <!-- 形を変えるときは、どう作り直すかをここに書く -->
- Settings: kept / reset needed
- DB: no re-import needed / import the DB attached to <OctantCompass vX.Y.Z>
- Pairing: no need to pair again / pair OctantPath with OctantCompass again
- Anything else to do: none

## Changes

- <利用者に見える変化を先に、1 行ずつ>

## Files

- <ファイル名>: <何か、どの OS 向けか>
- THIRD-PARTY-NOTICES: the software each executable bundles and their licences

## Known issues and feedback

Known issues are in GettingStarted ([English](https://github.com/BeatOctant/OctantSpecs/blob/main/GettingStarted_en.md) / [日本語](https://github.com/BeatOctant/OctantSpecs/blob/main/GettingStarted_ja.md)). Bug reports and ideas go to `#bug-reports` and `#feedback-ideas` on the [BeatOctant Discord server](https://discord.gg/gx6k3nKZBe).
````
