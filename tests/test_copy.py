"""Copy files: Hindi and English must stay in step, and the red-flag file must be whole.

These check structure only. They never judge or generate wording.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
COPY_DIRS = [ROOT / "web" / "src" / "copy", ROOT / "src" / "copy"]
SLOT = re.compile(r"\{(\w+)\}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("folder", COPY_DIRS, ids=lambda p: str(p.relative_to(ROOT)))
def test_hindi_and_english_have_the_same_strings(folder: Path) -> None:
    if not (folder / "en.json").exists() and not (folder / "hi.json").exists():
        pytest.skip("no copy files here yet")
    en, hi = load(folder / "en.json"), load(folder / "hi.json")
    assert set(en) == set(hi), f"keys only in one language: {sorted(set(en) ^ set(hi))}"
    for key in en:
        assert en[key].strip() and hi[key].strip(), f"{key} is empty in one language"
        # A slot like {start} that exists in one language must exist in the other, or a value goes missing.
        assert set(SLOT.findall(en[key])) == set(SLOT.findall(hi[key])), f"{key} has different slots"


def test_red_flag_file_has_both_languages() -> None:
    path = ROOT / "src" / "copy" / "red_flag.json"
    if not path.exists():
        pytest.skip("red_flag.json has not been written yet")
    text = load(path)
    assert set(text) == {"hi", "en"}
    assert all(isinstance(value, str) and value.strip() for value in text.values())
