import re
import unittest
from pathlib import Path

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageData.mlua"
STATE_PATH = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"


def extract_method(source, name, owner="data"):
    match = re.search(r"(?m)^\s*method\s+\w+\s+" + re.escape(name) + r"\s*\(([^\n]*)\)\s*\n", source)
    if not match:
        raise AssertionError(f"production method {name} not found")
    end = re.search(r"(?m)^\tend\s*$", source[match.end():])
    if not end:
        raise AssertionError(f"could not find end of production method {name}")
    signature = re.sub(r"\b(?:any|integer|string|number|boolean|table)\s+(\w+)", r"\1", match.group(1))
    body = source[match.end():match.end() + end.start()]
    return f"function {owner}:{name}({signature})\n{body}\nend"


WORLD_MOCKS = r"""
senderUserId = "u"
logs = {}
log = function(...) table.insert(logs, table.concat({...}, " ")) end
log_warning = function(...) end
isvalid = function(value) return value ~= nil end
data.goods = {
    apple = { id="apple", displayName="蘋果", price=10, isBoss=true },
    pear = { id="pear", displayName="梨子", price=20, isBoss=true }
}
function data:GetPort(portId) return { goods={self.goods.apple, self.goods.pear} } end
function data:GetGoodById(goodId) return self.goods[goodId] end
market = { remaining=100, saleUnitPrice=25, applied={}, consumed=0, entries={}, syncOk=true }
feedbackCalls = {}
afterMarketRead = function() end
_GreatVoyageVoyageData = data
_GreatVoyagePlayerMarket = {
    GetMarket=function(self, playerId, portId) afterMarketRead(); return market end,
    GetNow=function(self) return 1 end,
    MarkDirty=function(self, playerId, portId, goodId) market.lastDirtyGood=goodId; return market.syncOk end,
    PublishMarket=function(self, playerId, portId) end
}
_GreatVoyageMarketPricing = {
    GetBossStock=function(self, entries, profileCode, goodId, now) return { remaining=market.remaining } end,
    ConsumeBossStock=function(self, entries, profileCode, goodId, quantity, now)
        market.remaining = market.remaining - quantity
        market.consumed = market.consumed + quantity
        local record = entries[goodId] or { pressure=0, at=0, cycle=-1, bought=0 }
        record.cycle = math.floor(now / 10800)
        record.bought = record.bought + quantity
        entries[goodId] = record
        market.entries = entries
        return true
    end,
    GetSaleQuote=function(self, entries, portId, goodId, quantity, now)
        return { valid=true, unitPrice=market.saleUnitPrice, total=market.saleUnitPrice*quantity }
    end,
    ApplySale=function(self, entries, goodId, quote)
        table.insert(market.applied, {id=goodId, total=quote.total})
        local record = entries[goodId] or { pressure=0, at=0, cycle=-1, bought=0 }
        record.pressure = 0.5
        record.at = 1
        entries[goodId] = record
        market.entries = entries
    end
}
_UserService = {
    GetUserEntityByUserId=function(self, playerId) return { CurrentMapName="map_forest_port" } end
}
state = {
    voyageByPlayer={},
    testState={ship={cargoCapacity=8}, status="idle", cargo={id="",quantity=0,buyPrice=0,lots={}}, money=1000, economyRevision=0},
    clientCargoRevision=-1, clientSnapshotCargo={id="",quantity=0,buyPrice=0,lots={}},
    clientSnapshotPlayerId="", clientSnapshotStatus="idle", clientSnapshotOriginId="", clientSnapshotDestinationId="",
    clientSnapshotDistanceTravelled=0, clientSnapshotBudgetRemaining=0, clientSnapshotPausedDistance=0,
    clientSnapshotPendingEncounterId="", clientSnapshotEncounterCount=0, clientSnapshotCargoId="",
    clientSnapshotCargoQuantity=0, clientSnapshotCargoBuyPrice=0, clientSnapshotMoney=1000,
    clientSnapshotEconomyRevision=0, clientSnapshotEconomyMessage="", clientSnapshotHullDamage=0,
    clientSnapshotRemainingSeconds=60, clientSnapshotRaidRemaining=0, clientSnapshotLastReason=""
}
state.voyageByPlayer.u = state.testState
function state:GetOrCreateState(playerId) return self.testState end
function state:GetPortIdFromMap(mapName) return "forest" end
function state:IsAtShop(player, portId) return true end
function state:CompleteEconomyRequest(playerId, target, message)
    target.economyRevision = (target.economyRevision or 0) + 1
    target.lastMessage = message
end
function state:CompleteShipRequest(playerId, target, message) end
function state:ReceiveTransactionFeedback(...) table.insert(feedbackCalls, {...}) end
function state:PreviewDirectRoute(origin, destination) return nil end
"""


class CargoProductionMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_source = DATA_PATH.read_text(encoding="utf-8")
        cls.state_source = STATE_PATH.read_text(encoding="utf-8")

    def make_lua(self, methods=()):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("data = {}; state = {}")
        for name in ("CopyCargo", "GetCargoGoods", "GetCargoGoodQuantity", "AddCargo", "RemoveCargo"):
            lua.execute(extract_method(self.data_source, name))
        lua.execute(WORLD_MOCKS)
        for name in methods:
            lua.execute(extract_method(self.state_source, name, owner="state"))
        return lua

    def test_same_good_and_mixed_good_purchases_append_batches(self):
        lua = self.make_lua(("BuyGood",))
        lua.execute("state:BuyGood('apple', 1); state:BuyGood('apple', 2)")
        cargo = lua.globals().state.testState.cargo
        self.assertEqual((cargo.id, cargo.quantity, cargo.buyPrice), ("apple", 3, 10))
        self.assertEqual(len(cargo.lots), 1)
        lua.execute("state:BuyGood('pear', 1)")
        cargo = lua.globals().state.testState.cargo
        self.assertEqual(cargo.quantity, 4)
        self.assertEqual([(cargo.lots[i].id, cargo.lots[i].quantity) for i in range(1, 3)],
                         [("apple", 3), ("pear", 1)])
        self.assertEqual(lua.globals().state.testState.money, 950)
        self.assertEqual(lua.globals().market.consumed, 4)

    def test_boss_buy_sync_failure_rolls_back_money_cargo_and_market_row(self):
        lua = self.make_lua(("BuyGood",))
        lua.execute("""market.syncOk=false; market.entries.apple={pressure=0.25,at=99,cycle=0,bought=2}""")
        lua.execute("""state:BuyGood("apple", 1)""")
        market = lua.globals().market
        state = lua.globals().state.testState
        self.assertEqual(state.money, 1000)
        self.assertEqual(state.cargo.quantity, 0)
        self.assertEqual(market.entries.apple.pressure, 0.25)
        self.assertEqual(market.entries.apple.at, 99)
        self.assertEqual(market.entries.apple.cycle, 0)
        self.assertEqual(market.entries.apple.bought, 2)
        self.assertEqual(len(lua.globals().feedbackCalls), 0)
        self.assertNotIn("server buy", "\n".join(lua.globals().logs[i] for i in range(1, len(lua.globals().logs) + 1)))

    def test_full_capacity_rejects_without_changing_money_or_stock(self):
        lua = self.make_lua(("BuyGood",))
        lua.execute("""
            state.testState.ship.cargoCapacity=1
            state.testState.cargo=data:AddCargo(nil, "apple", 1, 10)
            state:BuyGood("pear", 1)
        """)
        self.assertEqual(lua.globals().state.testState.money, 1000)
        self.assertEqual(lua.globals().market.consumed, 0)
        self.assertEqual(lua.globals().market.remaining, 100)
        self.assertEqual(lua.globals().state.testState.cargo.quantity, 1)

    def test_market_yield_rechecks_cargo_state_and_capacity(self):
        lua = self.make_lua(("BuyGood",))
        lua.execute("""
            state.testState.ship.cargoCapacity=2
            state.testState.cargo=data:AddCargo(nil, "apple", 1, 10)
            afterMarketRead=function()
                state.testState.cargo=data:AddCargo(state.testState.cargo, "pear", 1, 20)
            end
            state:BuyGood("apple", 1)
        """)
        self.assertEqual(lua.globals().state.testState.money, 1000)
        self.assertEqual(lua.globals().market.consumed, 0)
        self.assertEqual(lua.globals().state.testState.cargo.quantity, 2)
        self.assertIn("狀態已變更", lua.globals().state.testState.lastMessage)

    def test_market_yield_rechecks_capacity_downgrade(self):
        lua = self.make_lua(("BuyGood",))
        lua.execute("""
            state.testState.ship.cargoCapacity=2
            state.testState.cargo=data:AddCargo(nil, "apple", 1, 10)
            afterMarketRead=function() state.testState.ship.cargoCapacity=1 end
            state:BuyGood("pear", 1)
        """)
        self.assertEqual(lua.globals().state.testState.money, 1000)
        self.assertEqual(lua.globals().market.consumed, 0)
        self.assertEqual(lua.globals().state.testState.cargo.quantity, 1)
        self.assertIn("狀態已變更", lua.globals().state.testState.lastMessage)

    def test_sell_quantity_uses_fifo_cost_and_only_removes_selected_good(self):
        lua = self.make_lua(("SellCargoInternal",))
        lua.execute("""
            state.testState.cargo={
                id="apple", quantity=5, buyPrice=10, lots={
                    {id="apple",quantity=2,buyPrice=10},
                    {id="pear",quantity=1,buyPrice=30},
                    {id="apple",quantity=2,buyPrice=20}
                }
            }
            state:SellCargoInternal("u", "apple", 3, false)
        """)
        cargo = lua.globals().state.testState.cargo
        self.assertEqual(lua.globals().state.testState.money, 1075)
        self.assertEqual(lua.globals().market.applied[1].id, "apple")
        self.assertEqual(lua.globals().market.lastDirtyGood, "apple")
        self.assertEqual(cargo.quantity, 2)
        self.assertEqual([(cargo.lots[i].id, cargo.lots[i].quantity, cargo.lots[i].buyPrice)
                          for i in range(1, 3)], [("pear", 1, 30), ("apple", 1, 20)])
        self.assertIn("profit=35", "\n".join(lua.globals().logs[i] for i in range(1, len(lua.globals().logs) + 1)))

    def test_sell_sync_failure_rolls_back_money_cargo_and_market_row(self):
        lua = self.make_lua(("SellCargoInternal",))
        lua.execute("""
            state.testState.cargo=data:AddCargo(nil, "apple", 2, 10)
            market.entries.apple={pressure=0.25,at=99,cycle=0,bought=2}
            market.syncOk=false
            state:SellCargoInternal("u", "apple", 1, false)
        """)
        state = lua.globals().state.testState
        record = lua.globals().market.entries.apple
        self.assertEqual(state.money, 1000)
        self.assertEqual(state.cargo.quantity, 2)
        self.assertEqual(record.pressure, 0.25)
        self.assertEqual(record.at, 99)
        self.assertEqual(record.cycle, 0)
        self.assertEqual(record.bought, 2)
        self.assertEqual(len(lua.globals().feedbackCalls), 0)
        self.assertNotIn("server sell", "\n".join(lua.globals().logs[i] for i in range(1, len(lua.globals().logs) + 1)))

    def test_snapshot_copies_lots_and_rejects_old_scalar_revision(self):
        lua = self.make_lua(("ReceiveVoyageSnapshot", "ReceiveCargoInventorySnapshot", "CopyClientSnapshot"))
        lua.execute("""
            local cargo=data:AddCargo(nil, "apple", 2, 10)
            cargo=data:AddCargo(cargo, "pear", 1, 20)
            state:ReceiveCargoInventorySnapshot(cargo, 2)
            cargo.lots[1].quantity=88
            state:ReceiveVoyageSnapshot("u","idle","","",0,0,0,"",0,"apple",2,10,900,2,"current",0,60,0,"")
            state:ReceiveVoyageSnapshot("u","idle","","",0,0,0,"",0,"apple",1,5,100,1,"old",0,60,0,"")
            copied=state:CopyClientSnapshot()
            copied.cargo.lots[1].quantity=99
        """)
        self.assertEqual(lua.globals().state.clientSnapshotCargo.quantity, 3)
        self.assertEqual(lua.globals().state.clientSnapshotCargo.lots[1].quantity, 2)
        self.assertEqual(lua.globals().state.clientCargoRevision, 2)
        self.assertEqual(lua.globals().state.clientSnapshotMoney, 900)
        self.assertEqual(lua.globals().state.clientSnapshotEconomyRevision, 2)
        self.assertEqual(lua.globals().copied.cargo.lots[1].quantity, 99)

    def test_legacy_cargo_and_remove_helpers(self):
        lua = self.make_lua()
        data = lua.globals().data
        empty = data.CopyCargo(data, None)
        self.assertEqual((empty.id, empty.quantity, empty.buyPrice, len(empty.lots)), ("", 0, 0, 0))
        empty_inventory = data.CopyCargo(data, lua.eval("{id='apple', quantity=9, buyPrice=7, lots={}}"))
        self.assertEqual((empty_inventory.id, empty_inventory.quantity, len(empty_inventory.lots)), ("", 0, 0))
        legacy = data.CopyCargo(data, lua.eval("{id='apple', quantity=2, buyPrice=7}"))
        self.assertEqual((legacy.lots[1].id, legacy.lots[1].quantity, legacy.lots[1].buyPrice),
                         ("apple", 2, 7))
        removed = data.RemoveCargo(data, lua.eval("""
            {id="apple",quantity=5,buyPrice=10,lots={
                {id="apple",quantity=2,buyPrice=10},
                {id="pear",quantity=1,buyPrice=30},
                {id="apple",quantity=2,buyPrice=20}
            }}
        """), "apple", 3)
        self.assertEqual(removed.cost, 40)
        self.assertEqual(removed.cargo.quantity, 2)
        self.assertIsNone(data.RemoveCargo(data, legacy, "pear", 1))

    def test_rpc_and_total_capacity_schema_are_wired_in_production(self):
        self.assertIn("method void SellGoodQuantity(string goodId, integer quantity)", self.state_source)
        self.assertIn("method void ReceiveCargoInventorySnapshot(table cargo, integer economyRevision)", self.state_source)
        buy = self.state_source.split("method void BuyGood(", 1)[1].split("\n\tend", 1)[0]
        self.assertIn("currentQuantity + quantity > capacity", buy)
        self.assertIn("currentCargo.quantity + quantity > capacity", buy)
        self.assertIn("AddCargo", buy)


if __name__ == "__main__":
    unittest.main()
