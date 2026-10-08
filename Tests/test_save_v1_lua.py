import json
import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "RootDesk/MyDesk/Persistence/GreatVoyageProfileStore.mlua"
SOURCE = STORE_PATH.read_text(encoding="utf-8")


def lua_value(value, lua):
    if isinstance(value, dict):
        table = lua.table()
        for key, item in value.items():
            table[key] = lua_value(item, lua)
        return table
    if isinstance(value, (list, tuple)):
        table = lua.table()
        for index, item in enumerate(value, 1):
            table[index] = lua_value(item, lua)
        return table
    return value


def python_value(value):
    if not hasattr(value, "items"):
        return value
    pairs = list(value.items())
    if all(isinstance(key, int) for key, _ in pairs):
        keys = sorted(key for key, _ in pairs)
        if keys == list(range(1, len(keys) + 1)):
            return [python_value(value[index]) for index in keys]
    return {key: python_value(item) for key, item in pairs}


def extract_method(name):
    pattern = re.compile(
        r"\tmethod\s+[^\n]+\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        re.S,
    )
    match = pattern.search(SOURCE)
    if match is None:
        raise AssertionError(f"production method not found: {name}")
    parameters = []
    for parameter in match.group(1).split(","):
        parameter = parameter.strip()
        if parameter:
            parameters.append(parameter.split()[-1])
    body = match.group(2)
    return parameters, body


def extract_handler(name):
    pattern = re.compile(
        r"\thandler\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        re.S,
    )
    match = pattern.search(SOURCE)
    if match is None:
        raise AssertionError(f"production handler not found: {name}")
    parameters = [item.strip().split()[-1] for item in match.group(1).split(",") if item.strip()]
    return parameters, match.group(2)


def extract_method_from(path, name):
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\tmethod\s+[^\n]+\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        re.S,
    )
    match = pattern.search(source)
    if match is None:
        raise AssertionError(f"production method not found: {name}")
    return match.group(2)


def extract_method_from_with_params(path, name):
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\tmethod\s+[^\n]+\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        re.S,
    )
    match = pattern.search(source)
    if match is None:
        raise AssertionError(f"production method not found: {name}")
    parameters = [item.strip().split()[-1] for item in match.group(1).split(",") if item.strip()]
    return parameters, match.group(2)


def method_bodies(path):
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^\t(?:method\s+[^\n]+|handler\s+[^\n]+)\n(.*?)^\tend\s*$", re.M | re.S)
    return pattern.findall(source)


def make_runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("Store = {}")
    names = [
        "IsIntegerInRange",
        "IsFiniteNumber",
        "IsKnownId",
        "FindById",
        "CalculateSavedShipLimits",
        "ValidateMarketEntries",
        "ValidateProfile",
        "BuildRuntimeProfile",
        "DecodeProfile",
        "GetProfileKey",
        "EmptyMarkets",
        "GetLegacyMarketKeys",
        "ImportLegacyMarketItem",
        "LoadLegacyMarkets",
        "IsSameBoundProfile",
        "SetPlayerLoadStatus",
        "SetLoadFailure",
        "ClaimBootstrapGate",
        "ReleaseBootstrapGate",
        "ReleaseBootstrapGateBeforeWrite",
        "LoadForPlayer",
        "GetProfileForUser",
        "SyncMarket",
        "TouchDirty",
        "EncodeCargoLots",
        "EncodeCore",
        "EncodeMarketRows",
        "IsWriteAcknowledged",
        "ReconcileWrite",
        "FinishAsyncWrite",
        "ResolveTimedOutWrite",
        "EncodeProfile",
        "FlushAsync",
        "FlushAndWait",
    ]
    for name in names:
        parameters, body = extract_method(name)
        args = ", ".join(["self", *parameters])
        lua.execute(f"Store[{name!r}] = function({args})\n{body}\nend")
    handler_parameters, handler_body = extract_handler("HandleUserLeaveEvent")
    handler_args = ", ".join(["self", *handler_parameters])
    lua.execute("Store.HandleUserLeaveEvent = function(" + handler_args + ")\n" + handler_body + "\nend")
    store = lua.globals().Store
    store.schemaVersion = 2
    store.maxPayloadBytes = 50000
    store.notFoundCode = 1000002
    store.compareFailedCode = 2000000
    lua.globals()._UtilLogic = lua.table_from({"ServerElapsedSeconds": 0})
    lua.globals()._HttpService = lua.eval("{JSONEncode=function(self, value) return \"new-payload\" end}")
    lua.globals().wait = lambda _seconds: setattr(lua.globals()._UtilLogic, "ServerElapsedSeconds", lua.globals()._UtilLogic.ServerElapsedSeconds + _seconds)
    store.openPorts = lua_value(["forest", "sky", "ludus", "nihal"], lua)
    store.accounts = lua.table()
    store.profileByUser = lua.table()
    store.loadStatusByUser = lua.table()
    return lua, store


SHIPS = [
    {"id": "small_sampan", "tier": 0, "maxHull": 100, "maxArmor": 40, "maxShield": 20, "cargoCapacity": 8},
    {"id": "merchant", "tier": 1, "maxHull": 120, "maxArmor": 48, "maxShield": 24, "cargoCapacity": 10},
]
CARDS = [
    {"id": "cargo", "available": True, "cargoBonus": 1},
    {"id": "hull", "available": True, "maxHullMultiplier": 0.10},
]
GOODS = [
    {"id": "commodity_a", "sourceRow": 54, "verified": True, "originId": "forest", "demands": {"sky": 1.2}},
    {"id": "commodity_b", "sourceRow": 55, "verified": True, "originId": "sky", "demands": {"forest": 1.3}},
]


def base_profile():
    return {
        "schemaVersion": 2,
        "revision": 4,
        "safePortId": "forest",
        "core": {
            "money": 12000,
            "cargo": {
                "id": "commodity_a",
                "quantity": 2,
                "buyPrice": 1000,
                "lots": [{"id": "commodity_a", "quantity": 2, "buyPrice": 1000}],
            },
            "activeShipId": "small_sampan",
            "ships": {
                "small_sampan": {"hull": 91, "shield": 10, "armor": 20, "slots": ["", "", ""]},
                "merchant": {"hull": 88, "shield": 20, "armor": 40, "slots": ["cargo", "", ""]},
            },
            "cardInventory": {"hull": 1},
        },
        "markets": {"forest": [], "sky": [], "ludus": [], "nihal": []},
    }


class SaveV1LuaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lua, cls.store = make_runtime()
        cls.ship_catalog = lua_value(SHIPS, cls.lua)
        cls.card_catalog = lua_value(CARDS, cls.lua)
        cls.goods_catalog = lua_value(GOODS, cls.lua)
        cls.store.shipCatalog = cls.ship_catalog
        cls.store.cardCatalog = cls.card_catalog
        cls.store.goodsCatalog = cls.goods_catalog
        cls.lua.globals()._GreatVoyageVoyageData = cls.lua.eval(
            "{ GetShipCatalog=function() return Store.shipCatalog end, GetShipUpgradeCards=function() return Store.cardCatalog end }"
        )
        cls.lua.globals()._GreatVoyageCommodityCatalog = cls.lua.eval(
            "{ GetAll=function() return Store.goodsCatalog end, GetById=function(_, id) return Store:FindById(id, Store.goodsCatalog) end }"
        )
        http = cls.lua.table()
        http.JSONDecode = lambda _self, raw: lua_value(json.loads(raw), cls.lua)
        def native_json_encode(_self, value):
            if hasattr(value, "items") and len(list(value.items())) == 0:
                raise ValueError("Native LuaTableToJsonType.UnknownType for empty table")
            return json.dumps(python_value(value), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        http.JSONEncode = native_json_encode
        cls.lua.globals()._HttpService = http

    def setUp(self):
        self.lua.globals()._GreatVoyageVoyageData = self.lua.eval(
            "{GetShipCatalog=function() return Store.shipCatalog end, "
            "GetShipUpgradeCards=function() return Store.cardCatalog end, "
            "GetShipById=function(self,id) return Store:FindById(id,Store.shipCatalog) end, "
            "GetStartingMoney=function() return 12000 end}"
        )
        self.lua.globals()._GreatVoyageCommodityCatalog = self.lua.eval(
            "{GetAll=function() return Store.goodsCatalog end, "
            "GetById=function(_,id) return Store:FindById(id,Store.goodsCatalog) end}"
        )

    def valid(self, profile=None):
        profile = profile or base_profile()
        return self.store.ValidateProfile(
            self.store, lua_value(profile, self.lua), self.ship_catalog, self.card_catalog, self.goods_catalog
        )

    def legacy_profile(self, cargo=None):
        profile = base_profile()
        profile["schemaVersion"] = 1
        profile["core"]["cargo"] = cargo or {"id": "commodity_a", "quantity": 2, "buyPrice": 1000}
        return profile

    def test_profile_round_trip_through_lua_decoder_and_validator(self):
        raw = json.dumps(base_profile(), ensure_ascii=False, separators=(",", ":"))
        decoded = self.store.DecodeProfile(self.store, raw)
        self.assertIsNotNone(decoded)
        self.assertTrue(self.valid(python_value(decoded)))

    def test_corrupt_and_future_schema_fail_closed(self):
        self.assertIsNone(self.store.DecodeProfile(self.store, "{broken"))
        future = base_profile()
        future["schemaVersion"] = 3
        raw = json.dumps(future, separators=(",", ":"))
        self.assertIsNone(self.store.DecodeProfile(self.store, raw))

    def test_card_conservation_and_capacity_are_strict(self):
        too_many = base_profile()
        too_many["core"]["cardInventory"]["cargo"] = 99
        self.assertFalse(self.valid(too_many))
        over_capacity = base_profile()
        over_capacity["core"]["cargo"]["quantity"] = 10
        over_capacity["core"]["cargo"]["lots"] = [{"id": "commodity_a", "quantity": 10, "buyPrice": 1000}]
        self.assertFalse(self.valid(over_capacity))
        self.assertTrue(self.valid())

    def test_explicit_empty_object_and_arrays_round_trip_through_native_like_encoder(self):
        profile = base_profile()
        profile["core"]["cargo"] = {"id": "", "quantity": 0, "buyPrice": 0, "lots": []}
        profile["core"]["cardInventory"] = {}
        profile["markets"] = {"forest": [], "sky": [], "ludus": [], "nihal": []}
        raw = self.store.EncodeProfile(self.store, lua_value(profile, self.lua))
        self.assertIsNotNone(raw)
        decoded = json.loads(raw)
        self.assertEqual(decoded["core"]["cardInventory"], {})
        self.assertEqual(decoded["markets"], {"forest": [], "sky": [], "ludus": [], "nihal": []})
        self.assertTrue(self.valid(decoded))

    def test_v1_empty_and_single_cargo_upgrade_after_legacy_validation(self):
        empty = self.store.DecodeProfile(self.store, json.dumps(self.legacy_profile({"id": "", "quantity": 0, "buyPrice": 0}), separators=(",", ":")))
        self.assertIsNotNone(empty)
        self.assertEqual(empty.schemaVersion, 2)
        self.assertEqual(python_value(empty.core.cargo), {"id": "", "quantity": 0, "buyPrice": 0, "lots": []})

        single = self.store.DecodeProfile(self.store, json.dumps(self.legacy_profile(), separators=(",", ":")))
        self.assertIsNotNone(single)
        self.assertEqual(single.schemaVersion, 2)
        self.assertEqual(
            python_value(single.core.cargo),
            {"id": "commodity_a", "quantity": 2, "buyPrice": 1000, "lots": [{"id": "commodity_a", "quantity": 2, "buyPrice": 1000}]},
        )

        invalid_legacy = self.legacy_profile()
        invalid_legacy["core"]["cargo"]["quantity"] = 0
        self.assertIsNone(self.store.DecodeProfile(self.store, json.dumps(invalid_legacy, separators=(",", ":"))))

    def test_v1_migration_keeps_original_raw_as_cas_acknowledgement(self):
        legacy_raw = json.dumps(self.legacy_profile(), ensure_ascii=False, separators=(",", ":"))
        self.lua.globals().legacyRaw = legacy_raw
        storage = self.lua.eval(
            "{raw=legacyRaw,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        production = self.lua.globals().Store
        store.schemaVersion = 2
        store.ValidateProfile = production.ValidateProfile
        store.DecodeProfile = production.DecodeProfile
        store.EncodeCore = production.EncodeCore

        profile = store.LoadForPlayer(store, "user-A")
        account = store.accounts["profile-A"]
        self.assertIsNotNone(profile)
        self.assertEqual(profile.schemaVersion, 2)
        self.assertEqual(account.profile.schemaVersion, 2)
        self.assertEqual(account.acknowledgedRaw, legacy_raw)
        self.assertFalse(account.dirty)
        self.assertEqual(storage.setCalls, 0)
        self.assertEqual(gate.calls, 0)

    def test_build_runtime_profile_deep_copies_all_cargo_lots(self):
        data = self.lua.globals()._GreatVoyageVoyageData
        original = data.CopyCargo
        data.CopyCargo = self.lua.eval(
            "function(self,cargo) local lots={}; for i,lot in ipairs(cargo.lots or {}) do "
            "lots[i]={id=lot.id,quantity=lot.quantity,buyPrice=lot.buyPrice} end; "
            "return {id=cargo.id,quantity=cargo.quantity,buyPrice=cargo.buyPrice,lots=lots} end"
        )
        try:
            cargo = lua_value(
                {
                    "id": "commodity_a",
                    "quantity": 3,
                    "buyPrice": 1000,
                    "lots": [
                        {"id": "commodity_a", "quantity": 2, "buyPrice": 1000},
                        {"id": "commodity_b", "quantity": 1, "buyPrice": 1750},
                    ],
                },
                self.lua,
            )
            state = lua_value(
                {"money": 9000, "cargo": cargo, "activeShipId": "small_sampan", "cardInventory": {}, "ownedShips": {}, "safePortId": "forest"},
                self.lua,
            )
            profile = lua_value(base_profile(), self.lua)
            saved = self.store.BuildRuntimeProfile(self.store, state, profile)
            self.assertIsNotNone(saved)
            cargo.lots[1].buyPrice = 2000
            self.assertEqual(saved.core.cargo.lots[1].buyPrice, 1000)
            self.assertEqual(saved.core.cargo.lots[2].buyPrice, 1750)
        finally:
            data.CopyCargo = original

    def test_v2_mixed_cargo_with_distinct_costs_round_trips(self):
        profile = base_profile()
        profile["core"]["cargo"] = {
            "id": "commodity_a",
            "quantity": 3,
            "buyPrice": 1000,
            "lots": [
                {"id": "commodity_a", "quantity": 2, "buyPrice": 1000},
                {"id": "commodity_b", "quantity": 1, "buyPrice": 1750},
            ],
        }
        raw = self.store.EncodeProfile(self.store, lua_value(profile, self.lua))
        self.assertIsNotNone(raw)
        decoded_json = json.loads(raw)
        self.assertEqual(decoded_json["core"]["cargo"]["lots"], profile["core"]["cargo"]["lots"])
        decoded = self.store.DecodeProfile(self.store, raw)
        self.assertIsNotNone(decoded)
        self.assertEqual(python_value(decoded.core.cargo), profile["core"]["cargo"])

    def test_v2_cargo_rejects_sparse_lots_over_capacity_and_projection_mismatch(self):
        valid = base_profile()
        valid["core"]["cargo"] = {
            "id": "commodity_a",
            "quantity": 2,
            "buyPrice": 1000,
            "lots": [{"id": "commodity_a", "quantity": 1, "buyPrice": 1000}, {"id": "commodity_a", "quantity": 1, "buyPrice": 1250}],
        }
        self.assertTrue(self.valid(valid))

        sparse = base_profile()
        sparse["core"]["cargo"] = {
            "id": "commodity_a",
            "quantity": 2,
            "buyPrice": 1000,
            "lots": {1: {"id": "commodity_a", "quantity": 1, "buyPrice": 1000}, 3: {"id": "commodity_b", "quantity": 1, "buyPrice": 1250}},
        }
        self.assertFalse(self.valid(sparse))

        over_capacity = base_profile()
        over_capacity["core"]["cargo"] = {
            "id": "commodity_a",
            "quantity": 9,
            "buyPrice": 1000,
            "lots": [{"id": "commodity_a", "quantity": 8, "buyPrice": 1000}, {"id": "commodity_b", "quantity": 1, "buyPrice": 1250}],
        }
        self.assertFalse(self.valid(over_capacity))

        mismatch = base_profile()
        mismatch["core"]["cargo"]["buyPrice"] = 1300
        self.assertFalse(self.valid(mismatch))

    def test_json_encoder_exception_returns_nil_instead_of_escaping(self):
        http = self.lua.globals()._HttpService
        original = http.JSONEncode
        http.JSONEncode = lambda _self, _value: (_ for _ in ()).throw(RuntimeError("encoder failure"))
        try:
            self.assertIsNone(self.store.EncodeProfile(self.store, lua_value(base_profile(), self.lua)))
            self.assertIsNone(self.store.EncodeCore(self.store, lua_value(base_profile()["core"], self.lua)))
        finally:
            http.JSONEncode = original

    def test_get_profile_for_user_returns_single_packet_contract(self):
        profile = lua_value(base_profile(), self.lua)
        self.store.accounts["profile-A"] = self.lua.table_from({"ready": True, "conflicted": False, "profile": profile})
        self.store.profileByUser["user-A"] = "profile-A"
        packet = self.store.GetProfileForUser(self.store, "user-A")
        self.assertEqual(packet.profileCode, "profile-A")
        self.assertEqual(python_value(packet.profile), python_value(profile))
        self.store.accounts["profile-A"].ready = False
        self.assertIsNone(self.store.GetProfileForUser(self.store, "user-A"))
        self.store.accounts["profile-A"].ready = True
        self.store.accounts["profile-A"].conflicted = True
        self.assertIsNone(self.store.GetProfileForUser(self.store, "user-A"))

    def test_sync_market_projects_optional_runtime_fields_and_keeps_account_ready(self):
        profile = lua_value(base_profile(), self.lua)
        account = self.lua.table_from({"profileCode": "profile-A", "ready": True, "conflicted": False, "profile": profile, "generation": 0, "dirty": False})
        self.store.accounts["profile-A"] = account
        self.store.profileByUser["user-A"] = "profile-A"
        entries = lua_value(
            {
                "commodity_a": {"pressure": 0.35, "at": 1790000000},
                "commodity_b": {"cycle": 3, "bought": 2},
            },
            self.lua,
        )
        self.assertTrue(self.store.SyncMarket(self.store, "user-A", "forest", entries))
        self.assertTrue(account.ready)
        self.assertFalse(account.conflicted)
        self.assertEqual(len(account.profile.markets.forest[1]), 5)
        self.assertEqual(account.profile.markets.forest[1][4], -1)
        self.assertEqual(account.profile.markets.forest[1][5], 0)
        self.assertEqual(account.profile.markets.forest[2][1], "commodity_b")
        self.assertEqual(account.profile.markets.forest[2][2], 0)
        self.assertEqual(account.profile.markets.forest[2][3], 0)
        self.assertEqual(account.profile.markets.forest[2][4], 3)
        self.assertEqual(account.profile.markets.forest[2][5], 2)
        self.assertTrue(account.dirty)

    def test_user_leave_clears_status_cache_for_same_user_relogin(self):
        account = self.lua.table_from({"activeUserId": "user-A"})
        self.store.accounts["profile-A"] = account
        self.store.profileByUser["user-A"] = "profile-A"
        self.store.loadStatusByUser["user-A"] = "ready"
        self.lua.globals()._GreatVoyageVoyageState = None
        self.lua.globals()._UserService = self.lua.eval(
            "{GetUserEntityByUserId=function(self,id) return nil end}"
        )
        self.store.FlushAndWait = self.lua.eval("function(self, profileCode) return true end")
        event = self.lua.table_from({"UserId": "user-A", "ProfileCode": "profile-A"})

        self.store.HandleUserLeaveEvent(self.store, event)
        self.assertIsNone(self.store.loadStatusByUser["user-A"])

        self.lua.globals().receivedLoadStatuses = self.lua.table()
        self.store.ReceiveLoadStatus = self.lua.eval(
            "function(self,status) table.insert(receivedLoadStatuses,status) end"
        )
        self.store.SetPlayerLoadStatus(self.store, "user-A", "ready")
        self.assertEqual(list(self.lua.globals().receivedLoadStatuses.values()), ["ready"])

    def test_user_leave_preserves_status_for_reconnected_same_profile(self):
        self.store.accounts["profile-A"] = self.lua.table_from({"activeUserId": "user-A"})
        self.store.profileByUser["user-A"] = "profile-A"
        self.store.loadStatusByUser["user-A"] = "ready"
        self.lua.globals()._GreatVoyageVoyageState = None
        self.lua.globals().newUserEntity = self.lua.eval(
            "{PlayerComponent={UserId='user-A',ProfileCode='profile-A'}}"
        )
        self.lua.globals()._UserService = self.lua.eval(
            "{GetUserEntityByUserId=function(self,id) return newUserEntity end}"
        )
        self.lua.globals().receivedLoadStatuses = self.lua.table()
        self.lua.globals().leaveDuringFlushStatus = "loading"
        self.store.ReceiveLoadStatus = self.lua.eval(
            "function(self,status) table.insert(receivedLoadStatuses,status) end"
        )
        self.store.FlushAndWait = self.lua.eval(
            "function(self,profileCode) self:SetPlayerLoadStatus('user-A', leaveDuringFlushStatus); return true end"
        )
        event = self.lua.table_from({"UserId": "user-A", "ProfileCode": "profile-A"})

        self.store.HandleUserLeaveEvent(self.store, event)
        self.assertEqual(self.store.loadStatusByUser["user-A"], "loading")

        self.lua.globals().leaveDuringFlushStatus = "ready"
        self.store.HandleUserLeaveEvent(self.store, event)
        self.assertEqual(self.store.loadStatusByUser["user-A"], "ready")
        self.assertEqual(list(self.lua.globals().receivedLoadStatuses.values()), ["loading", "ready"])

    def test_legacy_market_record_is_imported_without_normalizing_bad_values(self):
        self.store.legacyMarketPrefix = "GVMarketV1"
        markets = lua_value({"forest": [], "sky": [], "ludus": [], "nihal": []}, self.lua)
        seen = self.lua.table()
        good_item = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_forest_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_a": {"pressure": 0.25, "at": 1790000000, "cycle": 2, "bought": 3}}}),
            },
            self.lua,
        )
        self.assertTrue(self.store.ImportLegacyMarketItem(self.store, good_item, markets, seen))
        self.assertEqual(markets.forest[1][1], "commodity_a")
        optional_item = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_forest_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_a": {"pressure": 0.4, "at": 1790000001}}}),
            },
            self.lua,
        )
        optional_rows = lua_value({"forest": [], "sky": [], "ludus": [], "nihal": []}, self.lua)
        self.assertTrue(self.store.ImportLegacyMarketItem(self.store, optional_item, optional_rows, self.lua.table()))
        self.assertEqual(optional_rows.forest[1][4], -1)
        self.assertEqual(optional_rows.forest[1][5], 0)
        invalid_optional = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_forest_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_a": {"pressure": 0.4, "at": 1790000001, "cycle": "bad", "bought": 3}}}),
            },
            self.lua,
        )
        self.assertFalse(self.store.ImportLegacyMarketItem(self.store, invalid_optional, optional_rows, self.lua.table()))
        bad_item = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_forest_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_a": {"pressure": 1.5, "at": 1790000000, "cycle": 2, "bought": 3}}}),
            },
            self.lua,
        )
        self.assertFalse(self.store.ImportLegacyMarketItem(self.store, bad_item, markets, self.lua.table()))

    def test_legacy_market_migration_drains_all_pages_before_returning(self):
        self.store.legacyMarketPrefix = "GVMarketV1"
        first = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_forest_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_a": {"pressure": 0.25, "at": 1790000000, "cycle": 2, "bought": 3}}}),
            },
            self.lua,
        )
        second = lua_value(
            {
                "KeyInfo": {"Key": "GVMarketV1_sky_2"},
                "Value": json.dumps({"version": 1, "entries": {"commodity_b": {"pressure": 0.5, "at": 1790000000, "cycle": 3, "bought": 4}}}),
            },
            self.lua,
        )
        pages = self.lua.eval(
            "function(firstPage, secondPage) "
            "local page={index=1, data={firstPage, secondPage}, IsLastPage=false}; "
            "function page:GetCurrentPageDatas() return {self.data[self.index]} end; "
            "function page:LoadNextPageAndWait() return 0 end; "
            "function page:MoveToNextPageAndWait() self.index=self.index+1; self.IsLastPage=self.index>=#self.data end; "
            "return page end"
        )(first, second)
        storage = self.lua.eval("{ BatchGetAndWait=function(self, keys) self.keyCount=#keys; return 0, self.pages end }")
        storage.pages = pages
        imported, migration_status = self.store.LoadLegacyMarkets(self.store, storage)
        self.assertEqual(migration_status, "ready")
        self.assertIsNotNone(imported)
        self.assertEqual(imported.forest[1][1], "commodity_a")
        self.assertEqual(imported.sky[1][1], "commodity_b")
        self.assertEqual(pages.index, 2)

        failed_pages = self.lua.eval(
            "function(firstPage, secondPage) "
            "local page={index=1, data={firstPage, secondPage}, IsLastPage=false}; "
            "function page:GetCurrentPageDatas() return {self.data[self.index]} end; "
            "function page:LoadNextPageAndWait() return 73 end; "
            "function page:MoveToNextPageAndWait() self.index=self.index+1 end; "
            "return page end"
        )(first, second)
        storage.pages = failed_pages
        failed_markets, failure_status = self.store.LoadLegacyMarkets(self.store, storage)
        self.assertIsNone(failed_markets)
        self.assertEqual(failure_status, "retry")

    def test_async_generation_and_uncertain_ack_do_not_clear_newer_dirty_state(self):
        expected = "old-profile"
        payload = "new-profile"
        storage = self.lua.eval("{ GetAndWait=function(self, key) return 0, self.observed end }")
        storage.observed = payload
        account = self.lua.table_from(
            {"profileCode": "fixture", "storage": storage, "dirty": True, "generation": 8, "saving": True, "ready": True, "activeWriteSequence": 3, "writeSequence": 3, "writeKind": "async"}
        )
        self.store.storagePrefix = "GVSaveV1"
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.lua.globals().log_warning = lambda _message: None
        self.store.FinishAsyncWrite(self.store, "fixture", 3, 7, expected, payload, 2000000, expected)
        self.assertEqual(account.dirty, True)
        self.assertEqual(account.acknowledgedGeneration, 7)
        self.assertEqual(account.conflicted, None)

        storage.observed = "third-party-value"
        account.saving = True
        account.writeKind = "async"
        self.store.FinishAsyncWrite(self.store, "fixture", 3, 7, expected, payload, 2000000, expected)
        self.assertEqual(account.dirty, True)
        self.assertEqual(account.conflicted, True)
        self.assertEqual(account.ready, False)

    def test_timeout_exact_readback_and_stale_callback_are_safe(self):
        storage = self.lua.eval("{ GetAndWait=function(self, key) return 0, self.observed end }")
        storage.observed = "payload"
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": storage,
                "dirty": True,
                "generation": 9,
                "saving": True,
                "ready": True,
                "activeWriteSequence": 5,
                "writeSequence": 5,
                "writeKind": "async",
                "inflightExpectedRaw": "old",
                "inflightPayload": "payload",
                "inflightGeneration": 8,
            }
        )
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.store.ResolveTimedOutWrite(self.store, "fixture")
        self.assertEqual(account.acknowledgedRaw, "payload")
        self.assertEqual(account.dirty, True)
        self.assertEqual(account.saving, False)
        self.assertEqual(account.activeWriteSequence, 6)
        self.store.FinishAsyncWrite(self.store, "fixture", 5, 8, "old", "older", 0, "older")
        self.assertEqual(account.acknowledgedRaw, "payload")

    def test_async_reconcile_read_yield_blocks_parallel_timeout_resolver(self):
        storage = self.lua.eval(
            "{observed='payload', first=true, "
            "GetAndWait=function(self, key) "
            "if self.first then self.first=false; store:ResolveTimedOutWrite('fixture') end; "
            "return 0, self.observed end}"
        )
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": storage,
                "dirty": True,
                "generation": 9,
                "saving": True,
                "ready": True,
                "activeWriteSequence": 5,
                "writeSequence": 5,
                "writeKind": "async",
                "inflightExpectedRaw": "old",
                "inflightPayload": "payload",
                "inflightGeneration": 9,
            }
        )
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.lua.globals().store = self.store
        self.store.FinishAsyncWrite(self.store, "fixture", 5, 9, "old", "payload", 2000000, "old")
        self.assertEqual(account.activeWriteSequence, 5)
        self.assertEqual(account.acknowledgedRaw, "payload")
        self.assertFalse(account.dirty)
        self.assertFalse(account.saving)
        self.assertEqual(account.conflicted, None)

    def test_timeout_readback_throw_is_retryable_and_keeps_stale_callback_fenced(self):
        storage = self.lua.eval(
            "{calls=0, observed='payload', GetAndWait=function(self, key) "
            "self.calls=self.calls+1; if self.calls == 1 then error('injected readback timeout') end; "
            "return 0, self.observed end}"
        )
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": storage,
                "dirty": True,
                "generation": 10,
                "saving": True,
                "ready": True,
                "activeWriteSequence": 5,
                "writeSequence": 5,
                "writeKind": "async",
                "inflightExpectedRaw": "old",
                "inflightPayload": "payload",
                "inflightGeneration": 9,
                "acknowledgedRaw": "old",
            }
        )
        self.store.storagePrefix = "GVSaveV1"
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.lua.globals().log_warning = lambda _message: None

        self.store.ResolveTimedOutWrite(self.store, "fixture")
        self.assertEqual(storage.calls, 1)
        self.assertTrue(account.saving)
        self.assertEqual(account.writeKind, "reconcile")
        self.assertTrue(account.dirty)
        self.assertEqual(account.acknowledgedRaw, "old")
        self.assertFalse(account.reconcileInProgress)

        self.store.ResolveTimedOutWrite(self.store, "fixture")
        self.assertEqual(storage.calls, 2)
        self.assertFalse(account.saving)
        self.assertIsNone(account.writeKind)
        self.assertEqual(account.acknowledgedRaw, "payload")
        self.assertEqual(account.acknowledgedGeneration, 9)
        self.assertTrue(account.dirty)

        self.store.FinishAsyncWrite(self.store, "fixture", 5, 9, "old", "stale-payload", 0, "stale-payload")
        self.assertEqual(account.acknowledgedRaw, "payload")
        self.assertTrue(account.dirty)

    def test_async_callback_readback_throw_retains_lock_for_timeout_reconciliation(self):
        storage = self.lua.eval(
            "{calls=0, observed='payload', GetAndWait=function(self, key) "
            "self.calls=self.calls+1; if self.calls == 1 then error('injected callback readback failure') end; "
            "return 0, self.observed end}"
        )
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": storage,
                "dirty": True,
                "generation": 3,
                "saving": True,
                "ready": True,
                "activeWriteSequence": 4,
                "writeSequence": 4,
                "writeKind": "async",
                "inflightExpectedRaw": "old",
                "inflightPayload": "payload",
                "inflightGeneration": 3,
            }
        )
        self.store.storagePrefix = "GVSaveV1"
        self.store.accounts = self.lua.table_from({"fixture": account})

        self.store.FinishAsyncWrite(self.store, "fixture", 4, 3, "old", "payload", 2000000, "old")
        self.assertTrue(account.saving)
        self.assertEqual(account.writeKind, "async")
        self.assertTrue(account.dirty)
        self.assertFalse(account.reconcileInProgress)

        self.store.ResolveTimedOutWrite(self.store, "fixture")
        self.assertFalse(account.saving)
        self.assertEqual(account.acknowledgedRaw, "payload")
        self.assertFalse(account.dirty)

    def configure_load_runtime(self, storage):
        lua = self.lua
        store = self.store
        store.storagePrefix = "GVSaveV1"
        store.accounts = lua.table()
        store.profileByUser = lua.table()
        store.loadStatusByUser = lua.table()
        lua.globals()._UserService = lua.eval(
            "{GetUserEntityByUserId=function(self,id) return {PlayerComponent={UserId=id,ProfileCode='profile-A'}} end}"
        )
        lua.globals().guidCounter = 0
        lua.globals()._UtilLogic.NewGuid = lua.eval(
            "function(self) guidCounter=guidCounter+1; return string.format('%032x',guidCounter) end"
        )
        lua.globals()._DataStorageService = lua.eval(
            "{GetUserDataStorage=function(self, profileCode) return storageFixture end, "
            "GetGlobalDataStorage=function(self, name) globalGateName=name; return bootstrapGateFixture end}"
        )
        lua.globals().storageFixture = storage
        lua.globals().bootstrapGateFixture = lua.eval(
            "{value='OPEN', calls=0, GetAndWait=function(self,key) "
            "self.calls=self.calls+1; return 0,self.value end, "
            "UpdateAndWait=function(self,key,expected,newValue) "
            "if self.value ~= expected then return 2000000,self.value end; "
            "self.value=newValue; return 0,newValue end}"
        )
        lua.globals().globalGateName = None
        lua.globals().loadStatuses = lua.table()
        lua.globals().loadWarnings = lua.table()
        store.ReceiveLoadStatus = lua.eval("function(self,status) table.insert(loadStatuses,status) end")
        lua.globals().log_warning = lua.eval("function(message) table.insert(loadWarnings,message) end")
        lua.globals().log = lambda _message: None

    def configure_bootstrap_runtime(self, storage=None, gate=None):
        lua = self.lua
        if storage is None:
            storage = lua.eval(
                "{raw=nil, getCalls=0, setCalls=0, GetAndWait=function(self,key) "
                "self.getCalls=self.getCalls+1; return 0,self.raw end, "
                "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
            )
        self.configure_load_runtime(storage)
        store = self.clone_store()
        if gate is None:
            gate = lua.globals().bootstrapGateFixture
        players = lua.eval(
            "{['user-A']={PlayerComponent={UserId='user-A',ProfileCode='profile-A'}}}"
        )
        lua.globals().userPlayers = players
        lua.globals()._UserService = lua.eval(
            "{GetUserEntityByUserId=function(self,id) return userPlayers[id] end}"
        )
        lua.globals().bootstrapGateFixture = gate
        store.firstCreateSetVerified = True
        store.LoadLegacyMarkets = lua.eval("function(self,storage) return {forest={},sky={},ludus={},nihal={}},'ready' end")
        store.CreateInitialProfile = lua.eval(
            "function(self,markets) return {schemaVersion=1,revision=1,safePortId='forest',core={money=12000},markets=markets} end"
        )
        store.ValidateProfile = lua.eval("function(self,profile,ships,cards,goods) return true end")
        store.EncodeProfile = lua.eval("function(self,profile) return 'created-profile-payload' end")
        store.DecodeProfile = lua.eval(
            "function(self,raw) if raw=='created-profile-payload' or raw=='existing-profile-payload' then "
            "return {schemaVersion=1,revision=1,safePortId='forest',core={money=12000},markets={forest={},sky={},ludus={},nihal={}}} end; return nil end"
        )
        store.EncodeCore = lua.eval("function(self,core) return 'core-signature' end")
        return storage, gate, players, store

    def clone_store(self, base=None):
        if base is None:
            base = self.store
        clone = self.lua.eval(
            "function(base) local copy={}; for key,value in pairs(base) do copy[key]=value end; "
            "copy.accounts={}; copy.profileByUser={}; copy.loadStatusByUser={}; return copy end"
        )(base)
        return clone

    def test_corrupt_profile_load_is_terminal_negative_cached(self):
        storage = self.lua.eval(
            "{calls=0, GetAndWait=function(self,key) self.calls=self.calls+1 return 0,'corrupt-json' end}"
        )
        self.configure_load_runtime(storage)
        original_decode = self.store.DecodeProfile
        self.store.DecodeProfile = self.lua.eval("function(self,raw) return nil end")
        try:
            self.assertIsNone(self.store.LoadForPlayer(self.store, "user-A"))
            self.assertIsNone(self.store.LoadForPlayer(self.store, "user-A"))
            account = self.store.accounts["profile-A"]
            self.assertTrue(account.loadBlocked)
            self.assertEqual(storage.calls, 1)
            self.assertEqual(list(self.lua.globals().loadStatuses.values()), ["loading", "blocked"])
        finally:
            self.store.DecodeProfile = original_decode

    def test_two_initializer_instances_only_one_cas_owner_sets_missing_profile(self):
        storage, gate, players, store_a = self.configure_bootstrap_runtime()
        store_b = self.clone_store(store_a)
        players["user-B"] = self.lua.table_from(
            {"PlayerComponent": self.lua.table_from({"UserId": "user-B", "ProfileCode": "profile-A"})}
        )
        self.lua.globals().secondStore = store_b
        gate.UpdateAndWait = self.lua.eval(
            "function(self,key,expected,newValue) "
            "if self.value ~= expected then return 2000000,self.value end; "
            "self.value=newValue; self.lastClaimValue=newValue; if self.runSecond then self.runSecond=false; secondStore:LoadForPlayer('user-B') end; "
            "return 0,newValue end"
        )
        gate.runSecond = True

        profile = store_a.LoadForPlayer(store_a, "user-A")
        self.assertIsNotNone(profile)
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(storage.raw, "created-profile-payload")
        self.assertEqual(gate.value, "OPEN")
        self.assertEqual(self.lua.globals().globalGateName, "GVSaveV1Bootstrap")
        account_a = store_a.accounts["profile-A"]
        account_b = store_b.accounts["profile-A"]
        self.assertNotEqual(gate.lastClaimValue, "BUSY:" + account_b.bootstrapGateToken)
        self.assertFalse(account_a.saving)
        self.assertEqual(account_b.bootstrapGateState, "busy")

    def test_busy_missing_and_crashed_owner_gate_fail_closed(self):
        for gate_value, expected_state in (("BUSY:other-instance", "busy"), (None, "missing"), ("BUSY:crashed-owner", "busy")):
            with self.subTest(gate_value=gate_value):
                storage = self.lua.eval(
                    "{raw=nil,getCalls=0,setCalls=0,GetAndWait=function(self,key) self.getCalls=self.getCalls+1; "
                    "if self.getCalls == 1 then return 1000002,nil end; return 0,self.raw end, "
                    "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
                )
                _, gate, _, store = self.configure_bootstrap_runtime(storage)
                self.lua.globals()._UtilLogic.ServerElapsedSeconds = 0
                gate.value = gate_value
                gate.GetAndWait = self.lua.eval(
                    "function(self,key) if self.value == nil then return 1000002,nil end; return 0,self.value end"
                )
                self.assertIsNone(store.LoadForPlayer(store, "user-A"))
                account = store.accounts["profile-A"]
                self.assertEqual(storage.setCalls, 0)
                self.assertEqual(account.bootstrapGateState, expected_state)
                self.assertFalse(account.ready)
                expected_status = "setup" if expected_state == "missing" else "retry"
                self.assertEqual(account.loadFailureStatus, expected_status)
                self.assertEqual(store.loadStatusByUser["user-A"], expected_status)
                get_calls = storage.getCalls
                self.assertIsNone(store.LoadForPlayer(store, "user-A"))
                self.assertEqual(store.loadStatusByUser["user-A"], expected_status)
                self.assertEqual(storage.getCalls, get_calls)
                self.assertEqual(storage.setCalls, 0)
                if expected_state == "missing":
                    warnings = [load_warning for load_warning in self.lua.globals().loadWarnings.values()]
                    self.assertTrue(any("GVSaveV1Bootstrap gate 未預置" in warning for warning in warnings))
                    self.assertTrue(all("user-A" not in warning and "profile-A" not in warning and "BUSY:" not in warning for warning in warnings))
                    gate.value = "OPEN"
                    self.lua.globals()._UtilLogic.ServerElapsedSeconds = 31
                    self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
                    self.assertTrue(account.ready)
                    self.assertIsNone(account.loadFailureStatus)
                    self.assertEqual(store.loadStatusByUser["user-A"], "ready")
                    statuses = [status for status in self.lua.globals().loadStatuses.values()]
                    self.assertEqual(statuses[-2:], ["loading", "ready"])
                else:
                    warnings = [load_warning for load_warning in self.lua.globals().loadWarnings.values()]
                    self.assertTrue(any("bootstrap gate claim failed state=busy code=0" in warning for warning in warnings))

    def test_profile_read_failure_logs_state_and_error_code(self):
        storage = self.lua.eval(
            "{GetAndWait=function(self,key) return 1234567,nil end, "
            "SetAndWait=function(self,key,value) error('profile writes must not run') end}"
        )
        _, _, _, store = self.configure_bootstrap_runtime(storage)

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(store.loadStatusByUser["user-A"], "retry")
        warnings = [load_warning for load_warning in self.lua.globals().loadWarnings.values()]
        self.assertTrue(any("profile read failed state=GetAndWait code=1234567" in warning for warning in warnings))
        self.assertTrue(all("user-A" not in warning and "profile-A" not in warning for warning in warnings))

    def test_profile_read_throw_retries_without_write(self):
        storage = self.lua.eval(
            "{setCalls=0,GetAndWait=function(self,key) error('read unavailable') end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; error('profile writes must not run') end}"
        )
        _, _, _, store = self.configure_bootstrap_runtime(storage)

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(store.loadStatusByUser["user-A"], "retry")
        self.assertEqual(storage.setCalls, 0)
        warnings = [load_warning for load_warning in self.lua.globals().loadWarnings.values()]
        self.assertTrue(any("profile read failed state=GetAndWait code=throw" in warning for warning in warnings))

    def test_profile_not_found_with_open_gate_initializes_once(self):
        storage = self.lua.eval(
            "{raw=nil,getCalls=0,setCalls=0,GetAndWait=function(self,key) "
            "self.getCalls=self.getCalls+1; if self.getCalls == 1 then return 1000002,nil end; return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)

        profile = store.LoadForPlayer(store, "user-A")

        self.assertIsNotNone(profile)
        self.assertTrue(store.accounts["profile-A"].ready)
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(gate.value, "OPEN")
        self.assertEqual(store.loadStatusByUser["user-A"], "ready")

    def test_profile_and_gate_not_found_requests_setup_without_profile_write(self):
        storage = self.lua.eval(
            "{raw=nil,getCalls=0,setCalls=0,GetAndWait=function(self,key) "
            "self.getCalls=self.getCalls+1; if self.getCalls == 1 then return 1000002,nil end; return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        gate.value = None
        gate.GetAndWait = self.lua.eval("function(self,key) self.calls=self.calls+1; return 1000002,nil end")
        gate.UpdateAndWait = self.lua.eval("function(self,key,expected,value) error('NotFound gate must never be updated') end")

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))

        account = store.accounts["profile-A"]
        self.assertEqual(account.bootstrapGateState, "missing")
        self.assertEqual(account.loadFailureStatus, "setup")
        self.assertEqual(store.loadStatusByUser["user-A"], "setup")
        self.assertEqual(storage.setCalls, 0)
        self.assertIsNone(storage.raw)

    def test_profile_not_found_with_raw_payload_retries_without_write(self):
        storage = self.lua.eval(
            "{raw='existing-profile-payload',setCalls=0,GetAndWait=function(self,key) return 1000002,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))

        self.assertFalse(store.accounts["profile-A"].loadBlocked)
        self.assertEqual(store.accounts["profile-A"].loadFailureStatus, "retry")
        self.assertEqual(store.loadStatusByUser["user-A"], "retry")
        self.assertEqual(storage.setCalls, 0)
        self.assertEqual(gate.calls, 0)

    def test_prewrite_abort_releases_gate_after_confirmed_profile_not_found(self):
        storage = self.lua.eval("{GetAndWait=function(self,key) return 1000002,nil end}")
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        gate.value = "BUSY:prewrite-owner"
        account = self.lua.eval(
            "{profileCode='profile-A',bootstrapGateToken='prewrite-owner',"
            "bootstrapGateValue='BUSY:prewrite-owner',bootstrapGateStorage=bootstrapGateFixture}"
        )
        account.storage = storage

        released = store.ReleaseBootstrapGateBeforeWrite(store, account)

        self.assertTrue(released)
        self.assertEqual(gate.value, "OPEN")
        self.assertIsNone(account.bootstrapGateToken)

    def test_prewrite_abort_never_releases_after_set_attempt(self):
        storage = self.lua.eval("{GetAndWait=function(self,key) return 1000002,nil end}")
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        gate.value = "BUSY:prewrite-owner"
        account = self.lua.eval(
            "{profileCode='profile-A',bootstrapGateToken='prewrite-owner',"
            "bootstrapGateValue='BUSY:prewrite-owner',bootstrapGateStorage=bootstrapGateFixture,"
            "bootstrapSetAttempted=true}"
        )
        account.storage = storage

        self.assertFalse(store.ReleaseBootstrapGateBeforeWrite(store, account))
        self.assertEqual(gate.value, "BUSY:prewrite-owner")

    def test_prewrite_abort_keeps_gate_for_profile_not_found_with_raw_or_throw(self):
        for read_expression in (
            "function(self,key) return 1000002,'existing-profile-payload' end",
            "function(self,key) error('profile read unavailable') end",
        ):
            with self.subTest(read_expression=read_expression):
                storage = self.lua.eval("{GetAndWait=" + read_expression + "}")
                _, gate, _, store = self.configure_bootstrap_runtime(storage)
                gate.value = "BUSY:prewrite-owner"
                account = self.lua.eval(
                    "{profileCode='profile-A',bootstrapGateToken='prewrite-owner',"
                    "bootstrapGateValue='BUSY:prewrite-owner',bootstrapGateStorage=bootstrapGateFixture}"
                )
                account.storage = storage

                self.assertFalse(store.ReleaseBootstrapGateBeforeWrite(store, account))
                self.assertEqual(gate.value, "BUSY:prewrite-owner")

    def test_unknown_gate_cas_and_readback_never_set_or_release(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        gate.calls = 0
        gate.GetAndWait = self.lua.eval(
            "function(self,key) self.calls=self.calls+1; if self.calls == 1 then return 0,'OPEN' end; "
            "error('injected gate readback timeout') end"
        )
        gate.UpdateAndWait = self.lua.eval(
            "function(self,key,expected,newValue) self.value=newValue; error('injected CAS timeout') end"
        )

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        self.assertEqual(storage.setCalls, 0)
        self.assertTrue(gate.value.startswith("BUSY:"))
        self.assertEqual(account.bootstrapGateValue, gate.value)
        self.assertEqual(account.bootstrapGateState, "uncertain")

    def test_unknown_gate_claim_never_resends_while_open_and_accepts_late_exact_owner(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        gate.updateCalls = 0
        gate.UpdateAndWait = self.lua.eval(
            "function(self,key,expected,newValue) if expected == 'OPEN' then "
            "self.updateCalls=self.updateCalls+1; error('injected unknown gate claim') end; "
            "if self.value ~= expected then return 2000000,self.value end; "
            "self.value=newValue; return 0,newValue end"
        )

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        owner_value = account.bootstrapGateValue
        self.assertEqual(gate.updateCalls, 1)
        self.assertEqual(gate.value, "OPEN")
        self.assertEqual(storage.setCalls, 0)
        self.assertTrue(account.bootstrapClaimAttempted)

        self.lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(gate.updateCalls, 1)
        self.assertEqual(storage.setCalls, 0)
        self.assertEqual(gate.value, "OPEN")

        gate.value = owner_value
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(gate.updateCalls, 1)
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(gate.value, "OPEN")

    def test_unknown_initial_set_and_readback_keep_gate_until_exact_retry(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,getCalls=0,failVerify=true,GetAndWait=function(self,key) "
            "self.getCalls=self.getCalls+1; if self.failVerify and self.setCalls > 0 then error('injected profile readback timeout') end; "
            "return 0,self.raw end, SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; "
            "self.raw=value; error('injected Set timeout') end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        store.LoadLegacyMarkets = self.lua.eval(
            "function(self,storage) self.legacyCalls=(self.legacyCalls or 0)+1; "
            "return {forest={},sky={},ludus={},nihal={}},'ready' end"
        )
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        held_value = gate.value
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(storage.raw, account.bootstrapPayload)
        self.assertTrue(held_value.startswith("BUSY:"))
        self.assertEqual(gate.value, held_value)
        self.assertTrue(account.bootstrapSetAttempted)

        storage.failVerify = False
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        profile = store.LoadForPlayer(store, "user-A")
        self.assertIsNotNone(profile)
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(store.legacyCalls, 1)
        self.assertEqual(gate.value, "OPEN")
        self.assertTrue(account.ready)

    def test_unknown_set_with_absent_payload_never_resubmits_and_waits_for_late_commit(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; error('injected Set timeout without visible value') end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        held_value = gate.value
        self.assertEqual(storage.setCalls, 1)
        self.assertIsNone(storage.raw)
        self.assertTrue(account.bootstrapSetAttempted)
        self.assertEqual(gate.value, held_value)

        self.lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(gate.value, held_value)
        self.assertTrue(account.bootstrapSetAttempted)

        storage.raw = account.bootstrapPayload
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(storage.setCalls, 1)
        self.assertEqual(gate.value, "OPEN")
        self.assertTrue(account.ready)

    def test_existing_profile_skips_global_bootstrap_gate(self):
        storage = self.lua.eval(
            "{raw='existing-profile-payload',setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        profile = store.LoadForPlayer(store, "user-A")
        self.assertIsNotNone(profile)
        self.assertTrue(store.accounts["profile-A"].ready)
        self.assertEqual(gate.calls, 0)
        self.assertEqual(storage.setCalls, 0)
        self.assertIsNone(self.lua.globals().globalGateName)

    def test_pre_set_migration_failure_releases_only_after_exact_profile_read(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        store.LoadLegacyMarkets = self.lua.eval("function(self,storage) return nil,'blocked' end")
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(storage.setCalls, 0)
        self.assertEqual(gate.value, "OPEN")
        self.assertTrue(store.accounts["profile-A"].loadBlocked)

    def test_identity_change_after_gate_claim_prevents_set_and_releases_unwritten_claim(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, players, store = self.configure_bootstrap_runtime(storage)
        gate.UpdateAndWait = self.lua.eval(
            "function(self,key,expected,newValue) "
            "if self.value ~= expected then return 2000000,self.value end; self.value=newValue; "
            "if string.sub(newValue,1,5)=='BUSY:' then userPlayers['user-A'].PlayerComponent.ProfileCode='changed-profile' end; "
            "return 0,newValue end"
        )
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        self.assertEqual(storage.setCalls, 0)
        self.assertFalse(account.loading)
        self.assertEqual(gate.value, "OPEN")
        self.assertIsNone(store.profileByUser["user-A"])

    def test_bootstrap_gate_namespace_is_derived_for_isolated_qa_prefix(self):
        storage = self.lua.eval("{GetAndWait=function(self,key) return 0,'OPEN' end, UpdateAndWait=function(self,key,expected,value) return 0,value end}")
        _, _, _, store = self.configure_bootstrap_runtime()
        account = self.lua.table_from({})
        store.storagePrefix = "GVSaveV1_QA_case"
        self.lua.globals()._DataStorageService.GetGlobalDataStorage = self.lua.eval(
            "function(self,name) globalGateName=name; return isolatedGate end"
        )
        self.lua.globals().isolatedGate = storage
        self.assertTrue(store.ClaimBootstrapGate(store, account))
        self.assertEqual(self.lua.globals().globalGateName, "GVSaveV1_QA_caseBootstrap")

    def test_missing_gate_warning_uses_prefix_specific_storage_name(self):
        storage = self.lua.eval(
            "{raw=nil,setCalls=0,GetAndWait=function(self,key) return 0,self.raw end, "
            "SetAndWait=function(self,key,value) self.setCalls=self.setCalls+1; self.raw=value; return 0 end}"
        )
        _, gate, _, store = self.configure_bootstrap_runtime(storage)
        store.storagePrefix = "GVSaveV1_QA_case"
        gate.value = None
        gate.GetAndWait = self.lua.eval("function(self,key) return 1000002,nil end")

        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        warnings = [load_warning for load_warning in self.lua.globals().loadWarnings.values()]
        self.assertTrue(any("GVSaveV1_QA_caseBootstrap gate 未預置" in warning for warning in warnings))
        self.assertTrue(all("GVSaveV1Bootstrap gate 未預置" not in warning for warning in warnings))
        self.assertEqual(storage.setCalls, 0)

    def run_start_voyage_for_status(self, departure_status):
        state_path = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
        parameters, body = extract_method_from_with_params(state_path, "StartVoyage")
        internal_parameters, internal_body = extract_method_from_with_params(state_path, "StartVoyageInternal")
        lua = self.lua
        lua.execute("VoyageStart = {}")
        lua.execute(
            f"VoyageStart.StartVoyageInternal = function(self, {', '.join(internal_parameters)})\n"
            f"{internal_body}\nend"
        )
        lua.execute(f"VoyageStart.StartVoyage = function(self, {', '.join(parameters)})\n{body}\nend")
        state = lua.table_from(
            {
                "status": departure_status,
                "profileCode": "profile-A",
                "ship": lua.table_from({"id": "merchant", "hull": 40, "stats": lua.table(), "durationMultiplier": 1}),
                "safePortId": "forest",
            }
        )
        voyage = lua.globals().VoyageStart
        voyage.voyageByPlayer = lua.table_from({"user-A": state})
        voyage.voyageDurationSeconds = 60
        voyage.GetOrCreateState = lua.eval("function(self,userId) return self.voyageByPlayer[userId] end")
        voyage.GetPortIdFromMap = lua.eval("function(self,map) return 'forest' end")
        voyage.IsNearOwnShip = lua.eval("function(self,player,port) return true end")
        voyage.PreviewDirectRoute = lua.eval("function(self,origin,destination) return {accepted=true,originId=origin,destinationId=destination,segments={},distance=100} end")
        voyage.PublishSnapshot = lua.eval("function(self,playerId,state) end")
        voyage.ClearLegacyEncounter = lua.eval("function(self,state) end")
        voyage._T = lua.table()
        player = lua.eval("{PlayerComponent={ProfileCode='profile-A',MoveToMapPosition=function(self,map,pos) end},CurrentMapName='map_forest_port'}")
        lua.globals()._UserService = lua.eval("{GetUserEntityByUserId=function(self,id) return playerFixture end}")
        lua.globals().playerFixture = player
        lua.globals()._GreatVoyageProfileStore = lua.eval(
            "{MarkStateDirty=function(self,userId,state) return true end,FlushAndWait=function(self,profile) return true end}"
        )
        lua.globals()._UtilLogic.ServerElapsedSeconds = 100
        lua.globals().senderUserId = "user-A"
        lua.globals().Vector2 = lua.eval("function(x,y) return {x=x,y=y} end")
        lua.globals().log = lambda _message: None
        lua.globals().log_warning = lambda _message: None
        voyage.StartVoyage(voyage, "sky")
        return state

    def test_arrived_and_repaired_sunk_states_can_depart_again(self):
        for previous_status in ("arrived", "sunk"):
            with self.subTest(previous_status=previous_status):
                state = self.run_start_voyage_for_status(previous_status)
                self.assertEqual(state.status, "sailing")
                self.assertEqual(state.originId, "forest")
                self.assertEqual(state.destinationId, "sky")
                self.assertFalse(state.departurePending)
                self.assertFalse(state.persistencePending)

    def test_pending_arrival_and_retry_window_do_not_advance_voyage(self):
        state_path = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
        parameters, body = extract_method_from_with_params(state_path, "AdvanceVoyage")
        lua = self.lua
        lua.execute("VoyageAdvance = {}")
        lua.execute(f"VoyageAdvance.AdvanceVoyage = function(self, {', '.join(parameters)})\n{body}\nend")
        state = lua.table_from(
            {
                "status": "arrived",
                "persistencePending": True,
                "elapsedSailingSeconds": 60,
                "distanceTravelled": 100,
                "route": lua.table_from({"distance": 100}),
            }
        )
        voyage = lua.globals().VoyageAdvance
        voyage.voyageByPlayer = lua.table_from({"user-A": state})
        voyage.GetOrCreateState = lua.eval("function(self,userId) return self.voyageByPlayer[userId] end")
        lua.globals()._UtilLogic.ServerElapsedSeconds = 100
        lua.globals().senderUserId = "user-A"
        voyage.AdvanceVoyage(voyage, 5)
        self.assertEqual(state.status, "arrived")
        self.assertEqual(state.elapsedSailingSeconds, 60)
        self.assertEqual(state.distanceTravelled, 100)

        state.persistencePending = False
        state.status = "sailing"
        state.settlementRetryAt = 150
        state.elapsedSailingSeconds = 10
        voyage.AdvanceVoyage(voyage, 5)
        self.assertEqual(state.elapsedSailingSeconds, 10)
        self.assertEqual(state.settlementRetryAt, 150)

    def test_transient_profile_read_uses_30_second_backoff_then_retries(self):
        storage = self.lua.eval(
            "{calls=0, GetAndWait=function(self,key) self.calls=self.calls+1 return 73,nil end}"
        )
        self.configure_load_runtime(storage)
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = 100
        self.assertIsNone(self.store.LoadForPlayer(self.store, "user-A"))
        self.assertIsNone(self.store.LoadForPlayer(self.store, "user-A"))
        self.assertEqual(storage.calls, 1)
        self.assertEqual(self.store.accounts["profile-A"].nextRetryAt, 130)
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = 131
        self.assertIsNone(self.store.LoadForPlayer(self.store, "user-A"))
        self.assertEqual(storage.calls, 2)
        self.assertEqual(self.store.accounts["profile-A"].nextRetryAt, 161)

    def test_quick_same_user_relogin_rehydrates_idle_state_after_leave_capture(self):
        state_path = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
        capture_body = extract_method_from(state_path, "CaptureProfileForLeave")
        capture_body = capture_body.replace("--", "--", 1)
        get_params, get_body = extract_method_from_with_params(state_path, "GetOrCreateState")
        lua = self.lua
        lua.execute("Voyage = {}")
        lua.execute(f"Voyage.CaptureProfileForLeave = function(self, playerId)\n{capture_body}\nend")
        lua.execute(f"Voyage.GetOrCreateState = function(self, {', '.join(get_params)})\n{get_body}\nend")
        old_state = lua.table_from({"profileCode": "profile-A", "status": "sailing", "airBattle": lua.table_from({"phase": "active"})})
        voyage = lua.globals().Voyage
        voyage.voyageByPlayer = lua.table_from({"same-user": old_state})
        voyage._T = lua.table_from({"cardMarketByPlayer": lua.table_from({"same-user": lua.table_from(["old-market"])})})
        voyage.voyageDurationSeconds = 60
        voyage.CreateOwnedShip = lua.eval("function(self, d) return {id=d.id, name=d.name, maxHull=d.maxHull, maxShield=d.maxShield, maxArmor=d.maxArmor, cargoCapacity=d.cargoCapacity, hull=d.maxHull, shield=d.maxShield, armor=d.maxArmor, slots={'','',''}} end")
        voyage.CalculateShipUpgrades = lua.eval("function(self, id, slots) return {} end")
        voyage.ApplyShipUpgrades = lua.eval("function(self, ship, upgrades) end")
        voyage.GetPortIdFromMap = lua.eval("function(self, map) return 'forest' end")
        voyage.MovePlayerToPort = lua.eval("function(self, playerId, portId) end")
        profile = lua.table_from({
            "safePortId": "forest",
            "core": lua.table_from({
                "money": 12000,
                "cargo": lua.table_from({"id": "", "quantity": 0, "buyPrice": 0, "lots": lua.table()}),
                "cardInventory": lua.table(),
                "activeShipId": "small_sampan",
                "ships": lua.table_from({"small_sampan": lua.table_from({"hull": 71, "shield": 18, "armor": 39, "slots": lua.table_from(["", "", ""])})}),
            }),
        })
        profile_store = lua.table_from({"profileByUser": lua.table_from({"same-user": "profile-A"})})
        profile_store.LoadForPlayer = lua.eval("function(self, userId) return self.profile end")
        profile_store.profile = profile
        voyage_profile_store = profile_store
        lua.globals()._GreatVoyageProfileStore = voyage_profile_store
        previous_voyage_data = lua.globals()._GreatVoyageVoyageData
        lua.globals()._GreatVoyageVoyageData = lua.eval(
            "{GetShipById=function(self,id) return {id='small_sampan',name='Sampan',maxHull=100,maxShield=20,maxArmor=40,cargoCapacity=8} end, "
            "CopyCargo=function(self,cargo) return {id=cargo.id,quantity=cargo.quantity,buyPrice=cargo.buyPrice,lots={}} end}"
        )
        lua.globals()._UserService = lua.eval("{GetUserEntityByUserId=function(self,id) return {PlayerComponent={ProfileCode='profile-A'},CurrentMapName='map_forest_port'} end}")
        voyage.CaptureProfileForLeave(voyage, "same-user")
        self.assertIsNone(voyage.voyageByPlayer["same-user"])
        self.assertIsNone(voyage._T.cardMarketByPlayer["same-user"])
        restored = voyage.GetOrCreateState(voyage, "same-user")
        self.assertIsNotNone(restored)
        self.assertNotEqual(restored, old_state)
        self.assertEqual(restored.profileCode, "profile-A")
        self.assertEqual(restored.status, "idle")
        self.assertEqual(restored.ship.hull, 71)
        self.assertIsNone(restored.airBattle)
        lua.globals()._GreatVoyageVoyageData = previous_voyage_data

    def test_update_async_throw_reconciles_exact_write_and_releases_saving(self):
        storage = self.lua.eval(
            "{observed='old-payload', GetAndWait=function(self, key) return 0, self.observed end, "
            "UpdateAsync=function(self, key, expected, payload, callback) self.observed=payload; error('uncertain ack') end}"
        )
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": storage,
                "dirty": True,
                "generation": 2,
                "saving": False,
                "ready": True,
                "acknowledgedRaw": "old-payload",
                "profile": lua_value(base_profile(), self.lua),
                "writeSequence": 0,
            }
        )
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.lua.globals().log_warning = lambda _message: None
        self.assertFalse(self.store.FlushAsync(self.store, "fixture"))
        self.assertEqual(account.acknowledgedRaw, storage.observed)
        self.assertFalse(account.dirty)
        self.assertFalse(account.saving)
        self.assertEqual(account.writeKind, None)

    def test_second_flush_cannot_resolve_or_replace_inflight_sync_write(self):
        account = self.lua.table_from(
            {
                "profileCode": "fixture",
                "storage": self.lua.table(),
                "dirty": True,
                "generation": 4,
                "saving": False,
                "ready": True,
                "acknowledgedRaw": "old-payload",
                "profile": lua_value(base_profile(), self.lua),
                "writeSequence": 0,
            }
        )
        storage = account.storage
        storage.getCalls = 0
        storage.secondResult = None
        storage.GetAndWait = self.lua.eval("function(self, key) self.getCalls=self.getCalls+1 return 0, 'old-payload' end")
        storage.UpdateAndWait = self.lua.eval(
            "function(self, key, expected, payload) "
            "self.lastPayload=payload; local second = store:FlushAndWait('fixture'); self.secondResult=second; "
            "return 0, payload end"
        )
        self.store.accounts = self.lua.table_from({"fixture": account})
        self.lua.globals().store = self.store
        result = self.store.FlushAndWait(self.store, "fixture")
        self.assertTrue(result)
        self.assertFalse(storage.secondResult)
        self.assertEqual(storage.getCalls, 0)
        self.assertEqual(account.acknowledgedRaw, storage.lastPayload)
        self.assertFalse(account.saving)
        self.assertEqual(account.writeKind, None)

    def test_write_ack_is_exact_and_conflicts_fail_closed(self):
        self.assertTrue(self.store.IsWriteAcknowledged(self.store, 0, "new", "old", "new"))
        self.assertFalse(self.store.IsWriteAcknowledged(self.store, 0, "other", "old", "new"))
        self.assertFalse(self.store.IsWriteAcknowledged(self.store, 2000000, "new", "old", "new"))

    def test_production_lua_method_bodies_parse_in_lupa(self):
        paths = [
            STORE_PATH,
            ROOT / "RootDesk/MyDesk/Economy/GreatVoyagePlayerMarket.mlua",
            ROOT / "RootDesk/MyDesk/GreatVoyagePlayerAttack.mlua",
        ]
        for path in paths:
            bodies = method_bodies(path)
            self.assertTrue(bodies, path.name)
            for body in bodies:
                self.lua.eval("function()\n" + body + "\nend")
        voyage_path = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
        for name in [
            "GetOrCreateState",
            "PersistSettledVoyage",
            "CaptureProfileForLeave",
            "CaptureSafeProfilesForShutdown",
            "CompleteShipRequest",
            "CompleteEconomyRequest",
            "StartVoyage",
            "ReceiveTransactionFeedback",
            "AbandonVoyage",
        ]:
            body = extract_method_from(voyage_path, name)
            self.lua.eval("function()\n" + body + "\nend")

    def test_max_market_payload_bytes_are_measured_in_lua_utf8(self):
        profile = base_profile()
        for port in ("forest", "sky", "ludus", "nihal"):
            profile["markets"][port] = [
                [f"commodity_{port}_{index:03d}", 0.5, 1790000000, 120, 10]
                for index in range(156)
            ]
        raw = self.store.EncodeProfile(self.store, lua_value(profile, self.lua))
        self.assertIsNotNone(raw)
        byte_count = len(raw.encode("utf-8"))
        self.assertLess(byte_count, 50000)
        print(f"max-fixture records=624 utf8-bytes={byte_count} credit-at-4000={byte_count / 4000:.2f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
