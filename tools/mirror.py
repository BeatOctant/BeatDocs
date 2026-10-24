#!/usr/bin/env python3
"""BeatOctant の 7 つのリポジトリを、Organization BeatOctant に履歴を消した写しとして置く。

メンテナーが手で起動する（決まった間隔では回さない。OctantSpecs decisions.md 2026-10-22）。既定は空打ちで、
写しのコミットを手元の作業フォルダに作り、関所を通すところまで行う。--push を付けたときだけ GitHub に送る。

  python3 tools/mirror.py                      # 空打ち。作業フォルダに写しを作り、関所の結果を出す
  python3 tools/mirror.py --push               # 7 つすべてが関所を通ったら、写しの main とタグを送る

前提:
  - 7 つの元のリポジトリが同じフォルダに並んでいる（既定はこのリポジトリの 1 つ上。--src で変える）。
    どれも main にいて、手元の変更がなく、origin/main と同じであること
  - 決めた語の一覧（--words。既定は ~/.config/beatoctant/mirror-words.txt）。メールアドレス、手元の家のパス、
    手元の環境の名前（ホスト名など）を 1 行に 1 つ書く。一覧はどの repo にも入れない（入れると一覧ごと公開される）
  - --push のときは gh（GitHub CLI）。写しのリポジトリの設定を確かめ、送る。写しは https の URL で取って送るので、
    git が https で認証できること（ssh だけで使っている PC では、先に `gh auth setup-git`）

写しの作り方（どれかが守れないときは、何も送らずに止まる）:
  1. 元は git archive の中身だけ。作業中のフォルダのファイル（.gitignore したトークンや鍵、ゲームの DLL）は入らない。
     実行の印（100755）は元のとおりに付ける（CI が scripts/*.sh をそのまま起動するため）
  2. 外すもの（EXCLUDE）を外す。写す最上位のパス（TOP）に無いものがあれば止める（新しく増えたフォルダを黙って写さない）
  3. OWNER（作業用の非公開のリポジトリの持ち主）の 7 つの repo の URL を、ORG の URL にする（ssh の形は https にする）。
     LICENSE の著作権者や MOD の作者の名前は URL ではないので変えない
  4. 他の repo が版のタグ（@v0.8.0、tag = "v0.8.0"、OCTANTVECTOR_TAG）で指す版は、元でそのタグが写す main の最新に
     付いていること（写しにもう同じタグがあればよい）。写しの main の最新に同じタグを付ける。古いタグの中身は写さない
     （古い版の木には main で片付けた記述が残る。2026-10-23）。元の SHA（uv.lock の #<sha> など）は写しの SHA にする
  5. 関所: 決めた語と、セッションの URL・トークン・秘密鍵の形を、ファイルの中身（バイナリも）とパスと、
     写しのコミットの情報から探す。非公開の元を指す URL、写しに無いコミットや PR へのリンク、
     写しに無いパスへの blob/main・tree/main のリンク、self-hosted の runner も止める
  6. 写しのコミットの作者・コミッターは AUTHOR に固定し、本文は決まった文にする（手元の git の設定を使わない）
  7. 写しの main には、前の写しの上にコミットを 1 つ積む（force-push はしない。main の ruleset も force-push と削除を禁じる）。
     中身が前の写しと同じならコミットを積まない。前の写しで付けたタグは付け直さない（同じ元のコミットを指すときだけ通す）。タグは写しで付け直したものだけを送る
     （--tags や --mirror は使わない。元のタグは非公開の履歴を指す）
  8. --push の前に、写しのリポジトリの設定（Issue・PR・Wiki・Projects・Discussions が無効、
     private vulnerability reporting が有効）を確かめる
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

OWNER = "nejiman10"
ORG = "BeatOctant"
AUTHOR = ("BeatOctant", "mirror@beatoctant.invalid")

# 写す順。版のタグで指される側（OctantSpecs、OctantVector）を先にする
ORDER = ["OctantSpecs", "OctantVector", "OctantVectorPlugins", "OctantHarvest", "OctantCompass", "OctantPath", "OctantPathAndroid"]

# 写しに入れないもの（decisions.md 2026-10-22）。dependabot.yml は、写しが PR を受けないので外す
EXCLUDE = {"spikes", "probes", ".claude", "CLAUDE.md", ".github/dependabot.yml"}

# 写す最上位のパス。ここに無いものが元にあれば止める（足すときは、写してよいかを確かめてからここに書く）
COMMON = {".gitattributes", ".github", ".gitignore", "LICENSE", "README.md", "SECURITY.md"}
TOP = {
    "OctantSpecs": COMMON | {"CONTRIBUTING.md", "GettingStarted_en.md", "GettingStarted_ja.md", "octantcompass", "octantharvest",
                          "octantpath", "octantvector", "constitution.md", "contracts", "decisions.md", "open.md", "plans",
                          "roadmap.md", "tools"},
    "OctantVector": COMMON | {"THIRD_PARTY_NOTICES.md", "pyproject.toml", "src", "tests", "uv.lock"},
    "OctantVectorPlugins": COMMON | {"clap", "mert", "siglip", "wavlm", "whisper"},
    "OctantHarvest": COMMON | {"DB-NOTICE.md", "presets", "pyproject.toml", "src", "tests"},
    "OctantCompass": COMMON | {"OCTANTSPECS_REF", "pyproject.toml", "scripts", "src", "tests", "uv.lock"},
    "OctantPath": COMMON | {"OCTANTSPECS_REF", "Directory.Build.props", "docs", "scripts", "src", "tests"},
    "OctantPathAndroid": COMMON | {"OCTANTSPECS_REF", "core", "mod", "proxy", "scripts"},
}

REPOS = "|".join(ORDER)
URL = re.compile(rf"(?P<pre>ssh://git@|git@|https://|@)?github\.com[/:]{OWNER}/(?P<repo>{REPOS})\b")
LEFT_OWNER_URL = re.compile(rf"github\.com[/:]{OWNER}/", re.I)
# 他の repo が版のタグで指すところ（書き換えたあとの形）
PINS = [
    re.compile(rf"github\.com/{ORG}/(?P<repo>{REPOS})(?:\.git)?@(?P<tag>v\d+\.\d+\.\d+)"),
    re.compile(rf"github\.com/{ORG}/(?P<repo>{REPOS})(?:\.git)?\?tag=(?P<tag>v\d+\.\d+\.\d+)"),
    re.compile(rf'github\.com/{ORG}/(?P<repo>{REPOS})(?:\.git)?", tag = "(?P<tag>v\d+\.\d+\.\d+)"'),
    re.compile(r"(?P<repo>OCTANTVECTOR)_TAG: (?P<tag>v\d+\.\d+\.\d+)"),
]
NO_HISTORY_LINK = re.compile(rf"github\.com/{ORG}/(?:{REPOS})/(?:pull|issues|commit|compare)/")
SHA_LINK = re.compile(rf"github\.com/{ORG}/(?P<repo>{REPOS})/(?:blob|tree)/(?P<ref>[0-9a-f]{{7,40}})/")
MAIN_LINK = re.compile(rf"github\.com/{ORG}/(?P<repo>{REPOS})/(?:blob|tree)/main/(?P<path>[^)\s\"'#?>`]+)")
FULL_SHA = re.compile(r"\b[0-9a-f]{40}\b")
# 決めた語の一覧とは別に、いつも止める形
ALWAYS = [
    re.compile(rb"claude\.ai/code/session", re.I),
    re.compile(rb"Claude-Sess(?:ion):", re.I),  # コミットの本文の形（このファイルが自分で止まらないよう分けて書く）
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"xox[abpr]-[A-Za-z0-9-]{10,}"),
    re.compile(rb"hf_[A-Za-z0-9]{30,}"),
]


class Stop(Exception):
    pass


def git(cwd: Path, *args: str, input: bytes | None = None, env: dict | None = None, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, input=input, capture_output=True,
                            env={**os.environ, **(env or {})})
    if check and result.returncode != 0:
        raise Stop(f"git {' '.join(args)}（{cwd}）: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout.decode(errors="replace").strip()


def read_words(path: Path) -> list[bytes]:
    if not path.is_file():
        raise Stop(f"決めた語の一覧がありません: {path}（1 行に 1 つ。どの repo にも入れない場所に置く）")
    words = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    words = [w for w in words if w and not w.startswith("#")]
    if not words:
        raise Stop(f"決めた語の一覧が空です: {path}")
    return [w.encode() for w in words]


def check_source(src: Path) -> str:
    """元が main で、手元の変更がなく、origin/main と同じなら HEAD の SHA を返す。"""
    if git(src, "status", "--porcelain", "--untracked-files=no"):
        raise Stop(f"{src.name}: 手元に未コミットの変更があります")
    if git(src, "rev-parse", "--abbrev-ref", "HEAD") != "main":
        raise Stop(f"{src.name}: main にいません")
    git(src, "fetch", "--quiet", "origin", "main")
    head = git(src, "rev-parse", "HEAD")
    if head != git(src, "rev-parse", "origin/main"):
        raise Stop(f"{src.name}: HEAD が origin/main と違います（pull か push をしてから写す）")
    return head


def export(src: Path, commit: str) -> dict[str, bytes]:
    """コミットの中身を git archive で取り、外すものを外して {パス: 中身} にする。"""
    data = subprocess.run(["git", "archive", "--format=tar", commit], cwd=src, capture_output=True, check=True).stdout
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for member in tar.getmembers():
            if member.isdir() or member.name == "pax_global_header":
                continue
            path = member.name
            if any(path == e or path.startswith(e + "/") for e in EXCLUDE):
                continue
            if not member.isfile():
                raise Stop(f"{src.name}@{commit[:12]}: ファイルでないもの（シンボリックリンクなど）があります: {path}")
            files[path] = tar.extractfile(member).read()
    unknown = {p.split("/")[0] for p in files} - TOP[src.name]
    if unknown:
        raise Stop(f"{src.name}@{commit[:12]}: 写す最上位のパス（TOP）に無いものがあります: {', '.join(sorted(unknown))}")
    return files


def is_text(content: bytes) -> bool:
    if b"\0" in content:
        return False
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def rewrite(text: str) -> str:
    def repl(m: re.Match) -> str:
        pre = m.group("pre") or ""
        head = "@" if pre == "@" else ("https://" if pre else "")
        return f"{head}github.com/{ORG}/{m.group('repo')}"
    return URL.sub(repl, text)


def lines_with(text: str, pattern: re.Pattern) -> list[str]:
    return [f"{n}: {line.strip()[:160]}" for n, line in enumerate(text.splitlines(), 1) if pattern.search(line)]


class Copy:
    """1 つの repo の写し。元のコミットごとに、書き換えたあとの中身を持つ。"""

    def __init__(self, name: str, src: Path, work: Path):
        self.name, self.src, self.dir = name, src, work / name
        self.trees: list[tuple[str, str | None, dict[str, bytes]]] = []  # (元の SHA, 付けるタグ, 中身)
        self.mapped: dict[str, str] = {}  # 元の SHA → 写しの SHA

    def add(self, commit: str, tag: str | None) -> None:
        files = export(self.src, commit)
        for path, content in files.items():
            if is_text(content):
                files[path] = rewrite(content.decode("utf-8")).encode("utf-8")
        self.trees.append((commit, tag, files))


def pins(copies: dict[str, Copy]) -> set[tuple[str, str]]:
    found = set()
    for copy in copies.values():
        for _, _, files in copy.trees:
            for content in files.values():
                if not is_text(content):
                    continue
                text = content.decode("utf-8")
                for pattern in PINS:
                    for m in pattern.finditer(text):
                        repo = "OctantVector" if m.group("repo") == "OCTANTVECTOR" else m.group("repo")
                        found.add((repo, m.group("tag")))
    return found


def gate(copies: dict[str, Copy], words: list[bytes], known: dict[str, set[str]]) -> list[str]:
    """関所。止める理由を返す（空なら通る）。known は repo ごとの元のコミットの SHA（写しに無いものを指していないかを見る）。"""
    problems = []
    lowered = [w.lower() for w in words]
    heads = {name: copy.trees[-1][2] for name, copy in copies.items() if copy.trees}
    for name, copy in copies.items():
        for commit, _, files in copy.trees:
            where = f"{name}@{commit[:12]}"
            for path, content in files.items():
                low = content.lower()
                for w in lowered:
                    if w in path.lower().encode() or w in low or w.decode().encode("utf-16-le") in low:
                        problems.append(f"{where} {path}: 決めた語があります（{w.decode()[:3]}…）")
                for pattern in ALWAYS:
                    if pattern.search(content) or pattern.search(path.encode()):
                        problems.append(f"{where} {path}: {pattern.pattern.decode()} の形があります")
                if not is_text(content):
                    continue
                text = content.decode("utf-8")
                for line in lines_with(text, LEFT_OWNER_URL):
                    problems.append(f"{where} {path}:{line}（非公開の元を指す URL が残っています）")
                for line in lines_with(text, NO_HISTORY_LINK):
                    problems.append(f"{where} {path}:{line}（写しに無い PR・Issue・コミットへのリンクです）")
                for m in SHA_LINK.finditer(text):
                    if m.group("ref") not in copies[m.group("repo")].mapped.values():
                        problems.append(f"{where} {path}: {m.group(0)}（写しに無いコミットへのリンクです）")
                for sha in set(FULL_SHA.findall(text)):
                    for repo, shas in known.items():
                        if sha in shas and sha not in copies[repo].mapped.values():
                            problems.append(f"{where} {path}: {sha}（{repo} の元のコミットで、写しにありません）")
                if path.startswith(".github/workflows/") and "self-hosted" in text:
                    problems.append(f"{where} {path}: self-hosted の runner は写しに付けません")
                if commit == copy.trees[-1][0]:
                    for m in MAIN_LINK.finditer(text):
                        target, linked = heads.get(m.group("repo"), {}), m.group("path").rstrip(".,")
                        if not any(p == linked or p.startswith(linked.rstrip("/") + "/") for p in target):
                            problems.append(f"{where} {path}: {m.group(0)}（写しの main にそのパスがありません）")
    return problems


def source_commits(src: Path) -> set[str]:
    return set(git(src, "rev-list", "--all").split())


def prepare(copy: Copy, push: bool) -> str | None:
    """写しの作業用の clone を用意し、写しの main の先端の SHA（空なら None）を返す。"""
    if copy.dir.exists():
        shutil.rmtree(copy.dir)
    url = f"https://github.com/{ORG}/{copy.name}.git"
    clone = subprocess.run(["git", "clone", "--quiet", url, str(copy.dir)], capture_output=True,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if clone.returncode != 0:
        if push:
            raise Stop(f"{url} を取れません。先に Organization にリポジトリを作ってください: {clone.stderr.decode().strip()}")
        copy.dir.mkdir(parents=True)
        git(copy.dir, "init", "--quiet", "--initial-branch=main")
        return None
    # 写しの既定のブランチに関わらず、写しの main の上に積む
    has_main = git(copy.dir, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/main", check=False)
    git(copy.dir, "checkout", "--quiet", "-B", "main", *(["origin/main"] if has_main else []))
    return git(copy.dir, "rev-parse", "--verify", "--quiet", "HEAD", check=False) or None


def remote_tags(copy: Copy) -> dict[str, str]:
    out = git(copy.dir, "tag", "--list", "--format=%(refname:short) %(objectname)")
    return dict(line.split() for line in out.splitlines() if line)


def commit(copy: Copy, source: str, tag: str | None, files: dict[str, bytes], date: str) -> str:
    for entry in copy.dir.iterdir():
        if entry.name != ".git":
            shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    for path, content in files.items():
        target = copy.dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    # 実行の印は git archive の中身ではなく元の木から取る
    for line in git(copy.src, "ls-tree", "-r", source).splitlines():
        mode, _, _, path = line.split(None, 3)
        if mode == "100755" and path in files:
            (copy.dir / path).chmod(0o755)
    git(copy.dir, "add", "--all")
    if git(copy.dir, "rev-parse", "--verify", "--quiet", "HEAD", check=False) and \
            not git(copy.dir, "diff", "--cached", "--name-only"):
        return git(copy.dir, "rev-parse", "HEAD")  # 前の写しと同じ中身なら、コミットを積まない
    message = f"{copy.name} の写し（{date}{'、' + tag if tag else ''}）\n\n元のコミット: {source[:12]}\n"
    env = {"GIT_AUTHOR_NAME": AUTHOR[0], "GIT_AUTHOR_EMAIL": AUTHOR[1], "GIT_COMMITTER_NAME": AUTHOR[0],
           "GIT_COMMITTER_EMAIL": AUTHOR[1], "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    git(copy.dir, "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", message, env=env)
    sha = git(copy.dir, "rev-parse", "HEAD")
    if tag:
        git(copy.dir, "tag", tag, sha)
    return sha


def check_settings(name: str) -> list[str]:
    """写しのリポジトリの設定を gh で確かめる。"""
    def api(path: str) -> dict:
        import json
        out = subprocess.run(["gh", "api", path], capture_output=True)
        if out.returncode != 0:
            raise Stop(f"gh api {path}: {out.stderr.decode().strip()}")
        return json.loads(out.stdout)
    repo = api(f"repos/{ORG}/{name}")
    problems = []
    for key in ["has_issues", "has_wiki", "has_projects", "has_discussions", "has_pull_requests"]:
        if repo.get(key, False):
            problems.append(f"{ORG}/{name}: {key} が有効です（Settings > General > Features で切る）")
    if repo.get("private"):
        problems.append(f"{ORG}/{name}: private です")
    try:
        reporting = api(f"repos/{ORG}/{name}/private-vulnerability-reporting").get("enabled")
    except Stop:  # private の repo では GitHub が 404 を返す
        reporting = False
    if not reporting:
        problems.append(f"{ORG}/{name}: private vulnerability reporting が無効です（Settings > Security）")
    return problems


def main() -> int:
    here = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", type=Path, default=here.parent, help="7 つの元のリポジトリが並ぶフォルダ")
    parser.add_argument("--work", type=Path, help="写しを作る作業フォルダ（既定は一時フォルダ）")
    parser.add_argument("--words", type=Path, default=Path.home() / ".config/beatoctant/mirror-words.txt")
    parser.add_argument("--push", action="store_true", help="関所を通ったら写しの main とタグを送る")
    args = parser.parse_args()
    work = args.work or Path(tempfile.mkdtemp(prefix="beatoctant-mirror-"))
    date = dt.date.today().isoformat()
    try:
        words = read_words(args.words)
        copies: dict[str, Copy] = {}
        for name in ORDER:
            src = args.src / name
            head = check_source(src)
            copy = copies[name] = Copy(name, src, work)
            copy.base = prepare(copy, args.push)
            copy.tags = remote_tags(copy)
            # 前の写しのタグが元の同じ名前のタグと同じコミットから作られていれば、元の SHA をその写しの SHA に付け替える
            for tag in copy.tags:
                old = git(src, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{commit}}", check=False)
                made = git(copy.dir, "log", "-1", "--format=%B", f"{tag}^{{commit}}")
                if old and f"元のコミット: {old[:12]}" in made:
                    copy.mapped[old] = git(copy.dir, "rev-parse", f"{tag}^{{commit}}")
            copy.kept = {}  # 前の写しで付けたタグのうち、同じ元のコミットを指すもの（付け直さない）
            for tag in git(src, "tag", "--points-at", head).split():
                if tag in copy.tags:
                    made = git(copy.dir, "log", "-1", "--format=%B", f"{tag}^{{commit}}")
                    if f"元のコミット: {head[:12]}" not in made:
                        raise Stop(f"{name}: タグ {tag} は写しにもう別のコミットであります")
                    copy.kept[tag] = git(copy.dir, "rev-parse", f"{tag}^{{commit}}")
            copy.head = head
        for name in ORDER:
            copy = copies[name]
            copy.add(copy.head, None)
            copy.head_tags = sorted(t for t in git(copy.src, "tag", "--points-at", copy.head).split() if t not in copy.kept)
        # 版のタグで指される版は、写す main の最新に付いたタグだけ（古いタグの中身は写さない）
        for repo, tag in sorted(pins(copies)):
            copy = copies[repo]
            if tag not in copy.tags and tag not in copy.head_tags:
                raise Stop(f"{repo}: 他の repo が {tag} を指していますが、元の main の最新にそのタグがありません"
                           f"（写す前に、元の main の最新に新しい版のタグを付け、指す側をその版にする）")
        # 写しのコミットを作る。版のタグの元の SHA（uv.lock の #<sha> など）は、作った写しの SHA にする
        for name in ORDER:
            copy = copies[name]
            for i, (source, tag, files) in enumerate(copy.trees):
                for path, content in files.items():
                    if is_text(content):
                        text = content.decode("utf-8")
                        for other in copies.values():
                            for old, new in other.mapped.items():
                                text = text.replace(old, new)
                        files[path] = text.encode("utf-8")
                last = i == len(copy.trees) - 1
                sha = commit(copy, source, tag, files, date)
                # 前の写しのタグが同じ元を指すなら、元の SHA はそのタグの写しの SHA にする（uv.lock の #<sha> とタグを揃える）
                copy.mapped[source] = next(iter(copy.kept.values()), sha) if last else sha
                if last:
                    for head_tag in copy.head_tags:
                        git(copy.dir, "tag", head_tag, sha)
        known = {name: source_commits(copies[name].src) for name in ORDER}
        problems = gate(copies, words, known)
        for name in ORDER:
            copy = copies[name]
            info = git(copy.dir, "log", "--format=%an <%ae>%n%cn <%ce>%n%B", f"{copy.base}..HEAD" if copy.base else "HEAD")
            for w in words:
                if w.decode().lower() in info.lower():
                    problems.append(f"{name}: 写しのコミットの情報に決めた語があります")
            for pattern in ALWAYS:
                if pattern.search(info.encode()):
                    problems.append(f"{name}: 写しのコミットの情報に {pattern.pattern.decode()} の形があります")
        if args.push:
            for name in ORDER:
                problems += check_settings(name)
        for name in ORDER:
            copy = copies[name]
            new_tags = [t for _, t, _ in copy.trees if t] + copy.head_tags
            added = len(git(copy.dir, "rev-list", f"{copy.base}..HEAD" if copy.base else "HEAD").split())
            print(f"{name}: {added} コミット（{', '.join(new_tags) or '新しいタグなし'}） -> {copy.dir}")
        if problems:
            print(f"\n関所で止めました（{len(problems)} 件）。何も送っていません:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        if not args.push:
            print("\n関所を通りました。空打ちなので何も送っていません（送るときは --push）")
            return 0
        for name in ORDER:
            copy = copies[name]
            refs = ["HEAD:refs/heads/main"] + [f"refs/tags/{t}" for _, t, _ in copy.trees if t] + \
                   [f"refs/tags/{t}" for t in copy.head_tags]
            git(copy.dir, "push", "--quiet", "origin", *refs)
            print(f"{name}: 送りました")
        return 0
    except Stop as stop:
        print(f"止めました: {stop}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
