-- CityTradeManager.lua
-- 負責管理各港口的貨物庫存、基本物價與產出

local CityTradeManager = {}

-- 定義各個港口
CityTradeManager.Cities = {
    ["Lisbon"] = {
        name = "里斯本",
        inventory = {
            ["Salt"] = { basePrice = 10, currentPrice = 10, amount = 1000, productionRate = 50 },
            ["Wine"] = { basePrice = 30, currentPrice = 30, amount = 500, productionRate = 20 },
            ["OliveOil"] = { basePrice = 25, currentPrice = 25, amount = 800, productionRate = 30 }
        }
    },
    ["London"] = {
        name = "倫敦",
        inventory = {
            ["Wool"] = { basePrice = 40, currentPrice = 40, amount = 600, productionRate = 25 },
            ["Iron"] = { basePrice = 50, currentPrice = 50, amount = 400, productionRate = 15 }
        }
    },
    ["Venice"] = {
        name = "威尼斯",
        inventory = {
            ["Glass"] = { basePrice = 80, currentPrice = 80, amount = 200, productionRate = 5 },
            ["Silk"] = { basePrice = 100, currentPrice = 100, amount = 100, productionRate = 2 }
        }
    }
}

-- 初始化或更新時間刻度 (Tick)，模擬庫存產出
function CityTradeManager:UpdateProduction()
    for cityName, cityData in pairs(self.Cities) do
        for itemName, itemData in pairs(cityData.inventory) do
            itemData.amount = itemData.amount + itemData.productionRate
            -- 加上最大庫存限制，避免無限增長
            if itemData.amount > 5000 then
                itemData.amount = 5000
            end
        end
    end
end

-- 玩家購買貨物 (扣除城市庫存)
function CityTradeManager:BuyItem(cityName, itemName, amount)
    local city = self.Cities[cityName]
    if not city then return false, "城市不存在" end
    
    local item = city.inventory[itemName]
    if not item then return false, "此城市不產該貨物" end
    
    if item.amount < amount then
        return false, "庫存不足"
    end
    
    item.amount = item.amount - amount
    return true, item.currentPrice * amount
end

-- 玩家出售貨物 (增加城市庫存)
function CityTradeManager:SellItem(cityName, itemName, amount)
    local city = self.Cities[cityName]
    if not city then return false, "城市不存在" end
    
    local item = city.inventory[itemName]
    if not item then
        -- 如果城市沒有該貨物，則新建紀錄
        -- 這裡可以動態計算基礎價格或設定一個外來貨物預設價格
        city.inventory[itemName] = { basePrice = 20, currentPrice = 20, amount = amount, productionRate = 0 }
    else
        item.amount = item.amount + amount
    end
    
    return true
end

return CityTradeManager
