import json
import math
import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "RootDesk/MyDesk/Combat/GreatVoyageEncounterData.mlua"
DATA = ROOT / "docs/web/encounter-balance/encounter-balance.json"


def load_logic():
    source = SCRIPT.read_text(encoding="utf-8")
    source = re.sub(r"^@Logic\s*", "", source, flags=re.MULTILINE)
    source = re.sub(r"^script\s+\w+\s+extends\s+Logic\s*", "", source, flags=re.MULTILINE)
    source = re.sub(r"^\s*@ExecSpace\([^\n]*\)\s*", "", source, flags=re.MULTILINE)

    def convert_method(match):
        params = []
        raw_params = match.group(2).strip()
        if raw_params:
            for param in raw_params.split(","):
                params.append(param.strip().split()[-1])
        return "\tfunction Logic:" + match.group(1) + "(" + ", ".join(params) + ")"

    source = re.sub(r"\nend\s*$", "", source)
    source = re.sub(r"^[ \t]*method\s+\w+\s+(\w+)\(([^)]*)\)", convert_method, source, flags=re.MULTILINE)
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("Logic = {}\n" + source)
    return lua


class SourcePathPortabilityTests(unittest.TestCase):
    def test_data_path_matches_filesystem_case(self):
        current = ROOT
        for part in DATA.relative_to(ROOT).parts:
            self.assertIn(part, {entry.name for entry in current.iterdir()},
                          f"資料路徑大小寫與檔案系統不符：{current / part}")
            current /= part


class EncounterDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.lua = load_logic()
        cls.logic = cls.lua.eval("setmetatable({_T = {}}, {__index = Logic})")

    def test_adopted_enabled_and_disabled_pool(self):
        self.assertEqual(len(self.data["monsters"]), 132)
        self.assertEqual(sum(bool(m["enabled"]) for m in self.data["monsters"]), 129)
        prepared = self.logic.Prepare(self.logic, "victoria", 5, 0, 0, self.lua.table(), False)
        ids = {prepared["candidates"][i]["definition"]["packId"] for i in range(1, len(prepared["candidates"]) + 1)}
        disabled = {m["packId"] for m in self.data["monsters"] if not m["enabled"]}
        self.assertTrue(ids.isdisjoint(disabled))
        self.assertEqual(self.logic.GetMonsterById(self.logic, "mob/9300379.img")["enabled"], False)

    def test_open_sea_uses_only_global_pool(self):
        prepared = self.logic.Prepare(self.logic, "open_sea", 5, 0, 0, self.lua.table(), False)
        self.assertGreater(len(prepared["candidates"]), 0)
        for i in range(1, len(prepared["candidates"]) + 1):
            self.assertEqual(prepared["candidates"][i]["definition"]["area"], "__allair")

    def test_cargo_increases_encounters_cash_does_not(self):
        base = self.logic.Prepare(self.logic, "victoria", 1, 0, 0, self.lua.table(), False)
        cargo = self.logic.Prepare(self.logic, "victoria", 1, 50000, 0, self.lua.table(), False)
        self.assertGreater(cargo["chance"], base["chance"])
        self.assertGreaterEqual(cargo["countMin"], base["countMin"])
        self.assertGreaterEqual(cargo["countMax"], base["countMax"])
        for invalid in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(Exception):
                self.logic.Prepare(self.logic, "victoria", 1, invalid, 0, self.lua.table(), False)
            with self.assertRaises(Exception):
                self.logic.Prepare(self.logic, "victoria", 1, 0, invalid, self.lua.table(), False)

    def test_ship_caps_card_stack_and_species_stats(self):
        tier1 = self.logic.Prepare(self.logic, "victoria", 1, 0, 0, self.lua.table(), False)
        self.assertEqual(self.logic.GetShipTier(self.logic, 1)["maxLevel"], 50)
        self.assertEqual(self.logic.GetShipTier(self.logic, 5)["maxLevel"], 999)
        for i in range(1, len(tier1["candidates"]) + 1):
            self.assertLessEqual(tier1["candidates"][i]["definition"]["level"], 50)
        stats = self.lua.table_from({"encounterMultiplier": 0.5})
        lure = self.logic.Prepare(self.logic, "victoria", 1, 0, 0, stats, False)
        self.assertGreater(lure["chance"], tier1["chance"])
        badda = self.logic.GetMonsterById(self.logic, "mob/8642102.img")
        bubble = self.logic.GetMonsterById(self.logic, "mob/2230109.img")
        for monster in (badda, bubble):
            self.assertEqual(monster["level"], 28)
            self.assertEqual((monster["hp"], monster["attack"], monster["bounty"]), (120, 12, 100))
            self.assertEqual((monster["maxHp"], monster["attackDamage"], monster["attackIntervalSeconds"]), (120, 12, 2))

    def test_profiles_and_t5_one_shot_ceiling(self):
        self.assertEqual(self.logic.GetCombatProfile(self.logic, 0)["maxHull"], 100)
        self.assertEqual(self.logic.GetCombatProfile(self.logic, 1)["cannonDamage"], 40)
        profile = self.logic.GetCombatProfile(self.logic, 5)
        self.assertEqual(profile["cannonDamage"], 4000)
        self.assertLessEqual(max(m["hp"] for m in self.data["monsters"] if m["enabled"]), 3000)
        self.assertGreater(profile["cannonDamage"], 3000)

    def test_draw_wave_is_mixed_and_with_replacement(self):
        self.lua.execute("""
            _UtilLogic = { rolls = {0, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999, 0, 0.999999}, index = 1 }
            function _UtilLogic:RandomDouble()
                self.calls = (self.calls or 0) + 1
                local value = self.rolls[self.index] or 0
                self.index = self.index + 1
                return value
            end
            function _UtilLogic:RandomIntegerRange(minimum, maximum) return minimum end
        """)
        prepared = self.logic.Prepare(self.logic, "victoria", 5, 0, 0, self.lua.table(), False)
        wave = self.logic.DrawWave(self.logic, prepared)
        self.assertGreater(len(wave), 1)
        pack_ids = [wave[i]["packId"] for i in range(1, len(wave) + 1)]
        self.assertGreater(len(set(pack_ids)), 1)
        self.lua.execute("_UtilLogic.rolls = {0.999999, 0.999999, 0.999999, 0.999999, 0.999999, 0.999999, 0.999999, 0.999999, 0.999999, 0.999999}; _UtilLogic.index = 1; _UtilLogic.calls = 0")
        confirmed_wave = self.logic.DrawWave(self.logic, prepared)
        self.assertEqual(len(confirmed_wave), prepared["countMin"])
        self.assertEqual(self.lua.eval("_UtilLogic.calls"), len(confirmed_wave))
        self.assertTrue(all(confirmed_wave[i]["enabled"] for i in range(1, len(confirmed_wave) + 1)))


if __name__ == "__main__":
    unittest.main()
