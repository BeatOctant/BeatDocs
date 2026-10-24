# 契約1（OctantCompass・OctantHarvest → OctantVector）の出力の例

[契約1 推薦側（OctantCompass → OctantVector）](../../engine-runtime.md#公開する関数)の関数の戻り値の例です。2026-10-07 に決めた形で、契約1（OctantCompass・OctantHarvest → OctantVector）の一部として扱います。OctantCompass はこの例で OctantVector の代役（`FakeVectorEngine`）を作り、契約3（OctantPath ↔ OctantCompass）の形に変えるのは OctantCompass の `api` です。

- 例は[スキーマ](../../schemas/engine-runtime/)に合います。どの例がどのスキーマに合うかは [examples/schemas.json](../schemas.json) にあり、[tools/check.py](../../../tools/check.py) が確かめます
- 項目の形と意味は、スキーマの `description` にあります
- `hash` はすべて作った値で、実在のマップではありません
