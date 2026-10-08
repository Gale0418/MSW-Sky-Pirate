import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "RootDesk/MyDesk/Persistence/GreatVoyageSaveMaintenance.mlua"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")


def extract_block(kind, name):
    pattern = re.compile(
        rf"\t{kind}\s+[^\n]*\b{re.escape(name)}\(([^\n]*)\)\s*\n(.*?)\n\tend(?=\s|$)",
        re.S,
    )
    match = pattern.search(SOURCE)
    if match is None:
        raise AssertionError(f"production {kind} not found: {name}")
    parameters = [part.strip().split()[-1] for part in match.group(1).split(",") if part.strip()]
    return parameters, match.group(2)


def make_runtime(*, enabled=True, rollout_authorized=True, world_id="world-a", user_id="maintainer", players=None, instances=None, gate=(1000002, None), published=True):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("Maintenance = {}")
    for method in ("HasSafeContext", "IsOnlyReleaseInstance", "TrySeedGate"):
        parameters, body = extract_block("method", method)
        lua.execute(f"Maintenance.{method} = function(self, {', '.join(parameters)})\n{body}\nend")
    parameters, body = extract_block("method", "OnBeginPlay")
    lua.execute(f"Maintenance.OnBeginPlay = function({', '.join(['self', *parameters])})\n{body}\nend")
    parameters, body = extract_block("handler", "HandleUserEnterEvent")
    lua.execute(f"Maintenance.HandleUserEnterEvent = function(self, {', '.join(parameters)})\n{body}\nend")

    maintenance = lua.globals().Maintenance
    maintenance.enabled = enabled
    maintenance.initialRolloutAuthorized = rollout_authorized
    maintenance.expectedWorldId = world_id
    maintenance.maintenanceUserId = user_id
    maintenance.attempted = False
    maintenance.running = False
    maintenance.setAttempted = False
    maintenance.storageName = "GVSaveV1Bootstrap"
    maintenance.storagePrefix = "GVSaveV1"
    maintenance.gateKey = "gate"
    maintenance.openValue = "OPEN"
    maintenance.notFoundCode = 1000002

    users = lua.table()
    for index, player_id in enumerate(players if players is not None else [user_id], 1):
        users[index] = lua.table_from({"PlayerComponent": lua.table_from({"UserId": player_id})})
    accounts = lua.table()
    store = lua.table_from({"storagePrefix": "GVSaveV1", "bootstrapGateKey": "gate", "accounts": accounts})
    lua.globals()._GreatVoyageProfileStore = store
    lua.globals()._UserService = lua.table_from({"UserEntities": lua.table_from({"Values": users})})
    env = lua.table_from({"WorldId": "world-a", "IsPublishedPlay": lambda _self: published})
    lua.globals().Environment = env

    instance_pages = instances if instances is not None else [[{"Id": "instance-a", "CurrentUserCount": 1}]]
    page_state = {"index": 0, "moves": 0, "ok": True, "pages": True, "move_hook": None}
    def get_page_data():
        index = page_state["index"]
        data = instance_pages[index] if index < len(instance_pages) else []
        page_obj.IsLastPage = index >= len(instance_pages) - 1
        return lua.table_from([lua.table_from(item) for item in data])

    def move_page(_self):
        page_state["moves"] += 1
        page_state["index"] += 1
        if page_state["move_hook"] is not None:
            page_state["move_hook"]()
        return page_state.get("move_ok", True)

    page_obj = lua.table_from({"GetCurrentPageDatas": lambda _self: get_page_data(), "MoveToNextPageAndWait": move_page})
    def get_pages(_self):
        if not page_state["pages"]:
            return True, None
        return page_state["ok"], page_obj

    world_service = lua.table_from({"WorldInstanceId": "instance-a", "GetWorldInstanceInfoPagesAndWait": get_pages})
    lua.globals()._WorldInstanceService = world_service

    calls = {"global_storage": 0, "get": 0, "set": 0, "profile": 0, "logs": []}
    fault_counts = lua.table_from({"instances": 0, "storage": 0, "get": 0, "set": 0, "readback": 0, "page": 0})
    lua.globals().MaintenanceFaultCounts = fault_counts
    calls["fault_counts"] = fault_counts
    current_gate = {"result": gate}
    callbacks = {"on_get": None, "on_set": None, "get_count": 0, "set_count": 0}
    def get_and_wait(_self, key):
        calls["get"] += 1
        callbacks["get_count"] += 1
        if callbacks["on_get"] is not None:
            callbacks["on_get"]()
        return current_gate["result"]

    def set_and_wait(_self, key, value):
        calls["set"] += 1
        callbacks["set_count"] += 1
        if callbacks["on_set"] is not None:
            callbacks["on_set"]()
        return 0

    storage = lua.table_from({"GetAndWait": get_and_wait, "SetAndWait": set_and_wait})
    callbacks["storage"] = storage
    def get_global_storage(_self, name):
        calls["global_storage"] += 1
        return storage

    lua.globals()._DataStorageService = lua.table_from({"GetGlobalDataStorage": get_global_storage})
    lua.globals()._GreatVoyageProfileStore.accounts = accounts
    lua.globals().log = lambda message: calls["logs"].append(str(message))
    return lua, maintenance, users, store, page_state, calls, current_gate, callbacks


class SaveMaintenanceLuaTests(unittest.TestCase):
    def run_gate(self, **kwargs):
        runtime = make_runtime(**kwargs)
        lua, maintenance, users, store, page_state, calls, gate, callbacks = runtime
        maintenance.TrySeedGate(maintenance, maintenance.maintenanceUserId)
        return runtime

    def test_disabled_runtime_makes_no_storage_calls(self):
        _, maintenance, _, _, _, calls, _, _ = self.run_gate(enabled=False)
        self.assertEqual((calls["global_storage"], calls["get"], calls["set"], calls["profile"]), (0, 0, 0, 0))
        self.assertFalse(maintenance.attempted)

    def test_wrong_world_or_user_and_nonexclusive_do_not_touch_storage(self):
        for kwargs, triggering_user in [
            ({"enabled": True, "rollout_authorized": True, "world_id": "different"}, "maintainer"),
            ({"enabled": True, "rollout_authorized": True}, "someone-else"),
            ({"enabled": True, "rollout_authorized": False}, "maintainer"),
        ]:
            _, maintenance, _, _, _, calls, _, _ = make_runtime(**kwargs)
            maintenance.TrySeedGate(maintenance, triggering_user)
            self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0))

    def test_requires_one_local_player_and_one_complete_instance(self):
        cases = [
            {"players": ["maintainer", "guest"]},
            {"instances": [[{"Id": "instance-a", "CurrentUserCount": 1}, {"Id": "instance-b", "CurrentUserCount": 0}]]},
            {"instances": [[{"Id": "instance-b", "CurrentUserCount": 1}]]},
            {"instances": [[{"Id": "instance-a", "CurrentUserCount": 2}]]},
            {"instances": [[{"Id": "instance-a", "CurrentUserCount": 1}], [{"Id": "instance-b", "CurrentUserCount": 0}]]},
        ]
        for case in cases:
            _, _, _, _, _, calls, _, _ = self.run_gate(enabled=True, rollout_authorized=True, **case)
            self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0), case)

    def test_instance_page_error_stops_before_storage(self):
        _, maintenance, _, _, pages, calls, _, _ = make_runtime(enabled=True)
        pages["ok"] = False
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0))

    def test_false_page_advance_with_empty_next_page_is_not_complete(self):
        runtime = make_runtime(instances=[
            [{"Id": "instance-a", "CurrentUserCount": 1}],
            [],
        ])
        _, maintenance, _, _, page_state, calls, _, _ = runtime
        page_state["move_ok"] = False
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual(page_state["moves"], 1)
        self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0))
        _, maintenance, _, _, pages, calls, _, _ = make_runtime(enabled=True)
        pages["pages"] = False
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0))

    def test_only_confirmed_missing_gate_is_seeded_once(self):
        for result in ((0, None), (1000002, None)):
            runtime = make_runtime(enabled=True, gate=result)
            _, maintenance, _, _, _, calls, gate, _ = runtime
            def set_gate(_self, key, value):
                calls["set"] += 1
                gate["result"] = (0, "OPEN")
                return 0
            maintenance_set_storage(runtime, set_gate)
            maintenance.TrySeedGate(maintenance, "maintainer")
            self.assertEqual((calls["set"], calls["get"]), (1, 2))
            self.assertEqual(calls["profile"], 0)
            self.assertTrue(any(message.startswith("[VRF][SaveV1][Maintenance]") for message in calls["logs"]))

    def test_open_is_noop_and_empty_busy_other_or_error_are_not_written(self):
        for result in ((0, "OPEN"), (0, ""), (0, "BUSY"), (0, "other"), (9, None), (1000002, "unexpected")):
            _, _, _, _, _, calls, _, _ = self.run_gate(enabled=True, gate=result)
            self.assertEqual(calls["set"], 0, result)
            self.assertEqual(calls["profile"], 0)

    def test_busy_token_is_not_written_or_logged(self):
        token = "BUSY:private-instance-token"
        runtime = self.run_gate(gate=(0, token))
        _, _, _, _, _, calls, _, _ = runtime
        self.assertEqual(calls["set"], 0)
        self.assertNotIn(token, "\n".join(calls["logs"]))

    def test_set_timeout_is_confirmed_only_by_exact_readback(self):
        runtime = make_runtime(enabled=True)
        _, maintenance, _, _, _, calls, gate, callbacks = runtime
        def set_timeout(_self, key, value):
            calls["set"] += 1
            gate["result"] = (0, "OPEN")
            return 9
        maintenance_set_storage(runtime, set_timeout)
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual(calls["set"], 1)
        self.assertTrue(any("gate OPEN confirmed by exact readback" in message for message in calls["logs"]))
        self.assertEqual(calls["profile"], 0)

    def test_unknown_set_result_stops_without_resend(self):
        runtime = make_runtime(enabled=True)
        _, maintenance, _, _, _, calls, _, _ = runtime
        maintenance_set_storage(runtime, lambda _self, key, value: (calls.__setitem__("set", calls["set"] + 1) or 9))
        maintenance.TrySeedGate(maintenance, "maintainer")
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual(calls["set"], 1)
        self.assertTrue(any("indeterminate" in message for message in calls["logs"]))

    def test_owner_leave_or_new_player_during_yield_stops_followup_calls(self):
        for mutate in ("leave", "join"):
            lua, maintenance, users, _, _, calls, _, callbacks = make_runtime(enabled=True)
            if mutate == "leave":
                callbacks["on_get"] = lambda: users.__setitem__(1, None)
            else:
                callbacks["on_get"] = lambda: users.__setitem__(2, lua.table_from({"PlayerComponent": lua.table_from({"UserId": "guest"})}))
            maintenance.TrySeedGate(maintenance, "maintainer")
            self.assertEqual((calls["get"], calls["set"]), (1, 0), mutate)

    def test_owner_change_after_set_yield_stops_readback(self):
        for mutate in ("leave", "join"):
            runtime = make_runtime(enabled=True)
            lua, maintenance, users, _, _, calls, gate, callbacks = runtime
            def set_and_change(_self, key, value):
                calls["set"] += 1
                gate["result"] = (0, "OPEN")
                if mutate == "leave":
                    users[1] = None
                else:
                    users[2] = lua.table_from({"PlayerComponent": lua.table_from({"UserId": "guest"})})
                return 0
            maintenance_set_storage(runtime, set_and_change)
            maintenance.TrySeedGate(maintenance, "maintainer")
            self.assertEqual((calls["set"], calls["get"]), (1, 1), mutate)
            self.assertTrue(any("context changed after Set" in message for message in calls["logs"]))

    def test_reentrant_trigger_and_rejected_accounts_never_write(self):
        runtime = make_runtime(enabled=True)
        _, maintenance, _, store, _, calls, gate, callbacks = runtime
        def set_once(_self, key, value):
            calls["set"] += 1
            maintenance.TrySeedGate(maintenance, "maintainer")
            gate["result"] = (0, "OPEN")
            return 0
        maintenance_set_storage(runtime, set_once)
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual(calls["set"], 1)
        self.assertEqual(calls["profile"], 0)
        lua, maintenance, _, store, _, calls, _, _ = make_runtime(enabled=True)
        store.accounts[1] = lua.table_from(lua_account({"saving": True}))
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual((calls["global_storage"], calls["set"]), (0, 0))

    def test_store_identity_and_published_play_are_required(self):
        for mutation in ("prefix", "key", "draft"):
            runtime = make_runtime(enabled=True, published=mutation != "draft")
            _, maintenance, _, store, _, calls, _, _ = runtime
            if mutation == "prefix":
                store.storagePrefix = "other"
            elif mutation == "key":
                store.bootstrapGateKey = "profile"
            maintenance.TrySeedGate(maintenance, "maintainer")
            self.assertEqual((calls["global_storage"], calls["set"]), (0, 0), mutation)

    def test_owner_change_during_instance_page_yield_is_rejected(self):
        lua, maintenance, users, _, pages, calls, _, _ = make_runtime(
            enabled=True,
            instances=[[{"Id": "instance-a", "CurrentUserCount": 1}], [{"Id": "instance-a", "CurrentUserCount": 1}]],
        )
        pages["move_hook"] = lambda: users.__setitem__(1, None)
        maintenance.TrySeedGate(maintenance, "maintainer")
        self.assertEqual((calls["global_storage"], calls["get"], calls["set"]), (0, 0, 0))

    def test_trigger_annotations_and_no_profile_storage_calls(self):
        self.assertIn('@ExecSpace("ServerOnly")\n\t@EventSender("Service", "UserService")\n\thandler HandleUserEnterEvent', SOURCE)
        self.assertNotIn("GetUserDataStorage", SOURCE)
        self.assertNotIn("SetUserDataStorage", SOURCE)
        self.assertLess(len(SOURCE.splitlines()), 250)
        lua, maintenance, _, _, _, _, _, _ = make_runtime(enabled=True)
        maintenance.HandleUserEnterEvent(maintenance, lua.table_from({"UserId": "maintainer"}))
        self.assertTrue(maintenance.attempted)

    def test_lua_exceptions_stop_without_retry_or_profile_calls(self):
        scenarios = ("instance_pages", "page_data", "storage_factory", "gate_get", "gate_set", "set_throw_missing", "readback")
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                runtime = make_runtime(
                    instances=[[{"Id": "instance-a", "CurrentUserCount": 1}]],
                    gate=(1000002, None),
                )
                lua, maintenance, _, _, _, calls, gate, _ = runtime
                faults = calls["fault_counts"]
                if scenario == "instance_pages":
                    lua.globals()._WorldInstanceService.GetWorldInstanceInfoPagesAndWait = lua.eval(
                        "function(self) MaintenanceFaultCounts.instances = MaintenanceFaultCounts.instances + 1; error('instance pages boom') end"
                    )
                elif scenario == "page_data":
                    lua.globals()._WorldInstanceService.GetWorldInstanceInfoPagesAndWait = lua.eval(
                        "function(self) MaintenanceFaultCounts.instances = MaintenanceFaultCounts.instances + 1; return true, {IsLastPage=true, GetCurrentPageDatas=function(self) MaintenanceFaultCounts.page = MaintenanceFaultCounts.page + 1; error('page data boom') end} end"
                    )
                elif scenario == "storage_factory":
                    lua.globals()._DataStorageService.GetGlobalDataStorage = lua.eval(
                        "function(self, name) MaintenanceFaultCounts.storage = MaintenanceFaultCounts.storage + 1; error('storage factory boom') end"
                    )
                elif scenario == "gate_get":
                    runtime[7]["storage"].GetAndWait = lua.eval(
                        "function(self, key) MaintenanceFaultCounts.get = MaintenanceFaultCounts.get + 1; error('gate read boom') end"
                    )
                elif scenario == "gate_set":
                    lua.globals()._SetHook = lambda _self, key, value: (calls.__setitem__("set", calls["set"] + 1), gate.__setitem__("result", (0, "OPEN")))
                    runtime[7]["storage"].SetAndWait = lua.eval(
                        "function(self, key, value) MaintenanceFaultCounts.set = MaintenanceFaultCounts.set + 1; _SetHook(self, key, value); error('set timeout boom') end"
                    )
                elif scenario == "set_throw_missing":
                    runtime[7]["storage"].SetAndWait = lua.eval(
                        "function(self, key, value) MaintenanceFaultCounts.set = MaintenanceFaultCounts.set + 1; error('set outcome unknown') end"
                    )
                else:
                    runtime[7]["storage"].GetAndWait = lua.eval(
                        "(function() local count = 0; return function(self, key) count = count + 1; if count == 1 then return 1000002, nil end; MaintenanceFaultCounts.readback = MaintenanceFaultCounts.readback + 1; error('readback boom') end end)()"
                    )
                maintenance.TrySeedGate(maintenance, "maintainer")
                maintenance.TrySeedGate(maintenance, "maintainer")
                self.assertTrue(maintenance.attempted)
                self.assertFalse(maintenance.running)
                self.assertEqual(calls["profile"], 0)
                if scenario == "gate_set":
                    self.assertEqual(calls["set"], 1)
                    self.assertEqual(calls["get"], 2)
                    self.assertTrue(any(message.startswith("[VRF][SaveV1][Maintenance]") for message in calls["logs"]))
                elif scenario == "set_throw_missing":
                    self.assertEqual((faults.set, calls["get"]), (1, 2))
                    self.assertTrue(any("indeterminate" in message for message in calls["logs"]))
                elif scenario == "readback":
                    self.assertEqual(calls["set"], 1)
                    self.assertEqual(faults.readback, 1)
                else:
                    self.assertEqual(calls["set"], 0, scenario)


def lua_account(fields):
    return fields


def maintenance_set_storage(runtime, set_method):
    runtime[7]["storage"].SetAndWait = set_method


if __name__ == "__main__":
    unittest.main()
