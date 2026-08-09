-- PlayerInventory.lua
-- 管理玩家的金錢、貨物與船艙容量

local PlayerInventory = {}

PlayerInventory.Money = 5000
PlayerInventory.MaxCapacity = 100
PlayerInventory.CurrentCapacity = 0
PlayerInventory.Goods = {}

-- 取得目前可用的空間
function PlayerInventory:GetFreeSpace()
    return self.MaxCapacity - self.CurrentCapacity
end

-- 購買貨物並放入背包
function PlayerInventory:AddGoods(itemName, amount, cost)
    if self.Money < cost then
        return false, "資金不足"
    end
    
    if self:GetFreeSpace() < amount then
        return false, "船艙空間不足"
    end
    
    self.Money = self.Money - cost
    self.CurrentCapacity = self.CurrentCapacity + amount
    
    if not self.Goods[itemName] then
        self.Goods[itemName] = amount
    else
        self.Goods[itemName] = self.Goods[itemName] + amount
    end
    
    return true, "購買成功"
end

-- 賣出貨物
function PlayerInventory:RemoveGoods(itemName, amount, revenue)
    if not self.Goods[itemName] or self.Goods[itemName] < amount then
        return false, "貨物數量不足"
    end
    
    self.Goods[itemName] = self.Goods[itemName] - amount
    if self.Goods[itemName] == 0 then
        self.Goods[itemName] = nil
    end
    
    self.CurrentCapacity = self.CurrentCapacity - amount
    self.Money = self.Money + revenue
    
    return true, "出售成功"
end

return PlayerInventory
