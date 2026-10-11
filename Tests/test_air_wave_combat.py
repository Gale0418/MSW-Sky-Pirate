"""直接執行正式 mLua 方法：隊伍、賞金、防重、沉船與滿錢包。"""
import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
DATA = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageData.mlua"


def bind(lua, target, path, names):
    source = path.read_text(encoding="utf-8")
    for name in names:
        match = re.search(r"\tmethod\s+[^\n]+\s+" + name + r"\(([^\n]*)\)\s*\n([\s\S]*?)\n\tend", source)
        if not match:
            raise AssertionError(name)
        params = [p.strip().split()[-1] for p in match[1].split(",") if p.strip()]
        lua.execute(f"{target}.{name}=function(self,{','.join(params)})\n{match[2]}\nend".replace("self,)", "self)"))


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        log=function(...) end
        log_warning=function(...) end
        _UtilLogic={ServerElapsedSeconds=0}
        _UserService={GetUserEntityByUserId=function() return nil end}
        Data={_T={}}
        Voyage={_T={}}
    """)
    bind(lua, "Voyage", STATE, ["RefreshBattleRoster", "ClaimMonsterBounty", "SettleMonsterBounties", "AdvanceAirBattle", "FinalizeAirBattle", "ApplyShipDamage"])
    bind(lua, "Data", DATA, ["GetCargoEncounterValue", "GetGoodById"])
    lua.execute("""
        _GreatVoyageCommodityCatalog={GetById=function(self,id) return {price=2500,verified=true} end}
        _GreatVoyageVoyageData={CopyCargo=function() return {lots={}} end}
        Voyage.PublishSnapshot=function() end
        Voyage.PersistSettledVoyage=function(self,id,state,port) self:SettleMonsterBounties(state); self.saved=true; return true end
        function create(hull,damage,count,limit)
            local state={status='sailing',originId='forest',money=1000,pendingBounty=0,bountyCredit=0,economyRevision=0,shipRevision=0,
                ship={hull=hull,maxHull=hull,shield=0,maxShield=0,armor=0,maxArmor=0,stats={}}}
            local battle={id='fixture',phase='active',settled=false,enemies={},kills=0,bounty=0,screenLimit=limit,
                playerDamage=damage,playerAttackIntervalSeconds=1,flightSeconds=0.6,nextPlayerAttackAt=1,playerShotSequence=0,enemyShotSequence=0}
            for i=1,count do table.insert(battle.enemies,{uid=i,id='species'..i,name='怪'..i,hp=12,maxHp=12,damage=2,interval=2,bounty=i*100,claimed=false,active=false}) end
            state.airBattle=battle
            Voyage:RefreshBattleRoster(battle,0)
            return state,battle
        end
    """)
    return lua, lua.globals().Voyage


class AirWaveCombatTests(unittest.TestCase):
    def test_wave_snapshot_rejects_missing_component_and_other_players(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("""
            Voyage={}
            _UserService={}
            _UtilLogic={ElapsedSeconds=0}
            isvalid=function(value) return value ~= nil end
            _GreatVoyageAdventureController={_T={},RefreshAirBattleDisplay=function(self) self.refreshed=true end}
        """)
        bind(lua, "Voyage", STATE, ["ReceiveAirWaveSnapshot"])
        voyage = lua.globals().Voyage
        receive = voyage.ReceiveAirWaveSnapshot
        for player in (None, lua.table(), lua.table(PlayerComponent=lua.table(UserId="other"))):
            lua.globals()._UserService.LocalPlayer = player
            receive(voyage, "wave", lua.table(), 1, 1, 0, 100, 0, "captain")
            self.assertIsNone(lua.globals()._GreatVoyageAdventureController._T.airWave)
        lua.globals()._UserService.LocalPlayer = lua.table(PlayerComponent=lua.table(UserId="captain"))
        receive(voyage, "wave", lua.table(), 1, 1, 0, 100, 0, "captain")
        self.assertEqual(lua.globals()._GreatVoyageAdventureController._T.airWave.id, "wave")
        self.assertTrue(lua.globals()._GreatVoyageAdventureController.refreshed)

    def test_team_reinforcements_and_individual_bounties(self):
        lua, voyage = runtime()
        state, battle = lua.globals().create(1000, 4000, 5, 2)
        self.assertEqual(sum(e.active for _, e in battle.enemies.items()), 2)
        for now in range(1, 8):
            voyage.AdvanceAirBattle(voyage, "captain", state, now)
        self.assertEqual(battle.phase, "won")
        self.assertEqual(battle.kills, 5)
        self.assertEqual(state.pendingBounty, 1500)
        self.assertEqual(state.money, 1000)
        self.assertFalse(voyage.ClaimMonsterBounty(voyage, state, battle, battle.enemies[1]))
        voyage.SettleMonsterBounties(voyage, state)
        self.assertEqual(state.money, 2500)
        voyage.SettleMonsterBounties(voyage, state)
        self.assertEqual(state.money, 2500)

    def test_every_active_monster_can_attack(self):
        lua, voyage = runtime()
        state, battle = lua.globals().create(1000, 1, 3, 3)
        voyage.AdvanceAirBattle(voyage, "captain", state, 3)
        self.assertEqual(battle.enemyShotSequence, 3)
        self.assertEqual(state.ship.hull, 994)
        self.assertEqual(state.pendingBounty, 0)

    def test_no_timeout_win_and_no_live_enemy_reward(self):
        lua, voyage = runtime()
        state, battle = lua.globals().create(100000, 1, 1, 1)
        battle.enemies[1].hp = 100000
        battle.enemies[1].maxHp = 100000
        for now in range(1, 61):
            voyage.AdvanceAirBattle(voyage, "captain", state, now)
        self.assertEqual(battle.phase, "active")
        self.assertEqual(state.pendingBounty, 0)
        voyage.FinalizeAirBattle(voyage, "captain", state, battle, "won", 60)
        self.assertEqual(battle.phase, "active")

    def test_sink_keeps_cash_and_earned_bounty_loses_cargo(self):
        lua, voyage = runtime()
        state, battle = lua.globals().create(1, 12, 2, 2)
        battle.enemies[2].hp = 120
        battle.enemies[2].maxHp = 120
        state.cargo = lua.table_from({"quantity": 8})
        voyage.AdvanceAirBattle(voyage, "captain", state, 3)
        self.assertEqual(battle.phase, "sunk")
        self.assertEqual(battle.kills, 1)
        self.assertEqual(state.money, 1100)
        self.assertEqual(len(state.cargo.lots), 0)

    def test_wallet_overflow_is_credit_and_retries_do_not_duplicate(self):
        lua, voyage = runtime()
        state, _ = lua.globals().create(1000, 12, 1, 1)
        state.money = 2147483640
        state.pendingBounty = 500
        voyage.SettleMonsterBounties(voyage, state)
        self.assertEqual(state.money, 2147483647)
        self.assertEqual(state.bountyCredit, 493)
        voyage.SettleMonsterBounties(voyage, state)
        self.assertEqual(state.bountyCredit, 493)
        state.money -= 1000
        voyage.SettleMonsterBounties(voyage, state)
        self.assertEqual(state.money, 2147483140)
        self.assertEqual(state.bountyCredit, 0)

    def test_cargo_intrinsic_price_not_purchase_cost(self):
        lua, _ = runtime()
        cargo = lua.eval("{lots={{id='a',quantity=2,buyPrice=999999}}}")
        value = lua.globals().Data.GetCargoEncounterValue(lua.globals().Data, cargo)
        self.assertEqual(value, 5000)

    def test_bounty_credit_is_backwards_compatible_and_validated(self):
        from test_save_v1_lua import base_profile, make_runtime, lua_value, SHIPS, CARDS, GOODS

        lua, store = make_runtime()
        profile = base_profile()
        args = [lua_value(v, lua) for v in [SHIPS, CARDS, GOODS]]
        self.assertTrue(store.ValidateProfile(store, lua_value(profile, lua), *args))
        for credit in [0, 493, 2147483648, 9007199254740991]:
            profile["core"]["bountyCredit"] = credit
            self.assertTrue(store.ValidateProfile(store, lua_value(profile, lua), *args))
        for credit in [-1, 0.5, float("inf"), float("nan"), 9007199254740992, "493"]:
            profile["core"]["bountyCredit"] = credit
            self.assertFalse(store.ValidateProfile(store, lua_value(profile, lua), *args))

    def test_t5_repair_curve_and_starter_legacy_quotes(self):
        lua, _ = runtime()
        bind(lua, "Data", DATA, ["GetRepairQuote", "GetEconomyScale"])
        lua.execute("""
            Data.GetShipById=function() return nil end
            Data.GetShipProgression=function() return {[6]={fullRepair=50000000}} end
        """)
        quote = lua.globals().Data.GetRepairQuote
        data = lua.globals().Data
        t5 = lua.eval("{id='future_flagship',tier=5,maxHull=30000,hull=15000,maxShield=6000,shield=3000,maxArmor=12000,armor=6000,stats={repairCostMultiplier=1}}")
        self.assertEqual(quote(data, t5), 25000000)
        t5.hull = t5.shield = t5.armor = 0
        self.assertEqual(quote(data, t5), 50000000)
        t5.id = "small_sampan"
        self.assertEqual(quote(data, t5), 0)


if __name__ == "__main__":
    unittest.main()
