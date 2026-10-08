"""Lupa regressions for mixed cargo helpers and the merchant UI flow.

These tests execute extracted production method bodies. The small Lua stubs below
stand in for MSW services and UI fields; the cargo projection, selection, quantity
limits, and sell dispatch remain the production implementations.
"""

import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageData.mlua"
STATE_PATH = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
PHASE0_PATH = ROOT / "RootDesk/MyDesk/Phase0VoyagePrototype.mlua"
UI_PATH = ROOT / "RootDesk/MyDesk/UI/GreatVoyageAdventureController.mlua"


def extract_method(path, method_name):
    """Return the parameters and body of one top-level production method."""
    lines = path.read_text(encoding="utf-8").splitlines()
    declaration_pattern = re.compile(
        r"^(?P<indent>[\t ]*)method\s+[^\s]+\s+"
        + re.escape(method_name)
        + r"\((?P<parameters>[^)]*)\)\s*$"
    )
    declaration_index = None
    declaration = None
    for index, line in enumerate(lines):
        match = declaration_pattern.match(line)
        if match:
            declaration_index = index
            declaration = match
            break
    if declaration is None:
        raise AssertionError(f"production method not found: {path.name}.{method_name}")

    indent = declaration.group("indent")
    end_index = next(
        (
            index
            for index in range(declaration_index + 1, len(lines))
            if lines[index] == indent + "end"
        ),
        None,
    )
    if end_index is None:
        raise AssertionError(f"production method has no matching end: {method_name}")

    parameters = []
    for parameter in declaration.group("parameters").split(","):
        parameter = parameter.strip()
        if parameter:
            parameters.append(parameter.split()[-1])
    return parameters, "\n".join(lines[declaration_index + 1 : end_index])


def install_method(lua, table_name, path, method_name):
    parameters, body = extract_method(path, method_name)
    args = ", ".join(["self", *parameters])
    lua.execute(
        f"{table_name}[{method_name!r}] = function({args})\n{body}\nend"
    )


def to_lua(value, lua):
    if isinstance(value, dict):
        table = lua.table()
        for key, item in value.items():
            table[key] = to_lua(item, lua)
        return table
    if isinstance(value, (list, tuple)):
        table = lua.table()
        for index, item in enumerate(value, 1):
            table[index] = to_lua(item, lua)
        return table
    return value


def from_lua(value):
    if not hasattr(value, "items"):
        return value
    pairs = list(value.items())
    if all(isinstance(key, int) for key, _ in pairs):
        keys = sorted(key for key, _ in pairs)
        if keys == list(range(1, len(keys) + 1)):
            return [from_lua(value[index]) for index in keys]
    return {key: from_lua(item) for key, item in pairs}


class CargoUiLuaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lua = LuaRuntime(unpack_returned_tuples=True)
        cls.lua.execute("Data = {}; Controller = {}; Phase0 = {}")
        for method_name in ("CopyCargo", "GetCargoGoods", "GetCargoGoodQuantity"):
            install_method(cls.lua, "Data", DATA_PATH, method_name)
        for method_name in ("GetShopEntries", "AdjustQuantity", "SellGood", "SetShopTab"):
            install_method(cls.lua, "Controller", UI_PATH, method_name)
        for method_name in ("RefreshShipPanel", "GetShipCargoGridPageCount", "OnUpdate"):
            install_method(cls.lua, "Controller", UI_PATH, method_name)
        install_method(cls.lua, "Controller", UI_PATH, "GetSaveLoadMessage")
        install_method(cls.lua, "Phase0", PHASE0_PATH, "GetCargoText")

        cls.lua.execute(
            """
            Data.catalog = {
                commodity_a = {id='commodity_a', displayName='Amber Tea', iconRuid='tea-icon'},
                commodity_b = {id='commodity_b', displayName='Blue Spice', iconRuid='spice-icon'}
            }
            Data.GetGoodById = function(self, id) return self.catalog[id] end

            State = {
                snapshot = {
                    playerId='player-1',
                    cargo={
                        id='commodity_a', quantity=7, buyPrice=100,
                        lots={
                            {id='commodity_a', quantity=3, buyPrice=100},
                            {id='commodity_b', quantity=2, buyPrice=250},
                            {id='commodity_a', quantity=2, buyPrice=130}
                        }
                    },
                    ship={cargoCapacity=10},
                    cardInventory={}
                },
                soldGoodId=nil, soldQuantity=0, sellCalls=0
            }
            State.GetVoyageSnapshot = function(self) return self.snapshot end
            State.SellGoodQuantity = function(self, goodId, quantity)
                self.sellCalls = self.sellCalls + 1
                self.soldGoodId = goodId
                self.soldQuantity = quantity
            end
            _GreatVoyageVoyageData = Data
            _GreatVoyageVoyageState = State
            _GreatVoyagePlayerMarket = {
                GetClientQuote = function(self, portId, goodId, quantity)
                    return {unitPrice=42}
                end
            }
            _Phase0VoyagePrototype = {tradeQuantity=1}
            isvalid = function(value) return value ~= nil end
            Color = function(...) return {...} end
            Vector2 = function(...) return {...} end
            DataRef = function(value) return value end
            ImageType = {Simple='Simple'}
            PreserveSpriteType = {AspectOnly='AspectOnly', None='None'}
            log = function(message) end
            """
        )
        cls.controller = cls.lua.eval(
            "{shopTab='sell', currentPortId='forest', shopSelectedIndex=1, "
            "shopStatusMessage='', shopPage=1, shopQuantity=1, "
            "GetShopEntries=function(self) return Controller.GetShopEntries(self) end, "
            "RefreshShop=function(self) self.refreshCount=(self.refreshCount or 0)+1 end}"
        )
        cls.controller.SetShopTab = cls.lua.globals().Controller.SetShopTab
        cls.lua.execute(
            "Data.GetShipById = function(self, id) return {id=id, name='Sampan', tier=0, spriteRuid=''} end; "
            "Data.GetShipUpgradeCardById = function(self, id) return nil end; "
            "Data.GetCardSlotRuid = function(self) return '' end; "
            "Data.GetRepairQuote = function(self, ship) return 0 end; "
            "State.GetPortIdFromMap = function(self, mapName) return 'forest' end"
        )

    def setUp(self):
        self.lua = self.__class__.lua
        self.controller = self.__class__.controller
        self.lua.execute(
            "State.snapshot.cargo = {id='commodity_a', quantity=7, buyPrice=100, lots={"
            "{id='commodity_a', quantity=3, buyPrice=100},"
            "{id='commodity_b', quantity=2, buyPrice=250},"
            "{id='commodity_a', quantity=2, buyPrice=130}}}; "
            "State.snapshot.ship.cargoCapacity=10; State.snapshot.playerId='player-1'; "
            "State.sellCalls=0; State.soldGoodId=nil; State.soldQuantity=0; "
            "_Phase0VoyagePrototype.tradeQuantity=1; "
            "_GreatVoyageProfileStore={clientLoadStatus='loading'}"
        )
        self.controller.shopTab = "sell"
        self.controller.currentPortId = "forest"
        self.controller.shopSelectedIndex = 1
        self.controller.shopStatusMessage = ""
        self.controller.refreshCount = 0

    def test_save_load_status_messages_use_production_method(self):
        messages = {
            "setup": "存檔服務尚未初始化，請聯絡管理員；資產已保護。",
            "retry": "存檔連線暫時忙碌，稍後自動重試…",
            "blocked": "存檔暫時無法讀取，資產已保護；請聯絡管理員。",
            "loading": "正在讀取飛船與資產存檔…",
        }
        profile_store = self.lua.globals()._GreatVoyageProfileStore
        for status, expected in messages.items():
            with self.subTest(status=status):
                profile_store.clientLoadStatus = status
                actual = self.lua.globals().Controller.GetSaveLoadMessage(self.controller)
                self.assertEqual(actual, expected)

    def test_setup_and_retry_request_snapshot_every_30_seconds(self):
        original_state = self.lua.globals()._GreatVoyageVoyageState
        self.lua.execute(
            "SnapshotRetryTest = {refreshElapsed=0, _T={}, modalOpen=false, "
            "UpdateShipAcquired=function(self, delta) end, "
            "RefreshMapContext=function(self, force) end, "
            "RefreshInteraction=function(self) end, "
            "RefreshAirBattleDisplay=function(self) end}; "
            "SnapshotRetryTest.OnUpdate = Controller.OnUpdate; "
            "SnapshotRetryCalls=0; "
            "_GreatVoyageVoyageState={RequestEconomySnapshot=function(self) SnapshotRetryCalls=SnapshotRetryCalls+1 end}"
        )
        retry_test = self.lua.globals().SnapshotRetryTest
        profile_store = self.lua.globals()._GreatVoyageProfileStore
        request_calls = self.lua.globals()
        try:
            for status in ("setup", "retry"):
                with self.subTest(status=status):
                    profile_store.clientLoadStatus = status
                    retry_test._T.loadRetryElapsed = 0
                    request_calls.SnapshotRetryCalls = 0

                    self.lua.globals().Controller.OnUpdate(retry_test, 29)
                    self.assertEqual(request_calls.SnapshotRetryCalls, 0)
                    self.assertEqual(retry_test._T.loadRetryElapsed, 29)

                    self.lua.globals().Controller.OnUpdate(retry_test, 1)
                    self.assertEqual(request_calls.SnapshotRetryCalls, 1)
                    self.assertEqual(retry_test._T.loadRetryElapsed, 0)

            profile_store.clientLoadStatus = "ready"
            retry_test._T.loadRetryElapsed = 17
            request_calls.SnapshotRetryCalls = 0
            self.lua.globals().Controller.OnUpdate(retry_test, 29)
            self.assertEqual(request_calls.SnapshotRetryCalls, 0)
            self.assertEqual(retry_test._T.loadRetryElapsed, 0)
        finally:
            self.lua.globals()._GreatVoyageVoyageState = original_state

    def test_copy_cargo_deep_copies_and_preserves_mixed_lots(self):
        source = to_lua(
            {
                "id": "commodity_a",
                "quantity": 7,
                "buyPrice": 100,
                "lots": [
                    {"id": "commodity_a", "quantity": 3, "buyPrice": 100},
                    {"id": "commodity_b", "quantity": 2, "buyPrice": 250},
                    {"id": "commodity_a", "quantity": 2, "buyPrice": 130},
                ],
            },
            self.lua,
        )
        normalized = self.lua.globals().Data.CopyCargo(self.lua.globals().Data, source)
        normalized_view = from_lua(normalized)
        self.assertEqual(normalized_view["id"], "commodity_a")
        self.assertEqual(normalized_view["quantity"], 7)
        self.assertEqual(normalized_view["buyPrice"], 100)
        self.assertEqual(len(normalized_view["lots"]), 3)

        normalized.lots[1].quantity = 99
        self.assertEqual(source.lots[1].quantity, 3)

    def test_cargo_good_helpers_aggregate_by_first_seen_order(self):
        state = self.lua.globals().State
        cargo = state.snapshot.cargo
        goods = self.lua.globals().Data.GetCargoGoods(self.lua.globals().Data, cargo)
        self.assertEqual(
            from_lua(goods),
            [
                {"id": "commodity_a", "quantity": 5, "buyPrice": 100},
                {"id": "commodity_b", "quantity": 2, "buyPrice": 250},
            ],
        )
        self.assertEqual(
            self.lua.globals().Data.GetCargoGoodQuantity(
                self.lua.globals().Data, cargo, "commodity_b"
            ),
            2,
        )

    def test_copy_cargo_accepts_legacy_scalar_shape(self):
        legacy = to_lua(
            {"id": "commodity_b", "quantity": 4, "buyPrice": 275}, self.lua
        )
        copied = self.lua.globals().Data.CopyCargo(self.lua.globals().Data, legacy)
        self.assertEqual(
            from_lua(copied),
            {
                "id": "commodity_b",
                "quantity": 4,
                "buyPrice": 275,
                "lots": [{"id": "commodity_b", "quantity": 4, "buyPrice": 275}],
            },
        )

    def test_sell_tab_lists_each_good_without_mutating_catalog(self):
        entries = self.lua.globals().Controller.GetShopEntries(
            self.controller
        )
        self.assertEqual([entries[i].id for i in (1, 2)], ["commodity_a", "commodity_b"])
        self.assertEqual(self.lua.globals().Data.catalog.commodity_a.displayName, "Amber Tea")
        self.assertEqual(self.lua.globals().Data.catalog.commodity_b.displayName, "Blue Spice")

    def test_sell_quantity_is_bounded_by_selected_good_not_total_cargo(self):
        self.controller.shopSelectedIndex = 2
        self.lua.globals()._Phase0VoyagePrototype.tradeQuantity = 1
        self.lua.globals().Controller.AdjustQuantity(
            self.controller, 100
        )
        self.assertEqual(self.lua.globals()._Phase0VoyagePrototype.tradeQuantity, 2)

    def test_buy_quantity_is_bounded_by_free_cargo_slots(self):
        self.controller.shopTab = "goods"
        self.lua.globals()._Phase0VoyagePrototype.tradeQuantity = 1
        self.lua.globals().Controller.AdjustQuantity(
            self.controller, 100
        )
        self.assertEqual(self.lua.globals()._Phase0VoyagePrototype.tradeQuantity, 3)

    def test_sell_dispatch_targets_selected_good_and_quantity(self):
        self.controller.shopTab = "sell"
        self.controller.shopSelectedIndex = 2
        self.lua.globals()._Phase0VoyagePrototype.tradeQuantity = 2
        self.lua.globals().Controller.SellGood(
            self.controller
        )
        state = self.lua.globals().State
        self.assertEqual(state.sellCalls, 1)
        self.assertEqual(state.soldGoodId, "commodity_b")
        self.assertEqual(state.soldQuantity, 2)

    def test_goods_sell_action_opens_sell_tab_without_selling(self):
        self.controller.shopTab = "goods"
        self.lua.globals()._Phase0VoyagePrototype.tradeQuantity = 5
        self.lua.globals().Controller.SellGood(
            self.controller
        )
        self.assertEqual(self.controller.shopTab, "sell")
        self.assertEqual(self.lua.globals().State.sellCalls, 0)
        self.assertEqual(self.lua.globals()._Phase0VoyagePrototype.tradeQuantity, 1)

    def test_phase0_cargo_summary_describes_mixed_goods(self):
        phase0 = self.lua.eval("{cargoCapacity=10}")
        text = self.lua.globals().Phase0.GetCargoText(self.lua.globals().Phase0, phase0)
        self.assertEqual(text, "貨艙 2 種貨物 7/10｜商會可分別出售")

    def test_ship_cargo_grid_flattens_lots_and_keeps_page_offset(self):
        self.lua.execute(
            "State.snapshot.cargo = {id='commodity_a', quantity=14, buyPrice=100, lots={"
            "{id='commodity_a', quantity=13, buyPrice=100},"
            "{id='commodity_b', quantity=1, buyPrice=250}}}; "
            "State.snapshot.ship = {cargoCapacity=18}; State.snapshot.status='idle'; "
            "State.snapshot.money=1000; State.snapshot.ownedShips={}; "
            "State.clientShip = {id='small_sampan', name='Sampan', revision=1, "
            "hull=100, maxHull=100, shield=20, maxShield=20, armor=40, maxArmor=40, "
            "cargoCapacity=18, slots={slot1='', slot2='', slot3=''}}; "
            "CargoGridTest = {currentMapName='map_forest_port', pendingShipRepairRevision=-1, "
            "pendingShipShopRevision=-1, shipCargoGridPage=2, shipCargoGridPageSize=12, "
            "shipConditionText={}, shipWalletText={}, shipCapacityText={}, shipCargoText={}, "
            "shipCargoIcon={Entity={Enable=true}}, shipRepairButton={Enable=false, Entity={"
            "TextGUIRendererComponent={}, SpriteGUIRendererComponent={}}}, shipStatusText={Entity={Enable=true}}, "
            "FormatMoney=function(self, amount) return tostring(amount) end, "
            "IsNearPortMerchant=function(self) return false end, "
            "SetButtonEnabled=function(self, path, button, enabled) end}; "
            "CargoGridTest.GetShipCargoGridPageCount = Controller.GetShipCargoGridPageCount; "
            "for i=1,18 do "
            "CargoGridTest['shipCargoGridCell'..i]={Enable=false}; "
            "CargoGridTest['shipCargoGridIcon'..i]={Entity={Enable=false}, ImageRUID='', Color=nil, Type=nil}; "
            "CargoGridTest['shipCargoGridLabel'..i]={Entity={Enable=false}, Text=''}; "
            "end"
        )
        grid = self.lua.globals().CargoGridTest
        self.lua.globals().Controller.RefreshShipPanel(grid)

        self.assertEqual(grid.shipCargoGridPage, 2)
        self.assertEqual(grid.shipCargoGridIcon1.ImageRUID, "thumbnail://tea-icon")
        self.assertEqual(grid.shipCargoGridIcon2.ImageRUID, "thumbnail://spice-icon")
        self.assertEqual(grid.shipCargoGridLabel2.Text, "×1")
        self.assertIn("Blue Spice ×1", grid.shipCargoText.Text)

    def test_ship_panel_clears_stale_ui_while_loading_and_restores_when_ready(self):
        self.lua.execute(
            "Data.GetShipById = function(self, id) return {id=id, name='Sampan', tier=1, spriteRuid='ship-ruid'} end; "
            "Data.GetShipUpgradeCardById = function(self, id) return id ~= '' and {name='裝甲卡'} or nil end; "
            "Data.GetCardSlotRuid = function(self) return 'slot-ruid' end; "
            "Data.GetRepairQuote = function(self, ship) return 0 end; "
            "State.snapshot = {playerId='player-1', status='idle', money=900, "
            "cargo={id='commodity_a', quantity=1, buyPrice=100, lots={{id='commodity_a', quantity=1, buyPrice=100}}}, "
            "ownedShips={small_sampan=true}, ship={cargoCapacity=18}}; "
            "State.clientShip = {id='small_sampan', name='Sampan', revision=1, "
            "hull=100, maxHull=100, shield=20, maxShield=20, armor=40, maxArmor=40, "
            "cargoCapacity=18, slots={slot1='armor-card', slot2='', slot3=''}}; "
            "State.GetPortIdFromMap = function(self, mapName) return 'forest' end; "
            "LoadingTransitionTest = {currentMapName='map_forest_port', modalOpen=true, "
            "pendingShipRepairRevision=-1, pendingShipShopRevision=-1, shipShopPanel={Enable=false}, "
            "shipConditionText={Text='', FontSize=0, FontColor=nil}, shipWalletText={Text=''}, "
            "shipCapacityText={Text=''}, shipCargoText={Text=''}, shipCargoIcon={Entity={Enable=true}}, "
            "shipRepairButton={Enable=true, Entity={Enable=true, TextGUIRendererComponent={}, SpriteGUIRendererComponent={}}}, "
            "shipStatusText={Text='', Entity={Enable=true}}, shipFooterHintEntity={Enable=true}, "
            "shipCabinContentEntity={Enable=true}, shipCargoContentEntity={Enable=true}, shipInstalledContentEntity={Enable=true}, "
            "shipNameText={Text='', Entity={Enable=true}}, shipBadgeText={Text='', Entity={Enable=true}}, "
            "shipModsText={Text=''}, shipPreviewImage={Entity={Enable=true}, ImageRUID='', Color=nil}, "
            "shipCargoHintText={Text='', Entity={Enable=true}}, shipHeaderTitleText={Text='', Entity={Enable=true}}, "
            "shipShieldBarFillTransform={Entity={Enable=true}, RectSize={}}, "
            "shipArmorBarFillTransform={Entity={Enable=true}, RectSize={}}, "
            "shipHullBarFillTransform={Entity={Enable=true}, RectSize={}}, "
            "shipShieldValueText={Text='20 / 20'}, shipArmorValueText={Text='40 / 40'}, shipHullValueText={Text='100 / 100'}, "
            "shipModSlot1Button={Enable=true, Entity={Enable=true, SpriteGUIRendererComponent={}}}, "
            "shipModSlot2Button={Enable=true, Entity={Enable=true, SpriteGUIRendererComponent={}}}, "
            "shipModSlot3Button={Enable=true, Entity={Enable=true, SpriteGUIRendererComponent={}}}, "
            "shipModSlot1Label={Text=''}, shipModSlot2Label={Text=''}, shipModSlot3Label={Text=''}, "
            "shipCargoGridPage=1, shipCargoGridPageSize=12, shipCargoGridPageText={Text='', Entity={Enable=true}}, "
            "shipCargoGridPrevButton={Enable=true, Entity={Enable=true}}, shipCargoGridNextButton={Enable=true, Entity={Enable=true}}, "
            "GetSaveLoadMessage=function(self) return Controller.GetSaveLoadMessage(self) end, "
            "GetShipCargoGridPageCount=function(self, capacity) return Controller.GetShipCargoGridPageCount(self, capacity) end, "
            "FormatMoney=function(self, amount) return tostring(amount) end, "
            "IsNearPortMerchant=function(self) return true end, "
            "SetButtonEnabled=function(self, path, button, enabled) button.Enable=enabled end}; "
            "LoadingTransitionTest.RefreshShipPanel = Controller.RefreshShipPanel; "
            "for i=1,18 do "
            "LoadingTransitionTest['shipCargoGridCell'..i]={Enable=true}; "
            "LoadingTransitionTest['shipCargoGridIcon'..i]={Entity={Enable=true}, ImageRUID='', Color=nil, Type=nil}; "
            "LoadingTransitionTest['shipCargoGridLabel'..i]={Entity={Enable=true}, Text=''}; "
            "end; "
            "_GreatVoyageVoyageState=State; "
            "_GreatVoyageProfileStore={clientLoadStatus='ready'}"
        )
        grid = self.lua.globals().LoadingTransitionTest
        state = self.lua.globals().State

        self.lua.globals().Controller.RefreshShipPanel(grid)
        self.assertTrue(grid.shipPreviewImage.Entity.Enable)
        self.assertTrue(grid.shipModSlot1Button.Entity.Enable)
        self.assertTrue(grid.shipModSlot1Button.Enable)
        self.assertTrue(grid.shipShieldBarFillTransform.Entity.Enable)
        self.assertTrue(grid.shipCargoGridPageText.Entity.Enable)
        self.assertTrue(grid.shipCargoGridNextButton.Entity.Enable)

        state.clientShip.hull = None
        state.snapshot.playerId = ""
        self.lua.globals()._GreatVoyageProfileStore.clientLoadStatus = "setup"
        preserved_snapshot = {
            "money": state.snapshot.money,
            "status": state.snapshot.status,
            "cargo_quantity": state.snapshot.cargo.quantity,
            "capacity": state.snapshot.ship.cargoCapacity,
            "player_id": state.snapshot.playerId,
        }
        self.lua.globals().Controller.RefreshShipPanel(grid)

        self.assertFalse(grid.shipPreviewImage.Entity.Enable)
        for index in range(1, 4):
            self.assertFalse(grid[f"shipModSlot{index}Button"].Entity.Enable)
            self.assertFalse(grid[f"shipModSlot{index}Button"].Enable)
            self.assertFalse(grid[f"ship{['Shield', 'Armor', 'Hull'][index - 1]}BarFillTransform"].Entity.Enable)
            self.assertEqual(grid[f"ship{['Shield', 'Armor', 'Hull'][index - 1]}ValueText"].Text, "—")
        self.assertFalse(grid.shipCargoGridPageText.Entity.Enable)
        self.assertFalse(grid.shipCargoGridPrevButton.Entity.Enable)
        self.assertFalse(grid.shipCargoGridNextButton.Entity.Enable)
        self.assertFalse(grid.shipCargoGridPrevButton.Enable)
        self.assertFalse(grid.shipCargoGridNextButton.Enable)
        self.assertFalse(grid.shipCargoHintText.Entity.Enable)
        self.assertTrue(grid.shipCabinContentEntity.Enable)
        self.assertTrue(grid.shipCargoContentEntity.Enable)
        self.assertTrue(grid.shipInstalledContentEntity.Enable)
        self.assertEqual(
            {
                "money": state.snapshot.money,
                "status": state.snapshot.status,
                "cargo_quantity": state.snapshot.cargo.quantity,
                "capacity": state.snapshot.ship.cargoCapacity,
                "player_id": state.snapshot.playerId,
            },
            preserved_snapshot,
        )

        state.clientShip.hull = 100
        state.snapshot.playerId = "player-1"
        self.lua.globals()._GreatVoyageProfileStore.clientLoadStatus = "ready"
        self.lua.globals().Controller.RefreshShipPanel(grid)
        self.assertTrue(grid.shipPreviewImage.Entity.Enable)
        self.assertTrue(grid.shipModSlot1Button.Entity.Enable)
        self.assertTrue(grid.shipModSlot1Button.Enable)
        self.assertTrue(grid.shipShieldBarFillTransform.Entity.Enable)
        self.assertEqual(grid.shipHullValueText.Text, "100 / 100")
        self.assertTrue(grid.shipCargoGridPageText.Entity.Enable)
        self.assertTrue(grid.shipCargoGridNextButton.Entity.Enable)

    def test_buy_quantity_without_state_does_not_change_quantity(self):
        self.controller.shopTab = "goods"
        state = self.lua.globals()._GreatVoyageVoyageState
        self.lua.globals()._GreatVoyageVoyageState = None
        try:
            self.lua.globals().Controller.AdjustQuantity(self.controller, 1)
            self.assertEqual(self.lua.globals()._Phase0VoyagePrototype.tradeQuantity, 1)
            self.assertEqual(self.controller.refreshCount, 0)
        finally:
            self.lua.globals()._GreatVoyageVoyageState = state

    def test_unknown_cargo_icon_keeps_slot_without_crashing(self):
        self.test_ship_cargo_grid_flattens_lots_and_keeps_page_offset()
        self.lua.execute(
            "State.snapshot.cargo = {id='missing_good', quantity=1, buyPrice=100, "
            "lots={{id='missing_good', quantity=1, buyPrice=100}}}; "
            "CargoGridTest.shipCargoGridPage=1"
        )
        grid = self.lua.globals().CargoGridTest
        self.lua.globals().Controller.RefreshShipPanel(grid)
        self.assertTrue(grid.shipCargoGridCell1.Enable)
        self.assertFalse(grid.shipCargoGridIcon1.Entity.Enable)


if __name__ == "__main__":
    unittest.main(verbosity=2)
