"""用 Lupa 驅動正式航程方法，驗證遭遇節奏與試算輸入。"""
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
            raise AssertionError(f"找不到正式 mLua 方法：{name}")
        params = [part.strip().split()[-1] for part in match[1].split(",") if part.strip()]
        lua.execute(f"{target}.{name}=function(self,{','.join(params)})\n{match[2]}\nend".replace("self,)", "self)"))


def cadence_runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        log=function(...) end
        log_warning=function(...) end
        senderUserId='captain'
        _UtilLogic={ServerElapsedSeconds=1.5}
        _UserService={GetUserEntityByUserId=function() return {CurrentMapName='map_airship_deck'} end}
        Voyage={_T={},voyageByPlayer={captain={}}}
        _GreatVoyageVoyageData={
            GetAirspaces=function() return {{id='victoria',fog=false},{id='sky',fog=false}} end,
            GetShipById=function() return {tier=1} end,
            GetCargoEncounterValue=function() return 0 end
        }
        _GreatVoyageEncounterData={Prepare=function(self,area,tier,cargo,temptation,stats,fog)
            table.insert(self.areas,area)
            return {chance=_FixtureChance}
        end, areas={}}
        _FixtureChance=0.36
        Voyage.GetOrCreateState=function() return _FixtureState end
        Voyage.PublishSnapshot=function() end
        Voyage.ClearLegacyEncounter=function() end
        Voyage.ApplyVoyageCardProgress=function() return true end
        Voyage.BeginAirBattle=function(self,playerId,state,segment,count,now)
            self.battleCalls=(self.battleCalls or 0)+1
            self.battleArea=segment.airspaceId
        end
        Voyage.PersistSettledVoyage=function() return true end
        Voyage.MovePlayerToPort=function() end
        function make_state()
            return {status='sailing',route={distance=250},segments={
                {airspaceId='victoria',length=100,shortName='維多利亞'},
                {airspaceId='open_sea',length=100,shortName='開放海域'},
                {airspaceId='sky',length=50,shortName='天空之城'},
            }, ship={id='ship',tier=1,stats={}}, cargo={lots={}}, money=999999999,
                destinationId='port',elapsedSailingSeconds=0,voyageDurationSeconds=1,lastAdvanceAt=0,
                distanceTravelled=0,budgetRemaining=250,lastEncounterDistance=0,nextEncounterDistance=100,
                encounterCount=0,raidRemaining=0,raidEnemies={}}
        end
        function set_rolls(...)
            local values={...}
            math.randomCalls=0
            math.random=function()
                math.randomCalls=math.randomCalls+1
                return values[math.randomCalls] or 0.9
            end
        end
    """)
    bind(lua, "Voyage", STATE, ["GetSegmentForDistance", "GetSegmentEncounterChance", "AdvanceVoyage"])
    return lua, lua.globals().Voyage


class EncounterCadenceTests(unittest.TestCase):
    def test_checkpoints_accumulate_across_airspaces_without_reset(self):
        lua, voyage = cadence_runtime()
        lua.globals()._FixtureState = lua.globals().make_state()
        lua.globals().set_rolls(0.9, 0.9, 0.9)
        voyage.AdvanceVoyage(voyage, 1)
        areas = lua.globals()._GreatVoyageEncounterData.areas
        self.assertEqual([areas[i] for i in range(1, len(areas) + 1)], ["victoria", "open_sea", "sky"])
        state = lua.globals()._FixtureState
        self.assertEqual(state.lastEncounterDistance, 250)
        self.assertEqual(state.nextEncounterDistance, 350)
        self.assertEqual(lua.eval("math.randomCalls"), 3)

    def test_short_tail_uses_partial_hazard_and_each_checkpoint_rolls_once(self):
        lua, voyage = cadence_runtime()
        lua.globals()._FixtureState = lua.globals().make_state()
        # 完整 100 距離的機率為 0.36；最後 50 距離的門檻較低，因此 0.25 不應觸發。
        lua.globals().set_rolls(0.9, 0.9, 0.25)
        voyage.AdvanceVoyage(voyage, 1)
        self.assertEqual(lua.eval("math.randomCalls"), 3)
        self.assertEqual(lua.eval("Voyage.battleCalls or 0"), 0)

    def test_confirmed_event_rolls_once_and_does_not_reroll(self):
        lua, voyage = cadence_runtime()
        lua.globals()._FixtureState = lua.globals().make_state()
        lua.globals().set_rolls(0.1, 0.1, 0.1)
        voyage.AdvanceVoyage(voyage, 1)
        self.assertEqual(lua.eval("math.randomCalls"), 1)
        self.assertEqual(lua.eval("Voyage.battleCalls"), 1)
        self.assertEqual(lua.eval("Voyage.battleArea"), "victoria")

    def test_cargo_snapshot_and_card_slots_are_passed_once_without_cash(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute("""
            Voyage={_T={}}
            Data={_T={}}
            _GreatVoyageVoyageData=Data
            Data.GetGoodById=function(self,id) return {price=100} end
            Data.GetShipById=function(self,id) return {cannonMultiplier=1,durationMultiplier=1,cargoCapacity=10,maxHull=100,maxArmor=40,maxShield=20} end
            Data.GetShipUpgradeCardById=function(self,id)
                local cards={
                    lure={encounterMultiplier=0.10},
                    fog={fogEncounterMultiplier=0.20},
                    wildlife={monsterEncounterMultiplier=0.30},
                }
                return cards[id]
            end
            Data.GetAirspaces=function(self) return {{id='victoria',fog=false}} end
            _GreatVoyageEncounterData={Prepare=function(self,area,tier,cargo,temptation,stats,fog)
                self.calls=(self.calls or 0)+1
                self.area,self.tier,self.cargo,self.temptation,self.stats,self.fog=area,tier,cargo,temptation,stats,fog
                return {chance=0.4}
            end}
        """)
        bind(lua, "Voyage", STATE, ["CalculateShipUpgrades", "GetSegmentEncounterChance"])
        bind(lua, "Data", DATA, ["GetCargoEncounterValue"])
        voyage = lua.globals().Voyage
        upgrades = voyage.CalculateShipUpgrades(voyage, "ship", lua.table_from({1: "lure", 2: "fog", 3: "wildlife"}))
        stats = upgrades.stats
        self.assertAlmostEqual(stats.encounterMultiplier, 0.10)
        self.assertAlmostEqual(stats.fogEncounterMultiplier, 0.20)
        self.assertAlmostEqual(stats.monsterEncounterMultiplier, 0.30)
        state = lua.table_from({
            "ship": lua.table_from({"id": "ship", "tier": 1, "stats": stats}),
            "cargo": lua.eval("{lots={{id='good',quantity=2,buyPrice=999999999}}}"),
            "money": 999999999,
        })
        chance = voyage.GetSegmentEncounterChance(voyage, state, lua.table_from({"airspaceId": "victoria"}))
        self.assertAlmostEqual(chance, 0.4)
        encounter = lua.globals()._GreatVoyageEncounterData
        self.assertEqual(encounter.calls, 1)
        self.assertEqual(encounter.cargo, 200)
        self.assertEqual(encounter.temptation, 0)
        self.assertAlmostEqual(encounter.stats.encounterMultiplier, 0.10)
        self.assertAlmostEqual(encounter.stats.fogEncounterMultiplier, 0.20)
        self.assertAlmostEqual(encounter.stats.monsterEncounterMultiplier, 0.30)


if __name__ == "__main__":
    unittest.main()
