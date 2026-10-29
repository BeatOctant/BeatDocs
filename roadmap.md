# これからの予定

> 固さ: 予定で、約束ではありません。日付は決めていません。正本: 段階の定義は[憲法の原則 10](constitution.md#10-段階と文書の固さ)、問いの中身は [open.md](open.md)。

BeatOctant の段階ごとに、何が済んでいて何が残っているかの一覧です。問いの中身はここに書き写さず、[open.md](open.md) の番号へリンクします。決まったことは [decisions.md](decisions.md) にあります。

段階は「非公開（探求中）」→「公開（Dev 版）」→「公開（リリース）」です（[憲法の原則 10](constitution.md#10-段階と文書の固さ)）。

## いま: 公開（Dev 版）

誰でも取れる不安定版です（2026-10-24 から）。MOD・OctantCompass・OctantPath Desktop・DB はそれぞれの版で出し、支えるのは各部品の最新の版どうしの組み合わせだけです。利用者に約束するのは「OctantPath のプレイの記録を黙って消さない」だけです（2026-10-21・2026-10-22、[decisions.md](decisions.md#全体と段階)）。

- 推薦の流れ（OctantPath の MOD と OctantPath Desktop → OctantCompass → OctantVector）と、DB を作る流れ（OctantHarvest → OctantVector と OctantVectorPlugins → 配布 DB）は、どちらも動いている
- 署名した配布 DB の全量を作れる（OctantVector 0.4.0 から。[契約5 の非公開と Dev 版の扱い](contracts/distribution.md#非公開探求中の扱い)）
- 利用者向けの文書（[GettingStarted_ja.md](GettingStarted_ja.md)・[GettingStarted_en.md](GettingStarted_en.md)）がある
- ソースの写しは Organization（BeatOctant）に `tools/mirror.py` で置く（2026-10-23）。写しは PR と Issue を受けず、報告は Discord で受ける（2026-10-22）

出し方:

- 各部品の Release の本文は、[CONTRIBUTING の型](CONTRIBUTING.md#release-の本文)で書く。先頭に対応する Beat Saber の版と、記録の作り直し・入れ直し・ペアリングのし直しが要るかを書く
- 報告からどの部品のどの版か分かるようにする。OctantCompass と OctantPath Desktop は窓に版とコミットを出している

非公開（探求中）のあいだに済んだこと（[decisions.md](decisions.md)）:

- フィードバックの受け口は Discord（2026-10-22）。招待リンクを GettingStarted に書いた（2026-10-23）
- BSMG に AI で書いたコードの決まりはない（2026-10-22）
- メニューにいる間は消さず起動直後だけ消す（2026-10-08）。起動直後の自動削除で消す・残すが動くことを開発用の PC で確かめ、自動削除を既定で入にした（2026-10-22）
- 公開する文書に載せる情報と載せない情報の線引き（2026-10-22）と、文書の入口の整理（2026-10-23。公開前の監査で、実装と食い違っていた記述と、写しでたどれないリンクを直した）

## 使いながら決めること

使い始めてからの数字や困りごとで決める問いです。段階には結びつけていません。

- 推薦の定義の D1〜D8、推薦のその後の L1・L2、手札の P1〜P3、近いアーティストの A2〜A4、難易度合わせの F1〜F3（[open.md](open.md)）
- 契約の C2・C11・C14、OctantPath の U1・U4・U5・U6・U7（[open.md](open.md#契約の未決点)、[open.md](open.md#octantpath)）
- OctantVector の実装と決まりの食い違い V4・V5・V7〜V11（[open.md](open.md#octantvector)）
- ゲーム側の未確認の技術 G1〜G5（[open.md](open.md#spike-で確かめること)）

並行して進めているもの:

- Quest 版の OctantPath（[OctantPathAndroid](https://github.com/BeatOctant/OctantPathAndroid)）。ネットにつながない Quest は PC のプロキシで BeatSaver を引く（2026-10-20、[decisions.md](decisions.md#octantpath)）。いつ出すかは U6、Quest しか持たない人のための OctantCompass の置き場所は C14

## その次: 公開（リリース）

誰でも入れられ、配布先の索引から DB を自動で更新する版です（[契約5](contracts/distribution.md)）。

上げる前に要ること:

- 部品の間の契約を「先に決める」に戻す（[憲法の原則 10](constitution.md#10-段階と文書の固さ) の固める時期の (1)）
- 配布先への索引の公開と、OctantCompass の自動の更新（[契約5](contracts/distribution.md)）
- リリースの前に決める問い: C3（DB を重ねる）、C4（検索用の索引）、C5（差分を断ったときのエラー）、C8（repo をまとめるか）、C15（TLS）、U3（BeatSaver からの取得を減らす）（[open.md](open.md#契約の未決点)、[open.md](open.md#octantpath)）

## いつでも

段階に関係なく決めてよい問いです: C9（MOD のビルドの CI）、C10（OctantSpecs の PR の承認）、C12（`ChartsPerMap`）（[open.md](open.md#契約の未決点)）。
