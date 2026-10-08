import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
VOYAGE_PATH = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
PRICE_PATH = ROOT / "Scripts/PriceFluctuation.lua"


def extract_method(path, name):
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\tmethod\s+[^\n]+\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n([\s\S]*?)\n\tend(?=\s|$)"
    )
    match = pattern.search(source)
    if match is None:
        raise AssertionError(f"production method not found: {name}")
    params = [part.strip().split()[-1] for part in match.group(1).split(",") if part.strip()]
    return params, match.group(2)


def run_abandon(previous_card_revision, restored_card_revision, disconnected=False):
    params, body = extract_method(VOYAGE_PATH, "AbandonVoyage")
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("log = function(...) end; isvalid = function(_) return false end")
    lua.execute("Voyage = {}")
    lua.execute(
        "Voyage.AbandonVoyage = function(self, "
        + ", ".join(params)
        + ")\n"
        + body
        + "\nend"
    )
    lua.globals().previous = lua.table_from({
        "status": "sailing",
        "shipRevision": 9,
        "economyRevision": 11,
        "cardInventoryRevision": previous_card_revision,
    })
    lua.globals().restored = lua.table_from({
        "shipRevision": 0,
        "economyRevision": 0,
        "cardInventoryRevision": restored_card_revision,
        "safePortId": "port",
    })
    lua.execute(
        """manager = { voyageByPlayer = { captain = previous }, _T = {}, AbandonVoyage = Voyage.AbandonVoyage }
manager.GetOrCreateState = function(self, playerId) self.rehydrated = true; return restored end
manager.MovePlayerToPort = function(self, playerId, portId) end
manager.PublishSnapshot = function(self, playerId, state) self.publishedCardRevision = state.cardInventoryRevision end"""
    )
    lua.globals().manager.AbandonVoyage(lua.globals().manager, "captain", lua.globals().previous, disconnected)
    return lua.globals().manager, lua.globals().restored


class GitReviewRegressionTests(unittest.TestCase):
    def test_abandon_voyage_keeps_card_inventory_revision_monotonic(self):
        manager, restored = run_abandon(42, 0)
        self.assertEqual(restored.cardInventoryRevision, 42)
        self.assertEqual(manager.publishedCardRevision, 42)

        manager, restored = run_abandon(42, 50)
        self.assertEqual(restored.cardInventoryRevision, 50)
        self.assertEqual(manager.publishedCardRevision, 50)

    def test_disconnect_does_not_rehydrate_abandoned_voyage(self):
        manager, _ = run_abandon(42, 0, disconnected=True)
        self.assertIsNone(manager.rehydrated)
        self.assertIsNone(manager.publishedCardRevision)
        self.assertIsNone(manager.voyageByPlayer.captain)

    def test_legacy_price_keeps_both_inventory_thresholds_reachable(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("math.random = function(_, _) return 0 end")
        price = lua.execute(PRICE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(price.CalculatePrice(price, 100, 5000), 50)
        self.assertEqual(price.CalculatePrice(price, 100, 3000), 80)
        self.assertEqual(price.CalculatePrice(price, 100, 4000), 80)
        self.assertEqual(price.CalculatePrice(price, 100, 2000), 100)


if __name__ == "__main__":
    unittest.main()
