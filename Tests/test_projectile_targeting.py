"""混編空戰投射物與敵人視覺回歸：以 Lupa 執行正式 mLua 方法。"""
import re
import unittest
from pathlib import Path

from lupa import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
VISUAL = ROOT / "RootDesk/MyDesk/ShipVisual/GVShipVisualClient.mlua"
STATE = ROOT / "RootDesk/MyDesk/GreatVoyageVoyageState.mlua"
ENCOUNTER_DATA = ROOT / "RootDesk/MyDesk/Combat/GreatVoyageEncounterData.mlua"


def bind(lua, target, path, names):
    source = path.read_text(encoding="utf-8")
    for name in names:
        match = re.search(
            r"\tmethod\s+[^\n]+\s+" + name + r"\(([^\n]*)\)\s*\n([\s\S]*?)\n\tend",
            source,
        )
        if not match:
            raise AssertionError(f"正式 mLua 找不到方法：{name}")
        params = [part.strip().split()[-1] for part in match[1].split(",") if part.strip()]
        args = ",".join(params)
        lua.execute(f"{target}.{name}=function(self{',' if args else ''}{args})\n{match[2]}\nend")


METHODS = [
    "GetBattleRoamPosition", "GetBattleTargetCenter", "GetBattleEnemyCenter", "GetBattleMissEndPosition", "GetBattleMissTextPosition",
    "GetBattlePlayerShot", "UpdateBattleVisuals", "UpdateBattleWaveViews",
    "BattleWorldToLocal", "GetProjectileRotation", "CompletePlayerShotVisual",
    "ReleaseBattleVisuals", "ShowBattleDamageNumber", "UpdateBattleDamageNumbers", "ReleaseLocalViews",
    "PreloadBattleMonsterHitAnimations", "StartBattleHitPose", "UpdateBattleHitPoses",
]


def visual_runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        log=function(...) end
        log_warning=function(...) end
        Vector2=function(x,y) return {x=x or 0,y=y or 0} end
        Vector3=function(x,y,z) return {x=x or 0,y=y or 0,z=z or 0} end
        Color=function(r,g,b,a) return {r=r,g=g,b=b,a=a} end
        isvalid=function(value) return value ~= nil and value.valid ~= false end
        function entity(position)
            local transform={Position=position or Vector3(0,0,0),Rotation=Vector3(0,0,0),Scale=Vector3(1,1,1)}
            setmetatable(transform,{__index=function(self,key) if key=="WorldPosition" then return rawget(self,"ActualWorldPosition") or self.Position end end})
            local rendererValues={Enable=false,SpriteRUIDWrites=0}
            local renderer=setmetatable({},{
                __index=function(self,key) return rendererValues[key] end,
                __newindex=function(self,key,value)
                    if key=="SpriteRUID" then rendererValues.SpriteRUIDWrites=rendererValues.SpriteRUIDWrites+1 end
                    rendererValues[key]=value
                end})
            local e={valid=true,destroyCount=0,TransformComponent=transform,SpriteRendererComponent=renderer}
            function e:Destroy() self.destroyCount=self.destroyCount+1; self.valid=false end
            function e:AddComponent(name) if name=="DamageSkinComponent" then self.DamageSkinComponent={} end end
            return e
        end
        map={Name="map_airship_deck",TransformComponent={
            ToLocalPoint=function(self,p) return Vector3(p.x,p.y,p.z) end,
            ToWorldPoint=function(self,p) return Vector3(p.x,p.y,p.z) end}}
        local player={valid=true,CurrentMap=map}
        _UserService={LocalPlayer=player}
        _GreatVoyageAdventureController={_T={airWave=nil},clientAirBattle=nil}
        _GreatVoyageEncounterData={definitions={
            target={hitAnimationRuid="hit1-target"},
            primary={hitAnimationRuid="hit1-primary"},
            other={hitAnimationRuid="hit1-other"}}}
        _GreatVoyageEncounterData.GetMonsterById=function(self,id) return self.definitions[id] end
        _GreatVoyageEncounterData.GetAllMonsters=function(self)
            return {{enabled=true,packId="target"},{enabled=true,packId="primary"},{enabled=false,packId="other"}}
        end
        _UILogic={ScreenWidth=1920,ScreenHeight=1080,
            ScreenToWorldPosition=function(self,p) return Vector3(p.x/100,p.y/100,0) end}
        _UtilLogic={ElapsedSeconds=0}
        _ResourceService={calls={},PreloadAsync=function(self,ids,callback)
            table.insert(self.calls,{ids=ids,callback=callback})
        end}
        PreloadResultStatus={Success="Success",Failure="Failure"}
        _SpawnService={spawned={},SpawnByModelId=function(self,id,name,pos,parent)
            local e=entity(pos); e.Name=name; table.insert(self.spawned,e); return e
        end}
        _EffectService={PlayEffect=function() return 0 end,RemoveEffect=function() end}
        DamageSkinTweenType={Default="TweenDefault"}
        DamageSkinTextType={Miss="MissEnum"}
        LitMode={Default="LitDefault"}
        _DamageSkinService={calls={},textCalls={}}
        _DamageSkinService.Play=function(self,...) table.insert(self.calls,{...}) end
        _DamageSkinService.PlayTextDamage=function(self,...) table.insert(self.textCalls,{...}) end
        TestVisual={
            _T={},Entity={CurrentMap=map,TransformComponent={WorldPosition=Vector3(0,0,0)}},
            overlayModelId="overlay",impactAnimationRuid="impact",cannonAnimationRuid="cannon",
            cannonSpriteFacingOffset=180,enemyShotSpriteFacingOffset=180,
            shotFlightSeconds=1,lastPlayerShotSequence=0,lastEnemyShotSequence=0,
            shotElapsed=1,enemyShotElapsed=1,battleVisualElapsed=0,enemyHitFlashRemaining=0,
            appliedBattleId="",lastEnemyHp=-1}
        TestVisual.GetBattleMuzzlePosition=function(self) return self._Test.muzzle end
        TestVisual.GetBattleEnemyPosition=function(self) return Vector3(0,0,0) end
        TestVisual.GetBattleShipPosition=function(self) return Vector3(-3,-1,0) end
        TestVisual.GetMapSortingLayer=function(self) return "MapLayer6" end
        TestVisual.LoadBattleEnemyCenter=function(self,ruid)
            if self._T.enemyCenterCache == nil then self._T.enemyCenterCache={} end
            if self._T.enemyCenterReady == nil then self._T.enemyCenterReady={} end
            self._T.enemyCenterCache[ruid]=self._T.enemyCenterCache[ruid] or Vector2(0,0)
            self._T.enemyCenterReady[ruid]=true
        end
        TestVisual.ShowBattleImpact=function(self,position)
            if self._T.impacts == nil then self._T.impacts={} end
            table.insert(self._T.impacts,Vector3(position.x,position.y,position.z))
        end
    """)
    bind(lua, "TestVisual", VISUAL, METHODS)
    bind(lua, "_GreatVoyageEncounterData", ENCOUNTER_DATA, ["GetMonsterHitAnimationRuid"])
    return lua, lua.globals().TestVisual


def shot_fixture(lua, visual, *, target_uid=2, target_ruid="ruid-target", elapsed=0, flight=1, with_meta=True, muzzle=(1, 2)):
    lua.globals()._UtilLogic.ElapsedSeconds = 10
    visual._Test = lua.table(muzzle=lua.eval(f"Vector3({muzzle[0]},{muzzle[1]},0)"))
    battle, wave = lua.execute("""
        local battle={id="mixed",phase="active",enemyId="primary",enemyHp=10,
            enemyShotSequence=0,playerShotSequence=1,flightSeconds=1}
        local enemies={
            {uid=1,id="primary",animationRuid="ruid-primary",hp=10},
            {uid=2,id="target",animationRuid="ruid-target",hp=10},
            {uid=3,id="other",animationRuid="ruid-other",hp=10}}
        local wave={id="mixed",receivedAt=10,enemies=enemies}
        _GreatVoyageAdventureController.clientAirBattle=battle
        _GreatVoyageAdventureController._T.airWave=wave
        return battle,wave
    """)
    if with_meta:
        wave.enemies.playerShot = lua.table(
            sequence=1, targetUid=target_uid, targetId="target", animationRuid=target_ruid,
            elapsed=elapsed, flightSeconds=flight,
        )
    return battle, wave


def assert_vec(test, actual, expected, places=7):
    test.assertAlmostEqual(actual.x, expected.x, places=places)
    test.assertAlmostEqual(actual.y, expected.y, places=places)


class ProjectileTargetingTests(unittest.TestCase):
    def test_uid_roaming_is_independent_and_removal_does_not_reposition_survivors(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual)
        visual.UpdateBattleWaveViews(visual, battle, lua.globals().map)
        beta_before = visual._T.waveViews[3].TransformComponent.Position
        visual.battleVisualElapsed = 0.7
        visual.UpdateBattleWaveViews(visual, battle, lua.globals().map)
        beta_moved = visual._T.waveViews[3].TransformComponent.Position
        alpha_start = visual._T.waveViews[2].TransformComponent.Position
        wave.enemies = lua.table_from([
            lua.table(uid=1,id="primary",animationRuid="ruid-primary",hp=10),
            lua.table(uid=3,id="other",animationRuid="ruid-other",hp=10),
        ])
        visual.UpdateBattleWaveViews(visual, battle, lua.globals().map)
        beta_after = visual._T.waveViews[3].TransformComponent.Position
        assert_vec(self, beta_after, beta_moved)
        self.assertNotAlmostEqual(beta_moved.x, beta_before.x, places=6)
        self.assertNotAlmostEqual(alpha_start.x, beta_moved.x, places=5)

    def test_shot_keeps_launch_endpoint_rotation_and_straight_path_after_world_changes(self):
        for offset in ((0.2, -0.1), (-0.35, 0.25)):
            for muzzle in ((1, 2), (-2.5, 3.75)):
                with self.subTest(center_offset=offset, muzzle=muzzle):
                    lua, visual = visual_runtime()
                    battle, wave = shot_fixture(lua, visual, elapsed=0.1, flight=1, muzzle=muzzle)
                    visual._T.enemyCenterCache = lua.table_from({
                        "ruid-target": lua.eval(f"Vector2({offset[0]},{offset[1]})"),
                        "ruid-primary": lua.eval("Vector2(0.1,0.4)"),
                    })
                    visual._T.enemyCenterReady = lua.table_from({"ruid-target": True, "ruid-primary": True})
                    visual.UpdateBattleVisuals(visual, 0.05)
                    start = visual._T.playerShotStartPosition
                    endpoint = visual._T.playerShotEndPosition
                    rotation = visual._T.playerShotRotation
                    impact_time = visual._T.playerShotImpactTime
                    target_uid = visual._T.playerShotTargetUid
                    expected = visual.GetBattleTargetCenter(visual, target_uid, "ruid-target", impact_time)
                    assert_vec(self, start, lua.eval(f"Vector3({muzzle[0]},{muzzle[1]},0)"))
                    assert_vec(self, endpoint, expected)
                    # 模擬主目標、相機、中心快取及炮口在炮彈途中改變。
                    battle.enemyId = "other"
                    wave.enemies.playerShot = lua.table(sequence=1,targetUid=2,animationRuid="ruid-target",elapsed=0.3,flightSeconds=1)
                    visual._Test.muzzle = lua.eval("Vector3(99,-50,0)")
                    lua.globals()._UILogic.ScreenWidth = 1280
                    lua.globals()._UILogic.ScreenHeight = 720
                    visual._T.enemyCenterCache["ruid-target"] = lua.eval("Vector2(9,-8)")
                    for delta in (1 / 30, 1 / 60, 1 / 144, 0.2):
                        visual.UpdateBattleVisuals(visual, delta)
                        self.assertEqual(visual._T.playerShotTargetUid, 2)
                        assert_vec(self, visual._T.playerShotStartPosition, start)
                        assert_vec(self, visual._T.playerShotEndPosition, endpoint)
                        self.assertAlmostEqual(visual._T.playerShotRotation, rotation, places=7)
                        position = visual.localBattleShot.TransformComponent.Position
                        dx, dy = endpoint.x-start.x, endpoint.y-start.y
                        cross = (position.x-start.x)*dy-(position.y-start.y)*dx
                        self.assertAlmostEqual(cross, 0, places=6, msg="砲彈必須沿發射時固定線段前進")
                        self.assertGreaterEqual((position.x-start.x)*dx+(position.y-start.y)*dy, 0)

    def test_visual_miss_keeps_uid_and_line_ends_outside_sprite_without_impact(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.1, flight=1)
        wave.enemies.playerShot = lua.table(
            sequence=1,targetUid=2,animationRuid="ruid-target",elapsed=0.1,flightSeconds=1,hit=False
        )
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0.2,-0.1)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        visual._T.enemyMissRadius = lua.table_from({"ruid-target": 2.5})
        visual._T.impacts = lua.table()
        lua.execute("""
            local complete=TestVisual.CompletePlayerShotVisual
            TestVisual.CompletePlayerShotVisual=function(self,target)
                if self.lastPlayerShotSequence > (self._T.lastImpactSequence or 0) then
                    self._T.completionCount=(self._T.completionCount or 0)+1
                end
                return complete(self,target)
            end
        """)
        visual.UpdateBattleVisuals(visual, 0.05)
        start = visual._T.playerShotStartPosition
        endpoint = visual._T.playerShotEndPosition
        rotation = visual._T.playerShotRotation
        uid = visual._T.playerShotTargetUid
        impact_time = visual._T.playerShotImpactTime
        center = visual.GetBattleTargetCenter(visual, uid, "ruid-target", impact_time)
        self.assertFalse(visual._T.playerShotHit)
        self.assertEqual(uid, 2)
        self.assertGreaterEqual(((endpoint.x-center.x)**2+(endpoint.y-center.y)**2)**0.5, 2.5-1e-7)
        battle.enemyId = "other"
        visual.UpdateBattleVisuals(visual, 0.4)
        position = visual.localBattleShot.TransformComponent.Position
        dx,dy=endpoint.x-start.x,endpoint.y-start.y
        self.assertAlmostEqual((position.x-start.x)*dy-(position.y-start.y)*dx,0,places=6)
        self.assertAlmostEqual(visual._T.playerShotRotation,rotation,places=7)
        visual.UpdateBattleVisuals(visual, 0.5)
        body = visual._T.waveViews[uid].TransformComponent.Position
        expected_body = visual.GetBattleRoamPosition(visual,uid,visual.battleVisualElapsed)
        assert_vec(self,body,expected_body)
        self.assertEqual(visual._T.playerShotTargetUid,2)
        self.assertEqual(visual._T.lastImpactSequence,1)
        self.assertEqual(visual._T.completionCount,1)
        self.assertEqual(len(visual._T.impacts),0)
        visual.CompletePlayerShotVisual(visual,endpoint)
        self.assertEqual(visual._T.completionCount,1)
        self.assertEqual(len(visual._T.impacts),0)

    def test_missing_shot_metadata_waits_and_uses_late_original_uid(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, with_meta=False)
        visual.UpdateBattleVisuals(visual, 0.05)
        self.assertEqual(visual.lastPlayerShotSequence, 0)
        self.assertIsNone(visual._T.playerShotTargetUid)
        battle.enemyId = "other"
        wave.enemies.playerShot = lua.table(
            sequence=1,targetUid=2,animationRuid="ruid-target",elapsed=0,flightSeconds=1
        )
        visual.UpdateBattleVisuals(visual, 0.05)
        self.assertEqual(visual.lastPlayerShotSequence, 1)
        self.assertEqual(visual._T.playerShotTargetUid, 2)
        self.assertEqual(visual._T.playerShotTargetRuid, "ruid-target")

    def test_late_snapshot_finishes_once_and_won_cleanup_does_not_recreate_visuals(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.3, flight=1)
        lua.globals()._UtilLogic.ElapsedSeconds = 11.2
        visual.UpdateBattleVisuals(visual, 0.05)
        self.assertEqual(visual.lastPlayerShotSequence, 1)
        self.assertEqual(visual._T.lastImpactSequence, 1)
        self.assertEqual(len(visual._T.impacts), 1)
        battle.phase = "won"
        for _ in range(3):
            visual.UpdateBattleVisuals(visual, 0.25)
        self.assertEqual(len(visual._T.impacts), 1)
        self.assertEqual(visual._T.completedBattleId, "mixed")
        visual.UpdateBattleVisuals(visual, 0.1)
        self.assertEqual(len(visual._T.impacts), 1)
        self.assertEqual(visual.appliedBattleId, "")

    def test_complete_and_release_are_idempotent_without_alias_double_destroy(self):
        lua, visual = visual_runtime()
        visual.lastPlayerShotSequence = 7
        visual._T.lastImpactSequence = 0
        shot = lua.eval("entity(Vector3(0,0,0))")
        primary = lua.eval("entity(Vector3(0,0,0))")
        visual.localBattleShot = shot
        visual.localBattleEnemy = primary
        visual.localEnemyShot = lua.eval("entity(Vector3(0,0,0))")
        visual._T.waveViews = lua.table_from({1: primary})
        visual._T.playerShotTargetUid = 1
        target = lua.eval("Vector3(4,5,0)")
        visual.CompletePlayerShotVisual(visual, target)
        visual.CompletePlayerShotVisual(visual, target)
        self.assertEqual(len(visual._T.impacts), 1)
        visual.appliedBattleId = "mixed"
        visual.ReleaseBattleVisuals(visual)
        visual.ReleaseBattleVisuals(visual)
        self.assertEqual(primary.destroyCount, 1)
        self.assertEqual(shot.destroyCount, 1)
        self.assertEqual(visual.localBattleEnemy, None)


class DamageSkinVisualTests(unittest.TestCase):
    def test_hit_uses_server_damage_critical_and_anchor_survives_enemy_death(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.9, flight=1)
        shot = wave.enemies.playerShot
        shot.damage = 37
        shot.critical = True
        shot.hit = True
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0.2,-0.1)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        lua.execute("""
            local complete=TestVisual.CompletePlayerShotVisual
            TestVisual.CompletePlayerShotVisual=function(self,target)
                if self.lastPlayerShotSequence > (self._T.lastImpactSequence or 0) then
                    self._T.completionCount=(self._T.completionCount or 0)+1
                end
                return complete(self,target)
            end
        """)
        visual.UpdateBattleVisuals(visual, 0.05)
        visual.UpdateBattleVisuals(visual, 0.1)
        self.assertEqual(visual._T.lastImpactSequence, 1)
        self.assertEqual(visual._T.completionCount, 1)
        self.assertEqual(len(visual._T.impacts), 1)
        self.assertEqual(len(lua.globals()._DamageSkinService.calls), 1)
        self.assertEqual(len(lua.globals()._DamageSkinService.textCalls), 0)
        call = lua.globals()._DamageSkinService.calls[1]
        self.assertEqual(len(call), 11)
        self.assertEqual(call[2], "3271c3e79bf04ecba9a107d55495970d")
        self.assertEqual(call[3], 0)
        self.assertEqual(call[4][1], 37)
        self.assertEqual(call[5], "TweenDefault")
        self.assertTrue(call[6])
        self.assertEqual(call[7].x, 0)
        self.assertEqual(call[7].y, 0.4)
        anchor = visual._T.damageNumbers[1].entity
        self.assertIsNotNone(anchor.DamageSkinComponent)
        anchor_position = anchor.TransformComponent.Position
        monster = visual._T.waveViews[2]
        monster.Destroy(monster)
        self.assertFalse(monster.valid)
        self.assertTrue(anchor.valid)
        assert_vec(self, anchor.TransformComponent.Position, anchor_position)
        visual.CompletePlayerShotVisual(visual, visual._T.playerShotEndPosition)
        self.assertEqual(visual._T.completionCount, 1)
        self.assertEqual(len(lua.globals()._DamageSkinService.calls), 1)

    def test_miss_uses_native_miss_text_at_live_world_center_and_legacy_damage_is_absent(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.9, flight=1)
        shot = wave.enemies.playerShot
        shot.hit = False
        shot.damage = 0
        visual._T.impacts = lua.table()
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0.2,-0.1)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        visual.UpdateBattleVisuals(visual, 0.05)
        visual.UpdateBattleVisuals(visual, 0.1)
        self.assertEqual(visual._T.lastImpactSequence, 1)
        self.assertEqual(len(visual._T.impacts), 0)
        self.assertEqual(len(lua.globals()._DamageSkinService.calls), 0)
        self.assertEqual(len(lua.globals()._DamageSkinService.textCalls), 1)
        self.assertIsNone(visual._T.hitPoses[2])
        call = lua.globals()._DamageSkinService.textCalls[1]
        self.assertEqual(len(call), 9)
        self.assertEqual(call[2], "3271c3e79bf04ecba9a107d55495970d")
        self.assertEqual(call[3], "MissEnum")
        self.assertIsInstance(call[3], str)
        anchor = visual._T.damageNumbers[1].entity
        monster = visual._T.waveViews[2]
        expected = visual.GetBattleEnemyCenter(visual, monster.TransformComponent.WorldPosition, "ruid-target")
        expected = lua.eval(f"Vector3({expected.x},{monster.TransformComponent.WorldPosition.y+0.15},{monster.TransformComponent.WorldPosition.z})")
        assert_vec(self, anchor.TransformComponent.Position, expected)
        self.assertEqual(lua.globals()._DamageSkinService.textCalls[1][5].x, 0)
        self.assertEqual(lua.globals()._DamageSkinService.textCalls[1][5].y, 0)
        self.assertTrue(anchor.valid)
        visual.CompletePlayerShotVisual(visual, visual._T.playerShotEndPosition)
        self.assertEqual(len(lua.globals()._DamageSkinService.textCalls), 1)

    def test_legacy_shot_without_damage_keeps_hit_but_spawns_no_number(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.9, flight=1)
        self.assertIsNone(wave.enemies.playerShot.damage)
        self.assertIsNone(wave.enemies.playerShot.hit)
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0,0)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        visual.UpdateBattleVisuals(visual, 0.05)
        visual.UpdateBattleVisuals(visual, 0.1)
        self.assertEqual(visual._T.lastImpactSequence, 1)
        self.assertEqual(len(visual._T.impacts), 1)
        self.assertEqual(len(visual._T.damageNumbers or ()), 0)
        self.assertEqual(len(lua.globals()._DamageSkinService.calls), 0)
        self.assertEqual(len(lua.globals()._DamageSkinService.textCalls), 0)

    def test_damage_anchor_cap_ttl_off_map_and_release_cleanup(self):
        lua, visual = visual_runtime()
        visual._T.playerShotHit = True
        visual._T.playerShotDamage = 1
        visual._T.playerShotCritical = False
        for index in range(17):
            visual.ShowBattleDamageNumber(visual, lua.eval(f"Vector3({index},2,0)"))
        self.assertEqual(len(visual._T.damageNumbers), 16)
        first = lua.globals()._SpawnService.spawned[1]
        self.assertEqual(first.destroyCount, 1)
        last = visual._T.damageNumbers[16].entity
        self.assertTrue(last.valid)
        self.assertEqual(len(lua.globals()._DamageSkinService.calls), 17)

        lua.globals()._UtilLogic.ElapsedSeconds = 1.2
        visual.UpdateBattleDamageNumbers(visual)
        self.assertEqual(len(visual._T.damageNumbers), 0)
        self.assertFalse(last.valid)

        lua.globals()._UtilLogic.ElapsedSeconds = 2
        visual.ShowBattleDamageNumber(visual, lua.eval("Vector3(4,5,0)"))
        offmap = visual._T.damageNumbers[1].entity
        lua.execute('otherMap={Name="other"}; _UserService.LocalPlayer.CurrentMap=otherMap')
        visual.UpdateBattleDamageNumbers(visual)
        self.assertEqual(len(visual._T.damageNumbers), 0)
        self.assertFalse(offmap.valid)

        lua.execute('_UserService.LocalPlayer.CurrentMap=map')
        lua.globals()._UtilLogic.ElapsedSeconds = 3
        visual.ShowBattleDamageNumber(visual, lua.eval("Vector3(6,7,0)"))
        to_release = visual._T.damageNumbers[1].entity
        visual.ReleaseLocalViews(visual)
        self.assertEqual(len(visual._T.damageNumbers), 0)
        self.assertFalse(to_release.valid)



class HitPoseVisualTests(unittest.TestCase):
    def launch_hit_to_completion(self, *, elapsed=0.9):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=elapsed, flight=1)
        wave.enemies.playerShot.damage = 12
        wave.enemies.playerShot.critical = False
        wave.enemies.playerShot.hit = True
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0,0)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        visual.UpdateBattleVisuals(visual, 0.05)
        visual.UpdateBattleVisuals(visual, 0.1)
        return lua, visual, battle, wave

    def test_hit_pose_uses_original_uid_clip_roams_and_restores_without_rewriting_same_clip(self):
        lua, visual, battle, wave = self.launch_hit_to_completion()
        view = visual._T.waveViews[2]
        self.assertEqual(view.SpriteRendererComponent.SpriteRUID, "hit1-target")
        self.assertEqual(visual._T.hitPoses[2].originalRuid, "ruid-target")
        writes_during_hit = view.SpriteRendererComponent.SpriteRUIDWrites
        position_during_hit = view.TransformComponent.Position
        visual.UpdateBattleVisuals(visual, 0.08)
        moved_during_hit = view.TransformComponent.Position
        self.assertNotAlmostEqual(moved_during_hit.x, position_during_hit.x, places=6)
        self.assertEqual(view.SpriteRendererComponent.SpriteRUID, "hit1-target")
        self.assertEqual(view.SpriteRendererComponent.SpriteRUIDWrites, writes_during_hit)
        visual.UpdateBattleVisuals(visual, 0.08)
        self.assertEqual(view.SpriteRendererComponent.SpriteRUIDWrites, writes_during_hit)
        visual.UpdateBattleVisuals(visual, 0.16)
        self.assertEqual(view.SpriteRendererComponent.SpriteRUID, "ruid-target")
        writes_after_restore = view.SpriteRendererComponent.SpriteRUIDWrites
        self.assertEqual(writes_after_restore, writes_during_hit+1)
        visual.UpdateBattleVisuals(visual, 0.05)
        self.assertEqual(view.SpriteRendererComponent.SpriteRUIDWrites, writes_after_restore)

    def test_miss_never_starts_hit_pose(self):
        lua, visual = visual_runtime()
        battle, wave = shot_fixture(lua, visual, elapsed=0.9, flight=1)
        wave.enemies.playerShot.hit = False
        wave.enemies.playerShot.targetId = "target"
        visual._T.enemyCenterCache = lua.table_from({"ruid-target": lua.eval("Vector2(0,0)")})
        visual._T.enemyCenterReady = lua.table_from({"ruid-target": True})
        visual.UpdateBattleVisuals(visual, 0.05)
        visual.UpdateBattleVisuals(visual, 0.1)
        self.assertIsNone(visual._T.hitPoses[2])
        self.assertEqual(visual._T.waveViews[2].SpriteRendererComponent.SpriteRUID, "ruid-target")

    def test_dead_hit_uid_keeps_pose_then_only_that_entity_is_destroyed_and_release_clears(self):
        lua, visual, battle, wave = self.launch_hit_to_completion()
        dead_view = visual._T.waveViews[2]
        other_view = visual._T.waveViews[3]
        other_position = other_view.TransformComponent.Position
        self.assertEqual(dead_view.SpriteRendererComponent.SpriteRUID, "hit1-target")
        wave.enemies = lua.table_from([
            lua.table(uid=1,id="primary",animationRuid="ruid-primary",hp=10),
            lua.table(uid=3,id="other",animationRuid="ruid-other",hp=10),
        ])
        visual.UpdateBattleHitPoses(visual, 0.1, wave)
        self.assertTrue(visual._T.hitPoses[2].isDead)
        frozen_position = dead_view.TransformComponent.Position
        visual.UpdateBattleWaveViews(visual, battle, lua.globals().map)
        assert_vec(self, dead_view.TransformComponent.Position, frozen_position)
        assert_vec(self, other_view.TransformComponent.Position, other_position)
        visual.UpdateBattleHitPoses(visual, 0.19, wave)
        self.assertTrue(dead_view.valid)
        visual.UpdateBattleHitPoses(visual, 0.02, wave)
        self.assertFalse(dead_view.valid)
        self.assertEqual(dead_view.destroyCount, 1)
        self.assertIsNone(visual._T.waveViews[2])
        self.assertTrue(other_view.valid)
        assert_vec(self, other_view.TransformComponent.Position, other_position)

        visual.StartBattleHitPose(visual, 3, "other", "ruid-other")
        self.assertEqual(visual._T.hitPoses[3].hitRuid, "hit1-other")
        visual.ReleaseBattleVisuals(visual)
        self.assertEqual(len(visual._T.hitPoses), 0)
        self.assertFalse(other_view.valid)

    def test_hit_clip_preload_is_current_wave_only_deduplicated_and_cached(self):
        lua, visual = visual_runtime()
        wave = lua.eval("""{
            id="mixed",
            enemies={
                {uid=1,id="target",animationRuid="ruid-target"},
                {uid=2,id="target",animationRuid="ruid-target"},
                {uid=3,id="primary",animationRuid="ruid-primary"}
            }}""")
        visual.PreloadBattleMonsterHitAnimations(visual, wave)
        service = lua.globals()._ResourceService
        self.assertEqual(len(service.calls), 1)
        requested = [service.calls[1].ids[i] for i in range(1,len(service.calls[1].ids)+1)]
        self.assertEqual(requested, ["hit1-target", "hit1-primary"])
        service.calls[1].callback(lua.table_from(["Success", "Success"]))
        visual.PreloadBattleMonsterHitAnimations(visual, wave)
        self.assertEqual(len(service.calls), 1)
        expanded = lua.eval("""{
            id="mixed",
            enemies={
                {uid=1,id="target"},
                {uid=2,id="other"}
            }}""")
        visual.PreloadBattleMonsterHitAnimations(visual, expanded)
        self.assertEqual(len(service.calls), 2)
        added = [service.calls[2].ids[i] for i in range(1,len(service.calls[2].ids)+1)]
        self.assertEqual(added, ["hit1-other"])



class MissTextAnchorTests(unittest.TestCase):
    def test_small_and_large_monsters_use_frame_top_offset_from_actual_world_position(self):
        for top_offset in (0.45, 2.8):
            with self.subTest(top_offset=top_offset):
                lua, visual = visual_runtime()
                visual._T.waveViews = lua.table()
                view = lua.eval("entity(Vector3(-9,-8,0))")
                view.TransformComponent.ActualWorldPosition = lua.eval("Vector3(12,7,3)")
                visual._T.waveViews[4] = view
                visual._T.enemyCenterCache = lua.table_from({"ruid-sized": lua.eval("Vector2(0.4,-0.2)")})
                visual._T.enemyTopOffsetCache = lua.table_from({"ruid-sized": top_offset})
                result = visual.GetBattleMissTextPosition(visual, 4, "ruid-sized", 3.25)
                self.assertAlmostEqual(result.x, 12 - 0.4*1.5, places=7)
                self.assertAlmostEqual(result.y, 7 + top_offset + 0.15, places=7)
                self.assertAlmostEqual(result.z, 3, places=7)
                # world anchor is deliberatey distinct from the local view position.
                self.assertNotAlmostEqual(result.x, -9, places=3)
                self.assertNotAlmostEqual(result.y, -8, places=3)

    def test_missing_view_falls_back_to_the_same_uids_roam_position(self):
        lua, visual = visual_runtime()
        visual._T.waveViews = lua.table()
        visual._T.enemyCenterCache = lua.table_from({"ruid-fallback": lua.eval("Vector2(0.2,0.3)")})
        visual._T.enemyTopOffsetCache = lua.table_from({"ruid-fallback": 1.1})
        uid, elapsed = 7, 2.75
        roam = visual.GetBattleRoamPosition(visual, uid, elapsed)
        result = visual.GetBattleMissTextPosition(visual, uid, "ruid-fallback", elapsed)
        self.assertAlmostEqual(result.x, roam.x-0.2*1.5, places=7)
        self.assertAlmostEqual(result.y, roam.y+1.1+0.15, places=7)
        other = visual.GetBattleRoamPosition(visual, uid+1, elapsed)
        self.assertNotAlmostEqual(result.y, other.y+1.1+0.15, places=5)



class AtomicAirProjectionTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            log=function(...) end
            isvalid=function(value) return value ~= nil and value.valid ~= false end
            _UtilLogic={ElapsedSeconds=50,ServerElapsedSeconds=50}
            _UserService={LocalPlayer={valid=true,PlayerComponent={UserId="captain"}}}
            State={_T={}}
            _GreatVoyageAdventureController={_T={},calls=0,
                ReceiveAirBattleSnapshot=function(self,id,phase,airspaceId,enemyId,enemyName,enemyHp,enemyMaxHp,
                    playerHp,playerMaxHp,remainingSeconds,outcome,playerShotSequence,enemyShotSequence,
                    playerShotElapsed,enemyShotElapsed,playerId)
                    self.calls=self.calls+1
                    self.clientAirBattle={id=id,phase=phase,airspaceId=airspaceId,enemyId=enemyId,
                        enemyName=enemyName,enemyHp=enemyHp,enemyMaxHp=enemyMaxHp,playerHp=playerHp,
                        playerMaxHp=playerMaxHp,remainingSeconds=remainingSeconds,outcome=outcome,
                        playerShotSequence=playerShotSequence,enemyShotSequence=enemyShotSequence,
                        playerShotElapsed=playerShotElapsed,enemyShotElapsed=enemyShotElapsed}
                end,
                RefreshAirBattleDisplay=function(self) self.refreshes=(self.refreshes or 0)+1 end}
        """)
        bind(self.lua, "State", STATE, [
            "PublishAirBattleSnapshot", "ReceiveAirWaveSnapshot", "ReceiveAirBattleSnapshot"
        ])
        self.state = self.lua.globals().State
        self.controller = self.lua.globals()._GreatVoyageAdventureController

    def test_publish_projects_one_atomic_wave_with_monotonic_serial_and_metadata(self):
        bind(self.lua, "State", STATE, ["PublishAirBattleSnapshot"])
        battle = self.lua.execute("""
            local b={id="b-7",phase="active",airspaceId="sky",enemyId="first",enemyName="第一隻",
                enemyHp=9,enemyMaxHp=12,endsAt=70,playerShotSequence=4,enemyShotSequence=2,
                lastPlayerShotAt=49,lastEnemyShotAt=48,flightSeconds=0.6,kills=1,
                lastPlayerShotTarget={uid=2,id="second",animationRuid="ruid-second"},
                lastEnemyShotSource={uid=3,animationRuid="ruid-third"},
                enemies={
                    {uid=1,id="first",name="第一隻",hp=0,maxHp=12,active=true},
                    {uid=2,id="second",name="第二隻",hp=7,maxHp=10,active=true,animationRuid="ruid-second",bounty=30},
                    {uid=3,id="third",name="第三隻",hp=8,maxHp=8,active=false,animationRuid="ruid-third",bounty=40}}
            }
            return b
        """)
        state = self.lua.table(airBattle=battle, ship=self.lua.table(hull=500,maxHull=700), pendingBounty=20,bountyCredit=3)
        self.state.PublishAirBattleSnapshot(self.state, "captain", state)
        first_wave = self.controller._T.airWave
        self.assertEqual(first_wave.id, "b-7")
        self.assertEqual(first_wave.remaining, 2)
        self.assertEqual(first_wave.total, 3)
        self.assertEqual(first_wave.kills, 1)
        self.assertEqual(len(first_wave.enemies), 1)
        self.assertEqual(first_wave.enemies[1].uid, 2)
        self.assertEqual(first_wave.enemies.playerShot.targetUid, 2)
        self.assertEqual(first_wave.enemies.playerShot.sequence, 4)
        self.assertEqual(first_wave.enemies.enemyShot.sourceUid, 3)
        self.assertEqual(first_wave.enemies.projection.phase, "active")
        serial1 = first_wave.enemies.projection.serial
        self.state.PublishAirBattleSnapshot(self.state, "captain", state)
        second_wave = self.controller._T.airWave
        self.assertEqual(second_wave.enemies.projection.serial, serial1 + 1)
        self.assertEqual(self.controller.calls, 2)

    def test_out_of_order_and_legacy_scalar_cannot_override_atomic_won(self):
        def receive(serial, phase, enemy_id):
            projection = self.lua.table(
                serial=serial,id="atomic",phase=phase,airspaceId="sky",enemyId=enemy_id,
                enemyName=enemy_id,enemyHp=0 if phase == "won" else 9,enemyMaxHp=9,
                playerHp=500,playerMaxHp=700,remainingSeconds=0 if phase == "won" else 20,
                outcome=phase,playerShotSequence=3,enemyShotSequence=1,
                playerShotElapsed=0.4,enemyShotElapsed=0.2,
            )
            enemies = self.lua.table(projection=projection)
            self.state.ReceiveAirWaveSnapshot(self.state,"atomic",enemies,0 if phase=="won" else 1,2,2 if phase=="won" else 1,20,0,"captain")

        receive(2, "won", "last")
        calls_after_won = self.controller.calls
        retained_wave = self.controller._T.airWave
        receive(1, "active", "stale")
        self.assertEqual(self.controller.calls, calls_after_won)
        self.assertEqual(self.controller._T.airWave.enemies.projection.serial, retained_wave.enemies.projection.serial)
        self.assertEqual(self.controller.clientAirBattle.phase, "won")
        self.assertEqual(self.controller.clientAirBattle.enemyId, "last")
        self.assertEqual(self.controller._T.airProjectionSerial, 2)
        self.state.ReceiveAirBattleSnapshot(
            self.state,"atomic","active","sky","legacy","舊快照",9,9,500,700,30,"",
            2,1,0.1,0.1,"captain"
        )
        self.assertEqual(self.controller.calls, calls_after_won)
        self.assertEqual(self.controller.clientAirBattle.phase, "won")


class EnemyCenterPreloadRetryTests(unittest.TestCase):
    def setUp(self):
        self.lua, self.visual = visual_runtime()
        bind(self.lua, "TestVisual", VISUAL, ["LoadBattleEnemyCenter"])
        self.lua.execute("""
            _ResourceService.pending={}
            _ResourceService.calls=0
            _ResourceService.clip=nil
            _ResourceService.PreloadAsync=function(self,ids,callback)
                self.calls=self.calls+1
                table.insert(self.pending,{ruid=ids[1],callback=callback})
            end
            _ResourceService.LoadAnimationClipAndWait=function(self,ruid) return self.clip end
            _UtilLogic.ElapsedSeconds=100
            _UtilLogic.ServerElapsedSeconds=100
        """)

    def set_time(self, seconds):
        self.lua.globals()._UtilLogic.ElapsedSeconds = seconds
        self.lua.globals()._UtilLogic.ServerElapsedSeconds = seconds

    def set_unready_clip(self):
        self.lua.execute("""
            _ResourceService.clip={IsLoadComplete=false,Frames={ToTable=function(self) return {} end}}
        """)

    def set_ready_clip(self):
        self.lua.execute("""
            _ResourceService.clip={IsLoadComplete=true,Frames={ToTable=function(self)
                return {
                    {FrameSprite={IsLoadComplete=true,PixelPerUnit=100,Width=100,Height=80,PivotPixel={x=40,y=20}}},
                    {FrameSprite={IsLoadComplete=true,PixelPerUnit=100,Width=100,Height=100,PivotPixel={x=30,y=20}}}
                }
            end}}
        """)

    def complete_pending(self, index):
        pending = self.lua.globals()._ResourceService.pending[index]
        pending.callback(self.lua.table())

    def test_failed_load_cools_down_then_native_frames_set_positive_center(self):
        self.set_unready_clip()
        self.visual.LoadBattleEnemyCenter(self.visual, "ruid-x")
        self.complete_pending(1)
        self.visual.LoadBattleEnemyCenter(self.visual, "ruid-x")
        self.assertEqual(self.lua.globals()._ResourceService.calls, 1)
        self.assertFalse(self.visual._T.enemyCenterReady["ruid-x"] or False)
        self.set_time(101)
        self.visual.LoadBattleEnemyCenter(self.visual, "ruid-x")
        self.assertEqual(self.lua.globals()._ResourceService.calls, 2)
        self.set_ready_clip()
        self.complete_pending(2)
        self.assertTrue(self.visual._T.enemyCenterReady["ruid-x"])
        self.assertAlmostEqual(self.visual._T.enemyCenterCache["ruid-x"].x, 0.15, places=7)
        self.assertAlmostEqual(self.visual._T.enemyCenterCache["ruid-x"].y, 0.25, places=7)
        self.assertGreater(self.visual._T.enemyMissRadius["ruid-x"], 0)
        self.assertAlmostEqual(self.visual._T.enemyTopOffsetCache["ruid-x"], 1.2, places=7)

    def test_three_failed_loads_stop_retries(self):
        self.set_unready_clip()
        for attempt, now in enumerate((200, 201, 202), start=1):
            self.set_time(now)
            self.visual.LoadBattleEnemyCenter(self.visual, "ruid-bad")
            self.complete_pending(attempt)
        self.assertEqual(self.lua.globals()._ResourceService.calls, 3)
        self.set_ready_clip()
        self.set_time(210)
        for _ in range(20):
            self.visual.LoadBattleEnemyCenter(self.visual, "ruid-bad")
        self.assertEqual(self.lua.globals()._ResourceService.calls, 3)
        self.assertFalse(self.visual._T.enemyCenterReady["ruid-bad"] or False)


if __name__ == "__main__":
    unittest.main()
