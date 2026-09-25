# Great Voyage M1 Phase 2 — World Map UI

## 目標與邊界

以 Phase 1 的 port／route 契約驅動世界地圖與 HUD 的目的地選擇、航線預覽與航行中狀態。本 Phase 只處理既有 world map modal／HUD 的呈現與互動綁定，不重做既有交易 UI，也不修改港口幾何與甲板戰。

## 本 Phase 需要參照的技能

- `msw-ui-system`：`references/component-api.md`、`references/runtime-patterns.md`、`references/builder-protocol-ui.md` 與選用的 style template。
- `msw-general`：`references/platform.md`、`references/authoring.md`、`references/builder-protocol.md`。
- `msw-scripting`：`references/verify-checklist.md`（若需要 UI event／狀態綁定）。

## 任務清單

- ✅ 建立世界地圖四港節點與目的地狀態呈現：`Forest`／`Sky`／`Ludus`／`Nihal` 均已建立，共用 0..1 座標；現行畫面為圓形地標徽章，名稱與可抵達港口資訊在圖側呈現。
- ✅ 綁定直航預覽：`GreatVoyageAdventureController` 透過 `_GreatVoyageVoyageState:PreviewDirectRoute(origin, destination)` 取得總距離、空域順序、分區距離／占比、危險等級與預期事件量；只繪製單一 `Route` Sprite，禁止 waypoint、drag、zoom。
- 🟡 整合確認／取消與既有流程：`Sail` 為確認、`Close` 為取消；Client 只提交目的地與自身 `PlayerComponent.UserId`，Server 以 `_UserService:GetUserEntityByUserId` 重新取得玩家、依所在港口與靠船狀態重做 Preview 驗證，再進入甲板；保留 `_Phase0VoyagePrototype` 商店／HUD 相容路徑。
- ✅ UIBuilder／事件與 client-only 靜態驗證：維持原 UIGroup 與既有 UUID，新增節點均以 builder 寫入並注入 controller 綁定；按鈕與取消／確認命中區至少 88px。
- 🟡 視覺與互動驗收：已取得森林→天空航圖、甲板遭遇與商店的 Maker 截圖及 build/runtime 證據；仍需逐一核對四港箭頭端點、圖面可讀性與點擊區。手機基本點按列後續檢查，不阻塞 M1 PC 驗收。

## 依賴與禁止事項

- 依賴：Phase 1 的資料契約與合法狀態定義；`StartVoyage(destination)` 的伺服器驗證由航行狀態層負責；Phase 3 做完整四港整合驗收。
- 禁止：在既定四港以外擴港、加入角色升級或離船空戰；這些進 Roadmap Backlog。
- 視覺層次、字級與可讀性不由代理單方面判定完成；使用者視覺驗收留在 Phase 3。

## 驗證

靜態：UIBuilder `validate()` 通過；`write()` 完成並自動 lint（僅 warnings，無 errors），53 個 UI entity；controller 綁定注入 6 個新屬性，所有修改方法標記 `ClientOnly`。

2026-09-25 已執行 Maker refresh／build logs／Play／runtime logs，森林→天空之城航線與航圖、商店有截圖；詳見 `MissionCenter/smoke-tests.md` 的 `ST-GV-M1-VOYAGE-002`。此證據只覆蓋一條航線，不代表四港全通過。

## 狀態轉移紀錄

- 港口節點與繁中木牌：⬜ → 🟡 → ✅（builder 寫入與靜態檢查通過）
- 直航預覽與單一路線 Sprite：⬜ → 🟡 → ✅（builder／controller 靜態檢查通過）
- 確認／取消及既有雙港、HUD／商店相容：⬜ → 🟡 → ✅（介面與保留呼叫靜態檢查通過）
- UIBuilder／client-only：⬜ → 🟡 → ✅（`validate()`、lint errors=0、綁定檢查通過）
- 視覺／互動：⬜ → 🟡（已有 PC Maker 部分證據；四港與使用者主觀視覺待驗，手機點按另列後續）

## UI 層級與資料介面

`GreatVoyageAdventure`（既有 UIGroup）
└── `WorldMapModal/Window`
    ├── `Frame`（木質底框）
    ├── `MapArt`（官方 RUID `3864db48f177422aadd68a74a19897df`，640×472，AspectOnly）
    ├── `Route`（唯一可伸縮／旋轉的 Sprite，禁止 waypoint／拖曳／縮放）
    ├── `Forest`／`Sky`／`Ludus`／`Nihal`（88×88 以上木牌按鈕；`victoria` 僅為舊資料 alias）
    ├── `PreviewPanel/Title`／`Summary`／`Order`／`Details`
    └── `Sail`（確認）／`Close`（取消）

控制器在 ClientOnly 顯示 `_GreatVoyageVoyageState:PreviewDirectRoute(originId, destinationId)` 結果；確認時由 Client 取得自己的 `PlayerComponent.UserId`，向 Server 請求 `_GreatVoyageVoyageState:StartVoyage(destinationId, playerId)`。Server 依 UserId 取得自己的玩家 Entity、origin／船體靠近狀態並重新呼叫 Preview 驗證，不能共用 Logic 的單一玩家屬性。`sky` 是天空之城港 canonical id，`victoria` 只作舊資料 alias；既有 `_Phase0VoyagePrototype` 商店／HUD 呼叫保留。

使用者：主人需在 PC Maker 確認地圖可讀性、字級與主觀風格；代理先補四港箭頭端點及按鈕命中證據。手機基本點按後續另測，未測不冒稱通過，但不作 M1 關閉前置。
