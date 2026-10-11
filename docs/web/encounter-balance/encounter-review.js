(function () {
  'use strict';
  const data = JSON.parse(document.getElementById('balance-data').textContent);
  const $ = id => document.getElementById(id);
  const names = { low: '低難度', mid: '中難度', high: '高難度' };
  const pct = n => (n * 100).toFixed(1) + '%';
  const num = n => n.toLocaleString('zh-TW', { maximumFractionDigits: 2 });
  const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let prepared;
  let sampleIndex = 1;
  const rng = GVEncounter.seededRandom(20261011);
  function levelLabel(m) {
    const source = m.originalLevel !== null ? '來源 Lv.' + m.originalLevel
      : m.referenceLevel !== null ? '對照版 Lv.' + m.referenceLevel : '來源等級待查';
    return source + (m.balanceOverride ? ' · 自訂分級 Lv.' + m.balanceOverride.level + '（比照泡泡魚）' : '');
  }
  function areaName(id) { return id === '__allair' ? '全空域' : data.areas.find(a => a.id === id).name; }
  $('area').innerHTML = data.areas.map(a => '<option value="' + a.id + '">' + escape(a.name) + '</option>').join('');
  for (const id of ['card1', 'card2', 'card3']) $('' + id).innerHTML = '<option value="">空槽</option>' + data.cards.map(c => '<option value="' + c.id + '">' + escape(c.name) + '</option>').join('');
  $('curve').innerHTML = data.ships.map(s => {
    const profile = data.combatProfiles.find(p => p.tier === s.tier);
    return '<tr><td>T' + s.tier + '</td><td>' + (s.tier === 5 ? '完整池' : 'Lv.' + s.maxLevel) + '</td><td>' + s.weights.map(pct).join(' / ') + '</td><td>' + pct(s.chance) + '</td><td>' + s.count.join('～') + '</td><td>' + s.onScreen + '</td><td>' + num(profile.maxHull) + '／' + num(profile.maxShield) + '／' + num(profile.maxArmor) + '</td><td>' + num(profile.cannonDamage) + '／' + num(profile.cannonInterval) + 's</td></tr>';
  }).join('');
  $('snapshotDate').textContent = data.classificationExportedAt;
  function input() {
    return { tier: Number($('tier').value), area: $('area').value,
      cargoValue: Number($('cargoValue').value), temptation: Number($('temptation').value),
      cards: ['card1', 'card2', 'card3'].map(id => $(id).value), fogActive: $('fog').checked };
  }
  function update() {
    try {
      const values = input();
      prepared = GVEncounter.prepare(data, values);
      const p = prepared;
      $('temptationValue').textContent = values.temptation + ' / 100';
      $('sample').disabled = $('many').disabled = !p.probabilities.length;
      $('results').innerHTML = '<div class="metrics"><div class="metric"><strong>' + pct(p.chance) + '</strong><span>每次檢查遇敵率</span></div><div class="metric"><strong>' + p.minimum + '～' + p.maximum + '</strong><span>遇敵時總隻數</span></div><div class="metric"><strong>' + num(p.expectedCount) + '</strong><span>每次檢查期望隻數（含沒遇敵）</span></div></div><div class="bar" aria-label="難度權重">' + ['low', 'mid', 'high'].map(b => '<div class="' + b + '" style="width:' + (p.difficulty[b] * 100) + '%"></div>').join('') + '</div><div class="legend">' + ['low', 'mid', 'high'].map(b => '<span><i class="' + b + '"></i>' + names[b] + ' ' + pct(p.difficulty[b]) + '</span>').join('') + '</div><p class="quiet">船上貨物估值 ' + num(p.cargoValue) + ' G · 硬上限 ' + (p.tier === 5 ? '完整池' : 'Lv.' + p.maxLevel) + ' · 同屏 ' + p.onScreen + ' 隻，其餘排隊</p>' + (p.warning ? '<p>' + escape(p.warning) + '</p>' : '');
      const visible = data.monsters.filter(m => m.area === values.area || m.area === '__allair');
      $('poolCount').textContent = p.probabilities.length + ' 種可抽／' + visible.length + ' 種候選（含共用）';
      $('pool').innerHTML = visible.map(m => {
        const chance = p.probabilities.find(x => x.packId === m.packId);
        const reason = !m.enabled ? m.reviewReason : !chance ? '超過船級上限或這個船級尚未開放該難度' : '';
        const level = levelLabel(m);
        return '<article class="monster' + (!chance ? ' blocked' : '') + '"><img src="' + escape(m.thumbnail) + '" alt="' + escape(m.name) + '" loading="lazy"><div><h3>' + escape(m.name) + '</h3><p>' + escape(areaName(m.area)) + ' · ' + level + '</p><p><span class="tag">' + names[m.band] + '</span>' + ({ wildlife: '野生', magic: '魔法', neutral: '一般' }[m.family]) + '</p><p>HP ' + num(m.hp) + '／攻擊 ' + num(m.attack) + '／間隔 ' + num(m.attackInterval) + 's／賞金 ' + num(m.bounty) + ' G</p><p class="prob">' + (chance ? pct(chance.probability) + '（遇敵後單隻抽選）' : '0% · ' + escape(reason)) + '</p><a href="' + escape(m.sourceUrl) + '" target="_blank" rel="noreferrer">原作來源</a></div></article>';
      }).join('');
      $('sampleResult').textContent = '';
    } catch (error) {
      prepared = null;
      $('sample').disabled = $('many').disabled = true;
      $('results').innerHTML = '<p class="error" role="alert">' + escape(error.message) + '</p>';
      $('pool').replaceChildren();
      $('poolCount').textContent = '條件無效，請修正後再抽樣';
      $('sampleResult').textContent = '';
    }
  }
  for (const id of ['tier', 'area', 'cargoValue', 'temptation', 'fog', 'card1', 'card2', 'card3']) $(id).addEventListener('input', update);
  $('sample').addEventListener('click', () => {
    if (!prepared) return;
    const wave = GVEncounter.sample(prepared, rng);
    $('sampleResult').innerHTML = '<p>第 ' + sampleIndex++ + ' 次抽樣：' + (wave.total ? '共 ' + wave.total + ' 隻' : '平安通過') + '</p>' + (wave.total ? '<p>同屏出戰</p><div class="wave">' + wave.active.map(m => '<span>' + escape(m.name) + '</span>').join('') + '</div><p>排隊 ' + wave.queued.length + ' 隻</p><div class="wave queue">' + wave.queued.map(m => '<span>' + escape(m.name) + '</span>').join('') + '</div>' : '');
  });
  $('many').addEventListener('click', () => {
    if (!prepared) return;
    const random = GVEncounter.seededRandom(20261011);
    let battles = 0, count = 0;
    const observed = { low: 0, mid: 0, high: 0 };
    for (let i = 0; i < 10000; i++) {
      const wave = GVEncounter.sample(prepared, random);
      if (wave.total) battles++;
      count += wave.total;
      for (const m of [...wave.active, ...wave.queued]) observed[m.band]++;
    }
    $('sampleResult').textContent = '10,000 次抽樣：遇敵 ' + pct(battles / 10000) + '、每次平均 ' + num(count / 10000) + ' 隻；低／中／高隻數 ' + observed.low + '／' + observed.mid + '／' + observed.high + '。這是隨機模擬，並非 Maker 戰鬥。';
  });
  $('inventory').innerHTML = data.areas.concat([{ id: '__allair', name: '全空域' }]).map(a => '<h3>' + escape(a.name) + '</h3><p>' + data.monsters.filter(m => m.area === a.id).sort((a, b) => (a.balanceOverride?.level ?? a.originalLevel ?? a.referenceLevel ?? 999) - (b.balanceOverride?.level ?? b.originalLevel ?? b.referenceLevel ?? 999)).map(m => escape(m.name) + '［' + names[m.band] + '／' + levelLabel(m) + (!m.enabled ? '／待校準' : '') + '］').join('、') + '</p>').join('');
  update();
})();
