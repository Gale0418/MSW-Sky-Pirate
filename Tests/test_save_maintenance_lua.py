import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "RootDesk/MyDesk/Persistence/GreatVoyageProfileStore.mlua"


def extract_method(source, name):
    match = re.search(
        r"\tmethod\s+[^\n]+\s+" + re.escape(name) + r"\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        source,
        re.S,
    )
    if match is None:
        raise AssertionError(f"production method not found: {name}")
    params = [part.strip().split()[-1] for part in match.group(1).split(",") if part.strip()]
    return params, match.group(2)


def make_runtime(reads=None):
    source = STORE_PATH.read_text(encoding="utf-8")
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("Store = {}")
    methods = (
        "GetProfileKey",
        "IsSameBoundProfile",
        "SetPlayerLoadStatus",
        "SetLoadFailure",
        "LoadForPlayer",
    )
    for name in methods:
        extracted = extract_method(source, name)
        params, body = extracted
        lua.execute(f"Store[{name!r}] = function({', '.join(['self', *params])})\n{body}\nend")

    store = lua.globals().Store
    for name, value in {
        "storagePrefix": "GVSaveV1",
        "legacyMarketPrefix": "GVMarketV1",
        "schemaVersion": 2,
        "notFoundCode": 1000002,
        "compareFailedCode": 2000000,
        "maxPayloadBytes": 50000,
    }.items():
        setattr(store, name, value)
    store.accounts = lua.table()
    store.profileByUser = lua.table()
    store.loadStatusByUser = lua.table()
    store.openPorts = lua.table_from(["forest", "sky", "ludus", "nihal"])
    store.ReceiveLoadStatus = lua.eval("function(self, status, userId) end")

    lua.globals()._UtilLogic = lua.table_from({"ServerElapsedSeconds": 0, "NewGuid": lambda _self: "new-owner-token"})
    lua.globals()._HttpService = lua.eval("{JSONEncode=function(self, value) return 'payload' end}")
    lua.globals()._GreatVoyageSaveMaintenance = lua.table_from({"enabled": False})
    lua.globals()._GreatVoyageVoyageData = lua.eval(
        "{GetShipCatalog=function() return {} end, GetShipUpgradeCards=function() return {} end}"
    )
    lua.globals()._GreatVoyageCommodityCatalog = lua.eval("{GetAll=function() return {} end}")

    user = lua.table_from({"PlayerComponent": lua.table_from({"UserId": "user-A", "ProfileCode": "profile-A"})})
    lua.globals()._UserService = lua.table_from({
        "GetUserEntityByUserId": lambda _self, user_id: user if user_id == "user-A" else None
    })

    state = {"raw": None, "reads": list(reads or []), "read_index": 0, "get_calls": 0, "set_calls": 0, "writes": [], "on_set": None, "on_get": None}
    calls = {"user_storage": 0}

    def get_and_wait(_self, key):
        state["get_calls"] += 1
        if state["on_get"] is not None:
            state["on_get"]()
        if state["read_index"] < len(state["reads"]):
            result = state["reads"][state["read_index"]]
            state["read_index"] += 1
            return result
        return 0, state["raw"]

    def set_and_wait(_self, key, value):
        state["set_calls"] += 1
        state["writes"].append((key, value))
        if state["on_set"] is not None:
            state["on_set"](key, value)
        state["raw"] = value
        return 0

    storage = lua.table_from({"GetAndWait": get_and_wait, "SetAndWait": set_and_wait})
    def get_user_storage(_self, profile_code):
        calls["user_storage"] += 1
        return storage

    lua.globals()._DataStorageService = lua.table_from({"GetUserDataStorage": get_user_storage})
    lua.globals().loadWarnings = lua.table()
    lua.globals().log_warning = lua.eval("function(message) table.insert(loadWarnings, message) end")
    lua.globals().log = lambda _message: None

    # Keep the profile domain deterministic; these tests exercise only LoadForPlayer's storage flow.
    store.LoadLegacyMarkets = lua.eval("function(self, storage) return {forest={},sky={},ludus={},nihal={}}, 'ready' end")
    store.CreateInitialProfile = lua.eval("function(self, markets) return {schemaVersion=2,revision=1,safePortId='forest',core={},markets=markets} end")
    store.ValidateProfile = lua.eval("function(self, profile, ships, cards, goods) return true end")
    store.EncodeProfile = lua.eval("function(self, profile) return 'created-profile-payload' end")
    store.DecodeProfile = lua.eval(
        "function(self, raw) if raw == 'created-profile-payload' or raw == 'existing-profile-payload' then "
        "return {schemaVersion=2,revision=1,safePortId='forest',core={},markets={forest={},sky={},ludus={},nihal={}}} end; return nil end"
    )
    store.EncodeCore = lua.eval("function(self, core) return 'core-signature' end")
    state["user"] = user
    return lua, store, storage, state, calls


class DirectFirstCreateLuaTests(unittest.TestCase):
    def test_confirmed_missing_creates_once_directly(self):
        for first_read in ((0, None), (1000002, None)):
            with self.subTest(first_read=first_read):
                lua, store, storage, state, calls = make_runtime(reads=[first_read, (1000002, None)])
                profile = store.LoadForPlayer(store, "user-A")
                self.assertIsNotNone(profile)
                self.assertTrue(store.accounts["profile-A"].ready)
                self.assertEqual(state["set_calls"], 1)
                self.assertEqual(state["writes"], [("GVSaveV1_profile-A", "created-profile-payload")])
                self.assertEqual(store.loadStatusByUser["user-A"], "ready")
                account = store.accounts["profile-A"]
                self.assertIsNone(account.bootstrapSetAttempted)
                self.assertIsNone(account.bootstrapPayload)

    def test_existing_profile_is_decoded_without_write(self):
        _, store, _, state, calls = make_runtime(reads=[(0, "existing-profile-payload")])
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertTrue(store.accounts["profile-A"].ready)
        self.assertEqual(state["set_calls"], 0)

    def test_get_error_throw_and_notfound_with_data_never_write(self):
        for reads in ([(9, None)], [(1000002, "unexpected-payload")]):
            _, store, _, state, calls = make_runtime(reads=reads)
            self.assertIsNone(store.LoadForPlayer(store, "user-A"))
            self.assertEqual(state["set_calls"], 0)

        lua, store, storage, state, calls = make_runtime()
        storage.GetAndWait = lua.eval("function(self, key) error('injected profile read throw') end")
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(state["set_calls"], 0)

    def test_recheck_finds_existing_profile_before_set(self):
        _, store, _, state, calls = make_runtime(
            reads=[(1000002, None), (0, "existing-profile-payload")]
        )
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertTrue(store.accounts["profile-A"].ready)
        self.assertEqual(state["set_calls"], 0)

    def test_recheck_errors_and_inconsistent_missing_never_write(self):
        cases = (
            [(1000002, None), (17, None)],
            [(1000002, None), (1000002, "unexpected-payload")],
        )
        for reads in cases:
            with self.subTest(reads=reads):
                _, store, _, state, _ = make_runtime(reads=reads)
                self.assertIsNone(store.LoadForPlayer(store, "user-A"))
                self.assertEqual(state["set_calls"], 0)

        lua, store, storage, state, _ = make_runtime(reads=[(1000002, None)])
        storage.GetAndWait = lua.eval(
            "function(self, key) self.calls=(self.calls or 0)+1; "
            "if self.calls == 1 then return 1000002,nil end; error('injected recheck throw') end"
        )
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(state["set_calls"], 0)

    def test_unknown_set_is_not_resubmitted_and_late_exact_payload_becomes_ready(self):
        lua, store, storage, state, calls = make_runtime(reads=[(1000002, None), (1000002, None)])
        storage.SetAndWait = lua.eval("function(self, key, value) self.calls=(self.calls or 0)+1; error('injected Set timeout') end")
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        self.assertTrue(account.bootstrapSetAttempted)
        self.assertEqual(storage.calls, 1)

        reads_before_retry = state["get_calls"]
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(storage.calls, 1)
        self.assertEqual(state["get_calls"], reads_before_retry)

        lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(storage.calls, 1)
        self.assertFalse(account.ready)

        state["raw"] = account.bootstrapPayload
        lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertTrue(account.ready)
        self.assertEqual(storage.calls, 1)

    def test_unknown_set_with_different_late_payload_blocks_without_rewrite(self):
        lua, store, storage, state, _ = make_runtime(reads=[(1000002, None), (1000002, None)])
        storage.SetAndWait = lua.eval("function(self, key, value) self.calls=(self.calls or 0)+1; error('injected Set timeout') end")
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        account = store.accounts["profile-A"]
        state["raw"] = "different-profile-payload"
        lua.globals()._UtilLogic.ServerElapsedSeconds = account.nextRetryAt
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertTrue(account.loadBlocked or account.corrupt)
        self.assertEqual(storage.calls, 1)

    def test_reentrant_same_instance_does_not_issue_second_set(self):
        lua, store, _, state, calls = make_runtime(reads=[(1000002, None), (1000002, None)])
        state["on_set"] = lambda _key, _value: store.LoadForPlayer(store, "user-A")
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(state["set_calls"], 1)

    def test_profile_identity_change_after_read_prevents_creation(self):
        _, store, _, state, _ = make_runtime(reads=[(1000002, None)])
        state["on_get"] = lambda: setattr(state["user"].PlayerComponent, "ProfileCode", "changed-profile")
        self.assertIsNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(state["set_calls"], 0)
        self.assertIsNone(store.profileByUser["user-A"])
        self.assertFalse(store.accounts["profile-A"].loading)

    def test_maintenance_enabled_does_not_block_profile_lookup(self):
        lua, store, _, state, calls = make_runtime(reads=[(0, "existing-profile-payload")])
        lua.globals()._GreatVoyageSaveMaintenance.enabled = True
        self.assertIsNotNone(store.LoadForPlayer(store, "user-A"))
        self.assertEqual(state["set_calls"], 0)
        self.assertEqual(calls["user_storage"], 1)


if __name__ == "__main__":
    unittest.main()
