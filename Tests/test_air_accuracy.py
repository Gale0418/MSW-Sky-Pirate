"""Server-side aerial cannon accuracy curves and hit/miss resolution."""
import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
DATA = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageData.mlua"
ENCOUNTER = ROOT / "RootDesk/MyDesk/Combat/GreatVoyageEncounterData.mlua"


def bind(lua, target, path, names):
    source = path.read_text(encoding="utf-8")
    for name in names:
        match = re.search(
            r"\tmethod\s+[^\n]+\s+" + name + r"\(([^\n]*)\)\s*\n([\s\S]*?)\n\tend",
            source,
        )
        if not match:
            raise AssertionError(name)
        params = [p.strip().split()[-1] for p in match[1].split(",") if p.strip()]
        lua.execute(
            f"{target}.{name}=function(self,{','.join(params)})\n{match[2]}\nend".replace(
                "self,)", "self)"
            )
        )


def runtime(rolls=0):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        log=function(...) end
        log_warning=function(...) end
        _UtilLogic={
            ServerElapsedSeconds=0,
            rolls={},
            rollCount=0,
            RandomDouble=function(self)
                self.rollCount=self.rollCount+1
                return self.rolls[self.rollCount] or 0
            end
        }
        _GreatVoyageEncounterData={_T={}}
        _GreatVoyageVoyageData={_T={}}
        Voyage={_T={}}
        Data=_GreatVoyageVoyageData
        Encounter=_GreatVoyageEncounterData
        _UserService={GetUserEntityByUserId=function() return nil end}
    """)
    roll_values = rolls if isinstance(rolls, (list, tuple)) else [rolls]
    lua.globals()._UtilLogic["rolls"] = lua.table_from(roll_values)
    bind(lua, "Encounter", ENCOUNTER, ["GetMonsterHitChance", "GetPlayerHitChance"])
    bind(lua, "Voyage", STATE, [
        "RefreshBattleRoster", "ClaimMonsterBounty", "FinalizeAirBattle",
        "AdvanceAirBattle", "BeginAirBattle", "CalculateShipUpgrades",
        "ApplyShipUpgrades", "PublishAirBattleSnapshot",
    ])
    bind(lua, "Data", DATA, ["GetShipUpgradeCards", "GetShipUpgradeCardById"])
    lua.execute("""
        Data.GetEconomyScale=function() return 1 end
        Data.GetUpgradeCardArtRuid=function() return "" end
        Data.GetShipById=function(self,id)
            return {id=id,tier=0,maxHull=100,maxShield=0,maxArmor=0,
                cargoCapacity=5,cannonMultiplier=1,durationMultiplier=1}
        end
        Encounter.GetCombatProfile=function(self,tier)
            return {cannonDamage=tier == 5 and 4000 or 20,
                cannonInterval=tier == 5 and 0.6 or 1}
        end
        Encounter.DrawWave=function(self,prepared) return prepared.definitions end
        Voyage.PublishSnapshot=function() end
        Voyage.ReceiveAirWaveSnapshot=function(self,battleId,active)
            self.lastAirWave=active
        end
    """)
    return lua, lua.globals().Voyage


def begin_battle(lua, voyage, monster_id="mob/3230300.img", tier=0):
    definitions = lua.table_from([lua.table_from({
        "packId": monster_id, "name": "目標", "maxHp": 12,
        "attackDamage": 1, "attackIntervalSeconds": 100,
        "bounty": 150, "animationRuid": "anim",
    })])
    segment = lua.table_from({"shortName": "測試空域"})
    prepared = lua.table_from({"screenLimit": 1, "definitions": definitions})
    state = lua.table_from({
        "status": "sailing", "ship": lua.table_from({
            "id": "ship_test", "tier": tier, "cannonMultiplier": 1,
            "hull": 100, "maxHull": 100,
            "stats": lua.table_from({"accuracyBonus": 0}),
        }),
        "preparedEncounter": prepared, "voyageSequence": 1,
    })
    voyage.BeginAirBattle(voyage, "captain", state, segment, 1, 0)
    return state, state.airBattle


class AirAccuracyTests(unittest.TestCase):
    def test_monster_classes_and_clamped_monotonic_player_curve(self):
        lua, _ = runtime()
        data = lua.globals().Encounter
        chance = data.GetMonsterHitChance
        player_chance = data.GetPlayerHitChance

        self.assertAlmostEqual(chance(data, "mob/3230300.img"), 0.82)  # 幼魔精靈
        self.assertAlmostEqual(chance(data, "mob/2300100.img"), 0.82)  # 蝙蝠
        self.assertAlmostEqual(chance(data, "mob/8140200.img"), 0.96)  # 冥鐘
        self.assertAlmostEqual(chance(data, "mob/8150300.img"), 0.96)  # 赤翼龍
        self.assertAlmostEqual(chance(data, "mob/0100130.img"), 0.92)  # 穆魯
        curve = [player_chance(data, tier, "mob/0100130.img", 0) for tier in range(6)]
        self.assertEqual(curve, sorted(curve))
        for actual, expected in zip(curve, [0.92, 0.94, 0.96, 0.98, 0.99, 0.99]):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(player_chance(data, -20, "unknown", -1), 0.75)
        self.assertEqual(player_chance(data, 50, "unknown", 2), 0.99)

    def test_stabilizer_card_and_upgrade_bonus(self):
        lua, voyage = runtime()
        data = lua.globals().Data
        stabilizer = data.GetShipUpgradeCardById(data, "stabilizer")
        self.assertTrue(stabilizer.available)
        self.assertEqual(stabilizer.accuracyBonus, 0.05)
        self.assertEqual(stabilizer.price, 100)
        self.assertEqual(stabilizer.sellPrice, 50)
        self.assertEqual(stabilizer.requirement, "")
        self.assertIn("99%", stabilizer.description)

        one = lua.table_from(["stabilizer", "", ""])
        three = lua.table_from(["stabilizer", "stabilizer", "stabilizer"])
        upgrades_one = voyage.CalculateShipUpgrades(voyage, "ship_test", one)
        upgrades_three = voyage.CalculateShipUpgrades(voyage, "ship_test", three)
        self.assertAlmostEqual(upgrades_one.stats.accuracyBonus, 0.05)
        self.assertAlmostEqual(upgrades_three.stats.accuracyBonus, 0.15)

    def test_formal_battle_hit_and_miss_each_roll_once_at_launch_and_land_after_06(self):
        for rolls, expected_hit, expected_damage in (([0, 0, 0.99], True, 18), ([0, 1, 0.99], True, 22), ([1], False, 0)):
            with self.subTest(expected_hit=expected_hit, expected_damage=expected_damage):
                lua, voyage = runtime(rolls)
                state, battle = begin_battle(lua, voyage)
                enemy = battle.enemies[1]
                self.assertAlmostEqual(enemy.hitChance, 0.82)

                voyage.AdvanceAirBattle(voyage, "captain", state, 1)
                self.assertEqual(lua.globals()._UtilLogic.rollCount, 3 if expected_hit else 1)
                self.assertEqual(battle.lastPlayerShotHit, expected_hit)
                self.assertAlmostEqual(battle.lastPlayerShotHitChance, 0.82)
                self.assertEqual(battle.lastPlayerShotDamage, expected_damage)
                self.assertFalse(battle.lastPlayerShotCritical)
                self.assertEqual(enemy.hp, 12)
                self.assertEqual(state.pendingBounty or 0, 0)
                self.assertAlmostEqual(battle.playerImpactAt, 1.6)

                voyage.AdvanceAirBattle(voyage, "captain", state, 1.59)
                self.assertEqual(enemy.hp, 12)
                self.assertEqual(lua.globals()._UtilLogic.rollCount, 3 if expected_hit else 1)

                voyage.AdvanceAirBattle(voyage, "captain", state, 1.6)
                self.assertEqual(lua.globals()._UtilLogic.rollCount, 3 if expected_hit else 1)
                if expected_hit:
                    self.assertEqual(enemy.hp, 0)
                    self.assertEqual(battle.kills, 1)
                    self.assertEqual(state.pendingBounty, 150)
                    self.assertEqual(battle.phase, "won")
                else:
                    self.assertEqual(enemy.hp, 12)
                    self.assertEqual(battle.kills, 0)
                    self.assertEqual(state.pendingBounty or 0, 0)
                    self.assertEqual(battle.phase, "active")

    def test_snapshot_carries_result_and_legacy_fixture_without_chance_is_guaranteed_hit(self):
        lua, voyage = runtime([1])
        state, battle = begin_battle(lua, voyage)
        voyage.AdvanceAirBattle(voyage, "captain", state, 1)
        voyage.PublishAirBattleSnapshot(voyage, "captain", state)
        shot = voyage.lastAirWave.playerShot
        self.assertFalse(shot.hit)
        self.assertAlmostEqual(shot.hitChance, 0.82)
        self.assertEqual(shot.targetUid, 1)
        self.assertEqual(shot.damage, 0)
        self.assertFalse(shot.critical)

        lua.globals()._UtilLogic["rollCount"] = 0
        state2 = lua.table_from({"status": "sailing", "ship": lua.table_from({
            "hull": 100, "maxHull": 100, "stats": lua.table_from({}),
        })})
        enemy = lua.table_from({
            "uid": 1, "id": "fixture", "name": "舊 fixture", "hp": 12, "maxHp": 12,
            "damage": 1, "interval": 100, "bounty": 20, "claimed": False, "active": True,
            "nextAttackAt": 100,
        })
        enemies = lua.table_from([enemy])
        legacy = lua.table_from({
            "phase": "active", "settled": False, "enemies": enemies, "kills": 0,
            "screenLimit": 1, "playerDamage": 1, "playerAttackIntervalSeconds": 1,
            "flightSeconds": 0.6, "nextPlayerAttackAt": 1, "playerShotSequence": 0,
            "enemyShotSequence": 0,
        })
        state2.airBattle = legacy
        voyage.RefreshBattleRoster(voyage, legacy, 0)
        voyage.AdvanceAirBattle(voyage, "captain", state2, 1)
        self.assertTrue(legacy.lastPlayerShotHit)
        self.assertEqual(legacy.lastPlayerShotHitChance, 1)
        self.assertEqual(legacy.lastPlayerShotDamage, 1)
        self.assertFalse(legacy.lastPlayerShotCritical)
        self.assertEqual(lua.globals()._UtilLogic.rollCount, 0)

    def test_critical_chance_can_be_zero_or_one_and_t5_critical_one_shots_small_monster(self):
        for chance, crit_roll, expected_critical, expected_damage in (
            (0, 0, False, 18),
            (1, 0.99, True, 27),
        ):
            with self.subTest(chance=chance):
                lua, voyage = runtime([0, 0, crit_roll])
                state, battle = begin_battle(lua, voyage)
                battle.critChance = chance
                voyage.AdvanceAirBattle(voyage, "captain", state, 1)
                self.assertEqual(battle.lastPlayerShotCritical, expected_critical)
                self.assertEqual(battle.lastPlayerShotDamage, expected_damage)
                self.assertEqual(lua.globals()._UtilLogic.rollCount, 3)

        lua, voyage = runtime([0, 0, 0.99])
        state, battle = begin_battle(lua, voyage, tier=5)
        self.assertEqual(battle.playerDamage, 4000)
        self.assertEqual(battle.critChance, 0.05)
        self.assertEqual(battle.critMultiplier, 1.5)
        battle.critChance = 1
        voyage.AdvanceAirBattle(voyage, "captain", state, 0.6)
        self.assertEqual(battle.lastPlayerShotDamage, 5400)
        self.assertTrue(battle.lastPlayerShotCritical)
        self.assertEqual(lua.globals()._UtilLogic.rollCount, 3)
        voyage.AdvanceAirBattle(voyage, "captain", state, 1.2)
        self.assertEqual(battle.kills, 1)
        self.assertEqual(state.pendingBounty, 150)
        self.assertEqual(battle.phase, "won")
        self.assertEqual(lua.globals()._UtilLogic.rollCount, 3)


if __name__ == "__main__":
    unittest.main()
