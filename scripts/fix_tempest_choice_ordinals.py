#!/usr/bin/env python3
"""Close the ordinal gap left at qb_tem_2 by the ch_tem_material merge.

Deleting the material choice left its siblings at 0, 2, 3. Ordinals are
ordering rather than an index, so nothing breaks -- but choice ordinal 0 is the
one that auto-fires headlessly until a UI exists, so this list is worth keeping
honest. Renumbers to 0, 1, 2. Touches no prose, no effect and no count.
"""
import json, sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "remnant_content_consolidated_rev2.json"

def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw

    cs = sorted([c for c in data["choices"] if c["parentId"] == "qb_tem_2"],
                key=lambda c: c["ordinal"])
    if [c["ordinal"] for c in cs] == list(range(len(cs))):
        print("already contiguous; nothing to do")
        return 0
    assert [c["id"] for c in cs] == ["ch_tem_direct", "ch_tem_reject", "ch_tem_betray"], \
        [c["id"] for c in cs]
    before = json.dumps({c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]})
    for n, c in enumerate(cs):
        c["ordinal"] = n
    assert before == json.dumps({c["id"]: (c.get("label"), c.get("outcomeText"))
                                 for c in data["choices"]}), "prose changed"
    CONTENT.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8", newline="\n")
    print("qb_tem_2 choice ordinals -> 0, 1, 2")
    return 0

if __name__ == "__main__":
    sys.exit(main())
