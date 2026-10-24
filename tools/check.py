"""OctantSpecs の機械的な検査。文書とスキーマのずれを、人が読み比べずに見つけるためのもの。

1. contracts/schemas の JSON Schema と contracts/mod-api.openapi.yaml がスキーマとして正しい
2. すべての $ref が解決できる
3. contracts/examples の例が、examples/schemas.json に書いたスキーマに通る（例はすべて対応付けが要る）
4. Markdown のリンクと見出しへのリンクが、存在するファイルと見出しを指す
5. スキーマの description と x-defaultIn に書いた *.md の場所が存在する

使い方: python3 tools/check.py（jsonschema、referencing、PyYAML が要る。openapi-spec-validator があれば OpenAPI も検査する）
"""
import glob, json, os, re, sys
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "contracts")
BASE = "https://github.com/BeatOctant/OctantSpecs/contracts/"
errors = []


def err(msg):
    errors.append(msg)


def load_schemas():
    resources, docs = [], {}
    for f in sorted(glob.glob(os.path.join(C, "schemas", "**", "*.json"), recursive=True)):
        rel = os.path.relpath(f, C).replace(os.sep, "/")
        d = json.load(open(f, encoding="utf-8"))
        if d.get("$id") != BASE + rel:
            err(f"{rel}: $id は {BASE + rel} にする（いまは {d.get('$id')}）")
        try:
            Draft202012Validator.check_schema(d)
        except Exception as e:  # noqa: BLE001
            err(f"{rel}: スキーマとして正しくない: {e}")
        docs[rel] = d
        resources.append((BASE + rel, Resource.from_contents(d, default_specification=DRAFT202012)))
    api = yaml.safe_load(open(os.path.join(C, "mod-api.openapi.yaml"), encoding="utf-8"))
    docs["mod-api.openapi.yaml"] = api
    resources.append((BASE + "mod-api.openapi.yaml", Resource.from_contents(api, default_specification=DRAFT202012)))
    try:
        from openapi_spec_validator import validate
        validate(api, base_uri="file://" + os.path.join(C, "mod-api.openapi.yaml"))
    except ImportError:
        print("openapi-spec-validator がないので OpenAPI の形の検査を飛ばした")
    except Exception as e:  # noqa: BLE001
        err(f"mod-api.openapi.yaml: OpenAPI として正しくない: {str(e)[:300]}")
    return Registry().with_resources(resources), docs


def check_refs(registry, docs):
    def walk(o, base, where):
        if isinstance(o, dict):
            ref = o.get("$ref")
            if isinstance(ref, str):
                try:
                    registry.resolver(base_uri=base).lookup(ref)
                except Exception:  # noqa: BLE001
                    err(f"{where}: $ref {ref} が解決できない")
            for v in o.values():
                walk(v, base, where)
        elif isinstance(o, list):
            for v in o:
                walk(v, base, where)
    for rel, d in docs.items():
        walk(d, BASE + rel, rel)


def check_examples(registry):
    mapping = json.load(open(os.path.join(C, "examples", "schemas.json"), encoding="utf-8"))
    found = {os.path.relpath(f, os.path.join(C, "examples")).replace(os.sep, "/")
             for f in glob.glob(os.path.join(C, "examples", "*", "*.json"))}
    for f in sorted(found - set(mapping)):
        err(f"examples/{f}: examples/schemas.json に対応するスキーマがない")
    for ex, target in mapping.items():
        p = os.path.join(C, "examples", ex)
        if not os.path.exists(p):
            err(f"examples/schemas.json: {ex} がない")
            continue
        v = Draft202012Validator({"$ref": BASE + target}, registry=registry, format_checker=FormatChecker())
        for e in v.iter_errors(json.load(open(p, encoding="utf-8"))):
            err(f"examples/{ex}: {target} に合わない: {list(e.absolute_path)} {e.message[:200]}")


def slug(h):
    h = re.sub(r"[`*]", "", h.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def slugs(headings):
    """The anchors GitHub gives the headings: a repeated one gets -1, -2, ... in order."""
    seen, out = {}, set()
    for h in headings:
        s = slug(h)
        out.add(f"{s}-{seen[s]}" if s in seen else s)
        seen[s] = seen.get(s, 0) + 1
    return out


def check_markdown():
    files = glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
    anchors = {os.path.normpath(f): slugs(re.findall(r"^#+ (.*)$", open(f, encoding="utf-8").read(), re.M))
               for f in files}
    for f in files:
        text = open(f, encoding="utf-8").read()
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            link = m.group(1)
            if re.match(r"^[a-z]+:", link):
                continue
            path, _, anchor = link.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else os.path.normpath(f)
            rel = os.path.relpath(f, ROOT)
            if not os.path.exists(target):
                err(f"{rel}: リンク先 {link} がない")
            elif anchor and target.endswith(".md") and anchor.lower() not in anchors.get(target, set()):
                err(f"{rel}: 見出し {link} がない")


def check_schema_text(docs):
    md = re.compile(r"((?:[\w.-]+/)*[\w.-]+\.md)(?:#([^\s」）、。`]+))?")
    def walk(o, rel):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("description", "x-defaultIn") and isinstance(v, str):
                    for m in md.finditer(v):
                        p = os.path.join(ROOT, m.group(1))
                        if not os.path.exists(p):
                            err(f"{rel}: {k} の {m.group(1)} がない（リポジトリの根からの場所で書く）")
                else:
                    walk(v, rel)
        elif isinstance(o, list):
            for v in o:
                walk(v, rel)
    for rel, d in docs.items():
        walk(d, rel)


registry, docs = load_schemas()
check_refs(registry, docs)
check_examples(registry)
check_markdown()
check_schema_text(docs)
for e in errors:
    print("NG", e)
print(f"{len(errors)} 件の問題" if errors else "問題なし")
sys.exit(1 if errors else 0)
