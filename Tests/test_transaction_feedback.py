"""Behavior tests that execute the transaction methods extracted from production mLua."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "RootDesk" / "MyDesk" / "UI" / "GreatVoyageAdventureController.mlua"
VOYAGE_STATE = ROOT / "RootDesk" / "MyDesk" / "GreatVoyageVoyageState.mlua"
METHODS = (
    "FormatMoney",
    "HandleTransactionFeedback",
    "ShowNextShipAcquired",
    "UpdateShipAcquired",
    "StartVoyage",
    "StartVoyageWithReceipt",
    "BeginVoyage",
    "CloseWorldMap",
    "HandleDepartureResult",
    "SellGood",
    "OnEndPlay",
)
STATE_METHODS = (
    "StartVoyage",
    "StartVoyageWithReceipt",
    "ReceiveDepartureResult",
    "StartVoyageInternal",
    "AbandonVoyage",
)


def _extract_method(source: str, method_name: str) -> tuple[list[str], str]:
    lines = source.splitlines()
    header = re.compile(
        rf"^(?P<indent>[\t ]*)method\s+\w+\s+{re.escape(method_name)}\((?P<args>[^)]*)\)\s*$"
    )

    for start, line in enumerate(lines):
        match = header.match(line)
        if match is None:
            continue

        indent = match.group("indent")
        args = [
            parameter.strip().split()[-1]
            for parameter in match.group("args").split(",")
            if parameter.strip()
        ]
        for end in range(start + 1, len(lines)):
            if lines[end] == f"{indent}end":
                return args, "\n".join(lines[start + 1 : end])
        raise AssertionError(f"Could not find the closing end for {method_name}")

    raise AssertionError(f"Production method {method_name} was not found in {CONTROLLER}")


def _production_lua() -> str:
    source = CONTROLLER.read_text(encoding="utf-8")
    definitions = []
    for method_name in METHODS:
        args, body = _extract_method(source, method_name)
        parameter_list = ", ".join(["self", *args])
        definitions.append(f"function Controller.{method_name}({parameter_list})\n{body}\nend")
    return "\n".join(definitions)


def _production_state_lua() -> str:
    source = VOYAGE_STATE.read_text(encoding="utf-8")
    definitions = ["VoyageState = {}"]
    for method_name in STATE_METHODS:
        args, body = _extract_method(source, method_name)
        parameter_list = ", ".join(["self", *args])
        definitions.append(f"function VoyageState.{method_name}({parameter_list})\n{body}\nend")
    return "\n".join(definitions)


def _method_exec_space(source: str, method_name: str) -> str | None:
    lines = source.splitlines()
    header = re.compile(
        rf"^[\t ]*method\s+\w+\s+{re.escape(method_name)}\([^)]*\)\s*$"
    )
    for index, line in enumerate(lines):
        if header.match(line) and index > 0:
            match = re.fullmatch(r"[\t ]*@ExecSpace\(\"([^\"]+)\"\)[\t ]*", lines[index - 1])
            return match.group(1) if match else None
    return None


@pytest.fixture
def lua_game() -> LuaRuntime:
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(
        """
        Controller = {}
        _GreatVoyageVoyageData = { ships = {} }
        function _GreatVoyageVoyageData:GetShipById(shipId)
            return self.ships[shipId]
        end

        _SoundService = { calls = {} }
        function _SoundService:PlaySound(ruid, volume)
            table.insert(self.calls, { ruid = ruid, volume = volume })
        end

        function isvalid(value)
            return value ~= nil and value.valid ~= false
        end
        function DataRef(value) return value end
        function Vector3(x, y, z) return { x = x, y = y, z = z } end
        function Color(r, g, b, a) return { r = r, g = g, b = b, a = a } end
        function log(_) end

        _GreatVoyageVoyageState = {
            clientSnapshotStatus = "idle",
            clientSnapshotOriginId = "forest",
            clientSnapshotDestinationId = "",
            clientSnapshotLastReason = "",
            requests = {},
        }
        function _GreatVoyageVoyageState:StartVoyage(destinationId)
            table.insert(self.requests, destinationId)
        end
        function _GreatVoyageVoyageState:StartVoyageWithReceipt(destinationId, sequence)
            table.insert(self.requests, { destinationId = destinationId, sequence = sequence })
        end
        _Phase0VoyagePrototype = nil

        ImageType = { Simple = 1 }
        PreserveSpriteType = { AspectOnly = 1 }

        function newController()
            return setmetatable({
                _T = {},
                acquiredElapsed = -1,
                acquiredGroup = {
                    Enable = false,
                    CanvasGroupComponent = { GroupAlpha = 1 },
                },
                acquiredPresentation = { UIScale = { x = 1, y = 1, z = 1 } },
                acquiredShipName = { Text = "" },
                acquiredShipImage = { ImageRUID = "", Type = 0, PreserveSprite = 0 },
                coinSoundRuid = "coin-success",
                acquiredSoundRuid = "ship-fanfare",
                selectedDestinationId = "sky",
                currentPortId = "forest",
                pendingDestinationId = "sky",
                messageText = { Text = "" },
                worldMapModal = { Enable = true },
                shopModal = { Enable = false },
                promptButtonEntity = { Enable = false },
                modalType = "world_map",
                modalOpen = true,
            }, { __index = Controller })
        end
        """
    )
    lua.execute(_production_lua())
    lua.execute(_production_state_lua())
    return lua


def _new_controller(lua: LuaRuntime):
    return lua.globals().newController()


def _add_ship(lua: LuaRuntime, ship_id: str, name: str | None = None) -> None:
    lua.globals()._GreatVoyageVoyageData.ships[ship_id] = lua.table_from(
        {"name": name or ship_id, "spriteRuid": f"sprite-{ship_id}"}
    )


def _sound_calls(lua: LuaRuntime) -> list:
    calls = lua.globals()._SoundService.calls
    return [calls[index] for index in range(1, len(calls) + 1)]


def test_transaction_kind_allowlist_and_money_success_sound(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    valid_kinds = ("goods_buy", "goods_sell", "card_buy", "card_sell")

    for revision, kind in enumerate(valid_kinds, start=1):
        lua_game.globals().Controller.HandleTransactionFeedback(controller, kind, "", revision)

    lua_game.globals().Controller.HandleTransactionFeedback(controller, "ship_sell", "", 99)
    lua_game.globals().Controller.HandleTransactionFeedback(controller, "unknown", "", 99)

    calls = _sound_calls(lua_game)
    assert len(calls) == 4
    assert all(call["ruid"] == "coin-success" and call["volume"] == pytest.approx(0.65) for call in calls)
    assert controller._T.feedbackRevisions.ship_sell is None
    assert controller._T.feedbackRevisions.unknown is None


def test_duplicate_and_stale_revisions_do_not_replay(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    feedback = lua_game.globals().Controller.HandleTransactionFeedback

    feedback(controller, "goods_buy", "cargo", 8)
    feedback(controller, "goods_buy", "cargo", 8)
    feedback(controller, "goods_buy", "cargo", 7)
    feedback(controller, "goods_buy", "cargo", -1)

    assert len(_sound_calls(lua_game)) == 1
    assert controller._T.feedbackRevisions.goods_buy == 8


def test_successful_ship_buys_queue_and_play_one_fanfare_each(lua_game: LuaRuntime) -> None:
    _add_ship(lua_game, "sampan", "Starter Sampan")
    _add_ship(lua_game, "forest", "Forest Ship")
    controller = _new_controller(lua_game)
    feedback = lua_game.globals().Controller.HandleTransactionFeedback
    update = lua_game.globals().Controller.UpdateShipAcquired

    feedback(controller, "ship_buy", "sampan", 1)
    feedback(controller, "ship_buy", "forest", 2)

    assert controller.acquiredShipName.Text == "Starter Sampan"
    assert len(_sound_calls(lua_game)) == 1
    assert controller._T.acquiredQueue[1] == "forest"

    update(controller, 3.4)
    assert controller.acquiredShipName.Text == "Forest Ship"
    assert controller.acquiredGroup.Enable is True
    assert len(_sound_calls(lua_game)) == 2
    assert all(call["ruid"] == "ship-fanfare" for call in _sound_calls(lua_game))

    update(controller, 3.4)
    assert controller.acquiredGroup.Enable is False
    assert controller.acquiredElapsed == -1
    assert len(_sound_calls(lua_game)) == 2


def test_ship_show_fade_hide_and_negative_delta_clamp(lua_game: LuaRuntime) -> None:
    _add_ship(lua_game, "sampan", "Starter Sampan")
    controller = _new_controller(lua_game)
    lua_game.globals().Controller.HandleTransactionFeedback(controller, "ship_buy", "sampan", 1)
    update = lua_game.globals().Controller.UpdateShipAcquired

    update(controller, -1)
    assert controller.acquiredElapsed == 0
    assert controller.acquiredPresentation.UIScale.x == pytest.approx(0.72)
    assert controller.acquiredGroup.CanvasGroupComponent.GroupAlpha == pytest.approx(0)

    update(controller, 0.14)
    assert controller.acquiredPresentation.UIScale.x == pytest.approx(0.965)
    assert controller.acquiredGroup.CanvasGroupComponent.GroupAlpha == pytest.approx(1)

    update(controller, 3.02)
    assert controller.acquiredGroup.CanvasGroupComponent.GroupAlpha == pytest.approx((3.4 - 3.16) / 0.45)
    update(controller, 0.25)
    assert controller.acquiredGroup.Enable is False
    assert controller.acquiredElapsed == -1


def test_format_money_handles_maximum_integer(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    result = lua_game.globals().Controller.FormatMoney(controller, 2147483647)
    assert result == "2,147,483,647"


def test_invalid_ship_does_not_consume_revision(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    feedback = lua_game.globals().Controller.HandleTransactionFeedback

    feedback(controller, "ship_buy", "missing-ship", 12)
    assert controller._T.feedbackRevisions.ship_buy is None
    assert controller.acquiredElapsed == -1
    assert _sound_calls(lua_game) == []

    _add_ship(lua_game, "valid-ship", "Valid Ship")
    feedback(controller, "ship_buy", "valid-ship", 12)
    assert controller._T.feedbackRevisions.ship_buy == 12
    assert controller.acquiredElapsed == 0
    assert controller.acquiredShipName.Text == "Valid Ship"


def test_voyage_success_waits_for_matching_sequence_receipt(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    begin = lua_game.globals().Controller.BeginVoyage
    handle = lua_game.globals().Controller.HandleDepartureResult
    state = lua_game.globals()._GreatVoyageVoyageState

    begin(controller)
    assert len(state.requests) == 1
    assert state.requests[1].destinationId == "sky"
    assert state.requests[1].sequence == 1
    assert controller._T.pendingVoyageStart is True
    assert controller.worldMapModal.Enable is True
    assert controller.messageText.Text == "出航請求已送出，等船長確認中…"

    # Old or mismatched receipts cannot finish the active request.
    handle(controller, 0, True, "舊成功回執")
    assert controller._T.pendingVoyageStart is True
    assert controller.worldMapModal.Enable is True

    handle(controller, 1, True, "出發！航程開始囉！")
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is False
    assert controller.messageText.Text == "離港啟程！開始航行！"


def test_same_reason_rejection_clears_pending_and_allows_retry(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    begin = lua_game.globals().Controller.BeginVoyage
    handle = lua_game.globals().Controller.HandleDepartureResult
    state = lua_game.globals()._GreatVoyageVoyageState
    reason = "存檔尚未確認，這趟先不能出航。"

    begin(controller)
    handle(controller, 1, False, reason)
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is True
    assert controller.messageText.Text == reason

    begin(controller)
    assert len(state.requests) == 2
    assert state.requests[2].sequence == 2
    assert controller._T.pendingVoyageStart is True
    handle(controller, 2, False, reason)

    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is True
    assert controller.modalOpen is True
    assert controller.messageText.Text == reason


def test_stale_receipt_is_ignored_and_duplicate_click_does_not_resend(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    begin = lua_game.globals().Controller.BeginVoyage
    handle = lua_game.globals().Controller.HandleDepartureResult
    state = lua_game.globals()._GreatVoyageVoyageState

    begin(controller)
    handle(controller, 1, False, "上一趟拒絕")
    begin(controller)
    begin(controller)
    handle(controller, 1, False, "先前的拒絕訊息")

    assert len(state.requests) == 2
    assert state.requests[2].sequence == 2
    assert controller._T.pendingVoyageStart is True
    assert controller.worldMapModal.Enable is True

    begin(controller)
    assert len(state.requests) == 2

    handle(controller, 1, True, "舊回執")
    assert controller._T.pendingVoyageStart is True
    assert controller.worldMapModal.Enable is True

    handle(controller, 2, True, "本次成功")
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is False


def test_on_end_play_clears_pending_voyage_confirmation(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    lua_game.globals().Controller.BeginVoyage(controller)
    assert controller._T.pendingVoyageStart is True

    lua_game.globals().Controller.OnEndPlay(controller)

    assert controller._T.pendingVoyageStart is False
    assert controller._T.pendingVoyageStartSequence is None


def test_server_receipts_accept_only_new_matching_departure_and_retry_same_reason(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    lua_game.globals()._GreatVoyageAdventureController = controller
    lua_game.globals()._UserService = lua_game.table_from(
        {"LocalPlayer": {"valid": True, "PlayerComponent": {"UserId": "player-1"}}}
    )
    lua_game.globals().senderUserId = "player-1"
    lua_game.execute(
        """
        _GreatVoyageVoyageState = setmetatable({
            _T = {},
            voyageByPlayer = { ["player-1"] = { status = "idle", voyageSequence = 4 } },
            requests = {},
            testAccept = false,
            testThrow = false,
            testReason = "存檔尚未確認，這趟先不能出航。",
        }, { __index = VoyageState })
        function _GreatVoyageVoyageState:StartVoyageWithReceipt(destinationId, sequence)
            table.insert(self.requests, { destinationId = destinationId, sequence = sequence })
        end
        function _GreatVoyageVoyageState:StartVoyageInternal(playerId, destinationId)
            local state = self.voyageByPlayer[playerId]
            if self.testThrow then error("simulated internal failure") end
            state.lastReason = self.testReason
            if self.testAccept then
                state.status = "sailing"
                state.voyageSequence = state.voyageSequence + 1
                state.originId = "forest"
                state.destinationId = destinationId
                state.route = { accepted = true, originId = "forest", destinationId = destinationId }
                state.lastReason = "出發！航程開始囉！"
            end
        end
        """
    )

    begin = lua_game.globals().Controller.BeginVoyage
    begin(controller)
    assert controller._T.pendingVoyageStart is True
    assert controller.messageText.Text == "出航請求已送出，等船長確認中…"
    state = lua_game.globals()._GreatVoyageVoyageState
    request = state.requests[1]
    lua_game.globals().VoyageState.StartVoyageWithReceipt(state, request.destinationId, request.sequence)
    assert controller._T.pendingVoyageStart is False
    assert controller.messageText.Text == "存檔尚未確認，這趟先不能出航。"
    assert controller.worldMapModal.Enable is True

    # 相同拒絕原因的下一次請求仍由新 sequence 收到回執並結束等待。
    begin(controller)
    assert controller._T.departureRequestSequence == 2
    request = state.requests[2]
    lua_game.globals().VoyageState.StartVoyageWithReceipt(state, request.destinationId, request.sequence)
    assert controller._T.pendingVoyageStart is False
    assert controller.messageText.Text == "存檔尚未確認，這趟先不能出航。"

    # 已經 sailing 的狀態不能冒充本次新啟航；server receipt 仍回拒絕。
    voyage = state.voyageByPlayer["player-1"]
    voyage.status = "sailing"
    voyage.voyageSequence = 5
    voyage.originId = "forest"
    voyage.destinationId = "sky"
    voyage.route = lua_game.table_from({"destinationId": "sky"})
    state.testReason = "現在已經在航行中囉！"
    begin(controller)
    request = state.requests[3]
    lua_game.globals().VoyageState.StartVoyageWithReceipt(state, request.destinationId, request.sequence)
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is True
    assert controller.messageText.Text == "現在已經在航行中囉！"

    # 內部拋錯時回絕並清除重入鎖，不覆寫既有航程狀態。
    voyage.status = "arrived"
    voyage.voyageSequence = 5
    state.testThrow = True
    begin(controller)
    request = state.requests[4]
    lua_game.globals().VoyageState.StartVoyageWithReceipt(state, request.destinationId, request.sequence)
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is True
    assert controller.messageText.Text == "出航處理發生錯誤，沒有完成本次出航。"
    assert voyage.status == "arrived"
    assert voyage.voyageSequence == 5
    assert state._T.departureReceiptPending["player-1"] is None

    # 從非 sailing 狀態啟航，並且 sequence 與 destination 都改變時才回成功。
    state.testThrow = False
    state.testAccept = True
    begin(controller)
    request = state.requests[5]
    lua_game.globals().VoyageState.StartVoyageWithReceipt(state, request.destinationId, request.sequence)
    assert controller._T.pendingVoyageStart is False
    assert controller.worldMapModal.Enable is False
    assert controller.messageText.Text == "離港啟程！開始航行！"


def test_departure_result_uses_targeted_client_rpc_slot(lua_game: LuaRuntime) -> None:
    source = VOYAGE_STATE.read_text(encoding="utf-8")
    receiver_args, _ = _extract_method(source, "ReceiveDepartureResult")
    _, server_body = _extract_method(source, "StartVoyageWithReceipt")
    targeted_calls = [
        line.strip()
        for line in server_body.splitlines()
        if "self:ReceiveDepartureResult(" in line
    ]

    assert _method_exec_space(source, "ReceiveDepartureResult") == "Client"
    assert receiver_args == ["requestSequence", "accepted", "reason"]
    assert len(targeted_calls) == 3
    assert all(call.endswith(", playerId)") for call in targeted_calls)

    controller = _new_controller(lua_game)
    lua_game.globals()._GreatVoyageAdventureController = controller
    lua_game.globals().Controller.BeginVoyage(controller)
    lua_game.globals().VoyageState.ReceiveDepartureResult(
        lua_game.table_from({}), 1, False, "存檔尚未確認，這趟先不能出航。"
    )
    assert controller._T.pendingVoyageStart is False
    assert controller.messageText.Text == "存檔尚未確認，這趟先不能出航。"


def test_production_abandon_restoration_keeps_feedback_revisions_monotonic(lua_game: LuaRuntime) -> None:
    voyage = lua_game.table_from({"voyageByPlayer": lua_game.table(), "_T": lua_game.table()})
    voyage.AbandonVoyage = lua_game.globals().VoyageState.AbandonVoyage
    voyage.GetOrCreateState = lua_game.eval(
        "function(self, playerId) self.voyageByPlayer[playerId] = self.restoredState; return self.restoredState end"
    )
    voyage.MovePlayerToPort = lua_game.eval(
        "function(self, playerId, portId) self.movedPlayerId = playerId; self.movedPortId = portId end"
    )
    voyage.PublishSnapshot = lua_game.eval(
        "function(self, playerId, state) self.publishedShipRevision = state.shipRevision; self.publishedEconomyRevision = state.economyRevision end"
    )

    # 舊 runtime revision 較大時，回到 durable profile 不得讓已發布 revision 倒退。
    old_state = lua_game.table_from(
        {
            "status": "sailing",
            "shipRevision": 73,
            "economyRevision": 91,
            "raidEnemies": lua_game.table(),
            "lastReason": "離開甲板了，航程先取消囉！",
        }
    )
    restored = lua_game.table_from(
        {
            "shipRevision": 2,
            "economyRevision": 4,
            "safePortId": "forest",
            "raidEnemies": lua_game.table(),
        }
    )
    voyage.voyageByPlayer["player-1"] = old_state
    voyage.restoredState = restored
    lua_game.globals()._GreatVoyageVoyageState = voyage

    lua_game.globals().VoyageState.AbandonVoyage(voyage, "player-1", old_state, False)

    rehydrated = voyage.voyageByPlayer["player-1"]
    assert rehydrated is not None
    assert rehydrated.shipRevision == 73
    assert rehydrated.economyRevision == 91
    assert voyage.publishedShipRevision == 73
    assert voyage.publishedEconomyRevision == 91
    assert voyage.movedPlayerId == "player-1"
    assert voyage.movedPortId == "forest"

    # 舊值較小時保留重建狀態較大的 revision，行為等同 max(new, old)。
    old_state.shipRevision = 5
    old_state.economyRevision = 7
    restored.shipRevision = 19
    restored.economyRevision = 23
    voyage.voyageByPlayer["player-1"] = old_state
    lua_game.globals().VoyageState.AbandonVoyage(voyage, "player-1", old_state, False)

    assert restored.shipRevision == 19
    assert restored.economyRevision == 23
    assert voyage.publishedShipRevision == 19
    assert voyage.publishedEconomyRevision == 23


def test_sell_upgrade_card_uses_default_quantity_without_phase0_prototype(lua_game: LuaRuntime) -> None:
    controller = _new_controller(lua_game)
    controller.shopTab = "cards"
    controller.shopSelectedIndex = 1
    controller.qaEntries = lua_game.table_from([lua_game.table_from({"id": "card-1"})])
    controller.GetShopEntries = lua_game.eval("function(self) return self.qaEntries end")
    controller.RefreshShop = lua_game.eval("function(self) self.refreshed = true end")

    state = lua_game.globals()._GreatVoyageVoyageState
    state.saleCalls = lua_game.table()
    state.SellUpgradeCard = lua_game.eval(
        "function(self, cardId, quantity) table.insert(self.saleCalls, { cardId = cardId, quantity = quantity }) end"
    )
    lua_game.globals()._Phase0VoyagePrototype = None

    lua_game.globals().Controller.SellGood(controller)

    assert len(state.saleCalls) == 1
    assert state.saleCalls[1].cardId == "card-1"
    assert state.saleCalls[1].quantity == 1
    assert controller.shopStatusMessage == "改裝卡賣出請求已送出！"

    lua_game.globals()._Phase0VoyagePrototype = lua_game.table_from({"tradeQuantity": 3})
    lua_game.globals().Controller.SellGood(controller)

    assert len(state.saleCalls) == 2
    assert state.saleCalls[2].cardId == "card-1"
    assert state.saleCalls[2].quantity == 3
