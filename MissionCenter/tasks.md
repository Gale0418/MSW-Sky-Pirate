# Tasks
> 狀態備註：2026-08-06 E8 Wave 1 三場景、自製船、自然移動與舊原型隔離已通過 Maker 與 Terra 零批評複審，GV-T2 進行中。


| ID | Title | Type | Parent | Priority | Status | Owner | Depends on | Next action | Verification | Estimate | Labels | Comments |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 航線與空域資料表 | Epic |  | P1 | Done | Codex |  | 第一版已內嵌魔法森林/天空之城與普通雲海/黑雲帶 | Maker logs 顯示 5 次出航含普通雲海與黑雲帶 | M | plan, msw | Phase 0 只做普通雲海與黑雲帶 |
| E2 | 貿易貨物與價格結算 | Epic |  | P1 | Backlog | Codex | E1 | 分離交易貨物與升級素材 | 手動檢查買入、賣出、素材保留規則 | M | plan, prototype | 避免升級素材被當普通商品賣光 |
| E3 | 航行事件抽選與獎懲 | Epic |  | P1 | Done | Codex | E1 | 已在 Phase0VoyagePrototype 實作事件池與結算效果 | Maker logs 顯示 5 次事件抽選與損益結算 | M | execution, prototype | 平安、寶箱、小怪、大巴前兆 |
| E4 | 船體/護盾升級循環 | Epic |  | P1 | Done | Codex | E3 | 已在 Phase0VoyagePrototype 實作船體與護盾升級 | Maker logs 顯示船體 Lv.2 HP 128、護盾 Lv.2 耐久 38 | M | execution, prototype | Phase 0 只做船體與護盾 |
| E5 | 後續玩法 Backlog | Epic |  | P2 | Backlog | Codex |  | 保留但不進 Phase 0 | Backlog 項目不影響 Phase 0 完成 | L | backlog | 甲板戰、航線 UI、大巴正式戰、空賊玩法 |
| P0-T0 | 第一版可試玩文字循環 | Task | E4 | P0 | Done | Codex | P0-T1 | 已新增 Maker @Logic 按鍵文字流程 | Maker Play Test 可按 1/2/3/4/R 操作並輸出 logs | S | execution, msw | 第一版 playable |
| P0-T1 | 定稿 Phase 0 設計規格 | Task | E1 | P0 | Done | Codex |  | 已寫入 docs/superpowers/specs/2026-07-09-phase0-playable-design.md | 文件包含目標、非目標、操作、核心資料、驗證方式 | S | plan | 第一版規格已落地 |
| P0-T2 | 建立最小地點資料 | Task | E1 | P1 | Done | Codex | P0-T1 | 已內嵌魔法森林與天空之城 | Maker logs 顯示魔法森林與天空之城往返 | S | execution | 只做兩地點 |
| P0-T3 | 建立最小航線資料 | Task | E1 | P1 | Done | Codex | P0-T1 | 已定義魔法森林 <-> 天空之城航線 | Maker logs 顯示普通雲海、黑雲帶、風險與事件池 | S | execution | 第一條核心航線 |
| P0-T4 | 建立交易貨物與素材規則 | Task | E2 | P1 | Backlog | Codex | P0-T2 | 區分交易貨物與升級素材 | 手動檢查交易貨物可買賣，素材用於升級 | S | execution | 先避免動態經濟；第一版 playable 尚未接入 |
| P0-T5 | 建立事件抽選原型 | Task | E3 | P1 | Done | Codex | P0-T3 | 已實作順風、寶箱、小怪、大巴前兆 | Maker logs 中 5 次出航看到 4 種事件 | M | execution | 小怪先用文字結算 |
| P0-T6 | 建立航行結算原型 | Task | E3 | P1 | Done | Codex | P0-T5 | 已結算金錢、素材、船體 HP、護盾 | 出航後數值變化符合事件結果 | M | execution | 第一版暫不含交易貨物 |
| P0-T7 | 建立船體/護盾升級原型 | Task | E4 | P1 | Done | Codex | P0-T6 | 已定義成本與升級效果 | Maker logs 顯示船體與護盾升級成功 | S | execution | 只做兩種升級 |
| P0-T8 | Phase 0 煙霧測試 | Task | E4 | P0 | Done | Codex | P0-T7 | 已連續完成 5 次出航與 2 次升級 | smoke-tests.md 已記錄 Maker MCP 測試結果 | S | verification | Done 前已有驗證紀錄 |
| E6 | A 可玩垂直切片 | Epic |  | P0 | Done | Codex | E2,E3,E4 | 已完成交易、飛行、甲板戰與官方三場景重驗 | AC-T6／AC-T8 smoke test 通過 | L | plan, execution, verification | 2026-07-15 Maker MCP 重驗完成 |
| E7 | C 資料驅動可擴展骨架 | Epic |  | P1 | Done | Codex | E1,E2 | 先建立 schema 與介面，再保留內容擴充 | AC-T0 schema 檢查通過 | M | architecture, execution | 預留港口、貨物、航線怪物池、角色成長、技能書商店 |
| AC-T0 | 多港口／多貨物／航線與戰鬥資料 schema | Task | E7 | P0 | Done | Codex | E1,E2 | 定義 port、good、route、monsterPool、growth、skillBookShop 介面 | 資料可表達兩港口、多貨物、價差、菇菇與未來欄位 | S | architecture, msw | 只建立目前會用的 schema 與事件邊界 |
| AC-T1 | 魔法森林↔天空之城實際價差交易 | Task | E6 | P0 | Done | Codex | AC-T0,P0-T2 | 接通港口買入、航行、抵達賣出 | 買入、容量不足、獲利與虧損都有 log 證據 | M | economy, msw | 出航不保證獲利 |
| AC-T2 | style-4-blue 港口／交易／航線 UI | Task | E6 | P0 | Done | Codex | AC-T0 | UIBuilder 增量擴充交易列、數量、買賣與航線狀態 | UI lint 通過且按鈕事件與交易 log 對上 | M | ui, msw | 保留既有 UUID 綁定 |
| AC-T3 | 飛行背景、雲層、甲板與三層船體 | Task | E6 | P1 | Done | Codex | AC-T2 | 呈現飛行與可站立甲板，接護盾/裝甲/結構 | Play 畫面可辨識且 build logs 0 | M | visual, map, ship | 不做真自由座標飛行 |
| AC-T4 | 3 隻橘菇菇空降甲板 | Task | E6 | P0 | Done | Codex | AC-T0,AC-T3 | MapleTile/Rigidbody 從甲板上方生成並落地 | 正好 3 隻落在甲板範圍且無錯誤 | M | monster, combat, msw | 使用真實菇菇資源包 |
| AC-T5 | 玩家 Attack→Hit 護船 | Task | E6 | P0 | Done | Codex | AC-T4 | 接入玩家攻擊、菇菇 HP 與水晶/船體受擊 | 玩家可擊殺菇菇；放任時船體可受損 | M | combat, msw | 只做甲板護船 |
| AC-T6 | A+C 垂直切片整合驗證 | Task | E6 | P0 | Done | Codex | AC-T1,AC-T5 | 已完成交易→航線→飛行→甲板戰→結算 | ST-AC-FINAL-001 與 ST-AC-BG-RECHECK-006 通過 | S | verification, msw | 2026-07-15 官方三場景與 HUD 重驗通過 |
| AC-T7 | 更多港口／貨物／路線怪、角色升級與技能書商店 | Task | E7 | P2 | Backlog | Codex | AC-T0 | 後續另立規格 | 後續獨立 smoke test | L | progression, shop, backlog | 本 Cycle 不實作；保留更多港口、貨物、路線怪與升級／技能書擴充 |
| B-T1 | 高難航線玩家離船空戰 | Task | E5 | P2 | Backlog | Codex | AC-T6 | 另立空戰地圖、離船狀態與敵群規格 | 未來獨立垂直切片 smoke test | XL | combat, high-risk, backlog | 主人指定先記錄 |

| AC-T8 | 恢復 MSW Maker MCP 並重驗官方三場景與 GreatVoyageHUD | Task | E6 | P0 | Done | Codex | AC-T3,AC-T6 | 已完成 refresh → build → Play → HUD 與三場景驗收 | ST-AC-BG-RECHECK-006：build 0、HUD 初始化、三場景截圖與切換 logs 通過 | S | verification, mcp, map, ui | 移除 6 個誤掛 SpawnLocationComponent 後 runtime 0 Error |

| E8 | 三場景探索、啟航與 NPC 商店 | Epic |  | P0 | Done | Codex | E6,E7 | 三場景探索、專屬船啟航、世界地圖、甲板中繼與 NPC 商店均完成 | 三圖可走；自製船正確；雙港航行與楓谷藥水交易可用；build/runtime 0 Error；雙評審 PASS | L | execution, verification | 2026-08-06 完成；每波 Terra 嚴評，Wave2/3 Antigravity 視覺 PASS |
| GV-T1 | 三張實體地圖與自製船配置 | Task | E8 | P0 | Done | Codex | AC-T8 | Wave 1 已完成；進入 GV-T2 靠船啟航與跨圖航行 | 三圖 TileMapMode=0；角色可走；魔森與天空城自製船可辨識；甲板可視；build/runtime 0 Error；Terra PASS 無剩餘批評 | M | execution, verification | 2026-08-06 Maker 三圖 Play/走動截圖通過；回歸修正後三圖自繪船統一 scale 0.40，天空城梯子可攀爬、登船點跟隨船 Transform/Scale、魔森舊船與 npc-5097 已清理 |
| GV-T2 | 靠船啟航、世界地圖與跨圖航行 | Task | E8 | P0 | Done | Codex | GV-T1 | Wave 2 完成；雙港靠自製船開圖、甲板中繼與抵港均通過 | 魔森與天空城雙向可達；非靠船時按鈕隱藏；目標與日誌正確；Terra/Antigravity PASS | M | execution, ui, map | 2026-08-06 build 0、runtime 全 Info；自製船恢復 0.18 完整輪廓 |
| GV-T3 | 港口 NPC 對話與交易 UI | Task | E8 | P0 | Done | Codex | GV-T1,GV-T2 | 兩港 NPC 2D 靠近交談與楓谷正式藥水商店完成 | 近 NPC 才顯示 E；紅/藍/橘藥水有官方圖示；買賣、金幣、貨艙與錯誤提示正確 | M | execution, ui, economy | 藍色藥水 sky 80G→forest 100G 實機交易；Terra 零批評 PASS |
| GV-T4 | 三場景實機截圖與嚴格評審 | Task | E8 | P0 | Done | Codex | GV-T1,GV-T2,GV-T3 | 三波 Maker 截圖/logs、Terra 反覆複審與 Antigravity 視覺終審完成 | build 0；runtime nonInfo 0；三場景、雙港航行、NPC 商店均有證據；最終零批評 | S | verification | Terra PASS — 無剩餘批評；Antigravity Wave2/3 PASS；船體回歸修正再經 Terra PASS，證據 E8_ship_follow_fix |