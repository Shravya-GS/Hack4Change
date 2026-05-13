// ===================== STATE =====================
const PROFILE = {
  salary: 85000, savingsPct: 0.5, dailyLimit: 2800,
  emergencyTarget: 255000, emergencyCurrent: 76500,
  budgets: [
    { id:'dining',     name:'Dining',      limit:6600,     spent:4200, icon:'fa-utensils',       color:'#f59e0b' },
    { id:'groceries',  name:'Groceries',   limit:5000,     spent:3100, icon:'fa-basket-shopping', color:'#10b981' },
    { id:'shopping',   name:'Shopping',    limit:3000,     spent:1500, icon:'fa-bag-shopping',    color:'#6366f1' },
    { id:'transport',  name:'Transport',   limit:4000,     spent:900,  icon:'fa-car',             color:'#3b82f6' },
    { id:'medical',    name:'Medical',     limit:Infinity, spent:800,  icon:'fa-kit-medical',     color:'#ef4444' },
    { id:'subs',       name:'Subscriptions',limit:1500,   spent:499,  icon:'fa-tv',              color:'#a855f7' },
  ]
};

let state = {
  savingsLocked: 0, spendable: 0, dailySpent: 0,
  healthScore: 75, txList: [], smsFeed: [],
  budgets: JSON.parse(JSON.stringify(PROFILE.budgets)),
  gpsActive: false, location: null
};

// ===================== HELPERS =====================
const $ = id => document.getElementById(id);
const fmt = n => '₹' + Number(n).toLocaleString('en-IN');

function calcHealthScore() {
  let score = 100;
  const over = state.budgets.filter(b => b.limit !== Infinity && b.spent > b.limit).length;
  if (over >= 2) score -= 25; else if (over === 1) score -= 10;
  if (state.dailySpent > PROFILE.dailyLimit) score -= 20;
  const efRatio = PROFILE.emergencyCurrent / PROFILE.emergencyTarget;
  if (efRatio < 0.5) score -= 15; else if (efRatio < 1) score -= 7;
  if (state.savingsLocked === 0) score -= 30;
  return Math.max(0, Math.min(100, score));
}

function scoreLabel(s) {
  if (s >= 80) return ['Low Risk 🟢', 'Your finances are stable', '#10b981'];
  if (s >= 60) return ['Medium Risk 🟡', 'A few categories need attention', '#f59e0b'];
  if (s >= 40) return ['High Risk 🟠', 'Multiple overspends detected', '#f97316'];
  return ['Critical Risk 🔴', 'Immediate intervention needed', '#ef4444'];
}

// ===================== RENDER =====================
function render() {
  state.healthScore = calcHealthScore();
  renderHealthRing();
  renderDailyCard();
  renderFinCards();
  renderBudgets();
  renderTxList();
  renderInsights();
  updateTime();
}

function renderHealthRing() {
  const s = state.healthScore;
  const [label, sub, color] = scoreLabel(s);
  const circumference = 314;
  const offset = circumference - (s / 100) * circumference;
  const ring = $('ring-progress');
  ring.style.strokeDashoffset = offset;
  ring.style.stroke = color;
  $('ring-score').textContent = s;
  $('health-status-text').textContent = label;
  $('health-status-text').style.color = color;
  $('health-sub').textContent = sub;
  const dailyOk = state.dailySpent <= PROFILE.dailyLimit;
  $('hf-daily-dot').className = 'hf-dot ' + (dailyOk ? 'green' : 'red');
  $('hf-daily-text').textContent = 'Daily Limit: ' + (dailyOk ? 'OK' : 'Exceeded');
}

function renderDailyCard() {
  const pct = Math.min((state.dailySpent / PROFILE.dailyLimit) * 100, 100);
  const rem = PROFILE.dailyLimit - state.dailySpent;
  $('daily-spent-display').textContent = fmt(state.dailySpent);
  $('daily-bar').style.width = pct + '%';
  $('daily-bar').className = 'daily-bar ' + (pct >= 100 ? 'danger' : pct > 75 ? 'warning' : 'safe');
  if (pct < 100) {
    $('daily-safe-msg').innerHTML = '<i class="fas fa-shield-halved"></i> Silent Mode Active';
    $('daily-safe-msg').className = 'daily-msg safe-msg';
    $('daily-remaining').textContent = fmt(Math.max(rem, 0)) + ' left';
  } else {
    $('daily-safe-msg').innerHTML = '<i class="fas fa-bell"></i> Daily Limit Exceeded';
    $('daily-safe-msg').className = 'daily-msg danger-msg';
    $('daily-remaining').textContent = fmt(Math.abs(rem)) + ' over';
  }
}

function renderFinCards() {
  $('card-savings').textContent = fmt(state.savingsLocked);
  $('card-spendable').textContent = fmt(state.spendable);
  const efPct = Math.round((PROFILE.emergencyCurrent / PROFILE.emergencyTarget) * 100);
  $('emerg-pct').textContent = efPct + '%';
  $('emerg-bar').style.width = efPct + '%';
  $('emerg-bar').className = 'daily-bar ' + (efPct >= 100 ? 'safe' : efPct > 50 ? 'warning' : 'danger');
  $('emerg-sub').textContent = fmt(PROFILE.emergencyCurrent) + ' of ' + fmt(PROFILE.emergencyTarget) + ' target';
}

function renderBudgets() {
  const el = $('budget-list');
  el.innerHTML = '';
  state.budgets.forEach(b => {
    const isInf = b.limit === Infinity;
    const pct = isInf ? 0 : Math.min((b.spent / b.limit) * 100, 100);
    const overClass = (!isInf && b.spent > b.limit) ? 'over-cap' : '';
    const barClass = pct >= 100 ? 'danger' : pct > 80 ? 'warning' : 'safe';
    el.innerHTML += `
      <div class="budget-item">
        <div class="budget-row">
          <span class="budget-name">
            <span class="budget-icon" style="background:${b.color}22;color:${b.color}"><i class="fas ${b.icon}"></i></span>
            ${b.name}
          </span>
          <span class="budget-amounts ${overClass}">
            ${fmt(b.spent)} / ${isInf ? 'No Cap' : fmt(b.limit)}
          </span>
        </div>
        <div class="daily-bar-bg"><div class="daily-bar ${barClass}" style="width:${pct}%"></div></div>
      </div>`;
  });
}

function renderTxList() {
  const el = $('tx-list');
  if (!state.txList.length) { el.innerHTML = '<div class="tx-empty">No transactions yet. Use the <i class="fas fa-sliders"></i> simulator.</div>'; return; }
  el.innerHTML = state.txList.slice(0, 8).map(tx => `
    <div class="tx-item">
      <div class="tx-left">
        <h5>${tx.merchant}</h5>
        <p>${tx.date} · ${tx.category}</p>
      </div>
      <div>
        <span class="tx-amount ${tx.type}">${tx.type === 'credit' ? '+' : '-'}${fmt(tx.amount)}</span>
        ${tx.alerted ? '<span class="tx-badge badge-alert">⚠ Alert</span>' : '<span class="tx-badge badge-silent">✓ Silent</span>'}
      </div>
    </div>`).join('');
}

function renderInsights() {
  const el = $('insights-content');
  const overCats = state.budgets.filter(b => b.limit !== Infinity && b.spent > b.limit);
  const savPct = state.savingsLocked > 0 ? 50 : 0;
  const totalSpent = state.budgets.reduce((s, b) => s + b.spent, 0);
  el.innerHTML = `
    <div class="insight-card ${savPct >= 50 ? 'good' : 'bad'}">
      <h4>💰 Savings Rate</h4>
      <p>${savPct >= 50 ? `${fmt(state.savingsLocked)} locked (50%). Excellent discipline — keep it up.` : 'No salary credited yet. Credit salary to auto-lock 50% into savings.'}</p>
    </div>
    <div class="insight-card ${overCats.length === 0 ? 'good' : 'warn'}">
      <h4>📊 Budget Adherence</h4>
      <p>${overCats.length === 0 ? 'All categories within limits. Great spending control!' : `${overCats.map(c => c.name).join(', ')} ${overCats.length > 1 ? 'are' : 'is'} over budget. Review these categories.`}</p>
    </div>
    <div class="insight-card ${state.dailySpent <= PROFILE.dailyLimit ? 'good' : 'bad'}">
      <h4>📅 Daily Limit</h4>
      <p>${state.dailySpent <= PROFILE.dailyLimit ? `${fmt(state.dailySpent)} spent today — within the ₹2,800 limit.` : `₹${state.dailySpent - PROFILE.dailyLimit} over daily limit. Reduce tomorrow's spend to compensate.`}</p>
    </div>
    <div class="insight-card warn">
      <h4>🛡 Emergency Fund</h4>
      <p>${fmt(PROFILE.emergencyCurrent)} saved of ${fmt(PROFILE.emergencyTarget)} target (3 months expenses). ${PROFILE.emergencyCurrent < PROFILE.emergencyTarget ? 'Try adding ₹5,000/month to accelerate this.' : 'Target met!'}</p>
    </div>
    <div class="insight-card">
      <h4>🏆 Health Score: ${state.healthScore}/100</h4>
      <p>${scoreLabel(state.healthScore)[0]} — ${scoreLabel(state.healthScore)[1]}. Total monthly spend tracked: ${fmt(totalSpent)}.</p>
    </div>`;
}

function updateTime() {
  const now = new Date();
  $('live-time').textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  const h = now.getHours();
  const greeting = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
  $('dash-greeting').textContent = greeting;
}

// ===================== TOAST NOTIFICATIONS =====================
function showToast(title, body, type = '') {
  const icons = { warn: 'fa-triangle-exclamation', danger: 'fa-bell', success: 'fa-shield-halved', '': 'fa-info-circle' };
  const id = 'toast-' + Date.now();
  const div = document.createElement('div');
  div.className = `toast ${type}`; div.id = id;
  div.innerHTML = `<div class="toast-head"><i class="fas ${icons[type] || icons['']}"></i><span class="toast-title">${title}</span></div><div class="toast-body">${body}</div>`;
  $('toast-area').prepend(div);
  setTimeout(() => { div.style.animation = 'toastOut 0.4s forwards'; setTimeout(() => div.remove(), 400); }, 6000);
}

// ===================== AI RULES =====================

// Rule 1 & 2: Transaction Processing
function processTransaction(merchant, amount, category, type = 'debit') {
  const prevDaily = state.dailySpent;
  if (type === 'debit') {
    state.dailySpent += amount;
    const bud = state.budgets.find(b => b.id === category.toLowerCase() || b.name.toLowerCase() === category.toLowerCase());
    if (bud) bud.spent += amount;
  }

  const alerted = type === 'debit' && state.dailySpent > PROFILE.dailyLimit && prevDaily <= PROFILE.dailyLimit;
  const overBy = state.dailySpent - PROFILE.dailyLimit;

  state.txList.unshift({ merchant, amount, category, type, date: 'Just now', alerted });
  render();

  if (type === 'credit') return;

  // Rule 1: Silent
  if (state.dailySpent <= PROFILE.dailyLimit) {
    console.log(`[SILENT] ₹${amount} at ${merchant} — under daily limit`);
    return;
  }

  // Rule 2: Alert
  if (alerted) {
    let msg = `You've crossed your ₹2,800 daily limit. Extra ${fmt(overBy)} spent at ${merchant}.`;
    if (category === 'Medical') {
      msg = `Medical expenses are priority — health comes first. Daily limit exceeded by ${fmt(overBy)}. No action needed, logged for monthly review.`;
      showToast('Medical Expense Logged', msg, 'success');
    } else if (category === 'Dining') {
      msg = `Crossed daily limit at ${merchant}. The extra ${fmt(overBy)} could go toward your emergency fund. Consider skipping extras.`;
      showToast('Daily Limit Exceeded', msg, 'danger');
    } else if (category === 'Shopping') {
      msg = `Hit daily cap at ${merchant}. Review your cart — ${fmt(overBy)} over limit today.`;
      showToast('Daily Limit Exceeded', msg, 'warn');
    } else {
      showToast('Daily Limit Exceeded', msg, 'danger');
    }
  }
}

// Rule 3: Geo-fence Modal
function showGeoFenceAlert(zoneType, name) {
  const catMap = { restaurant: 'dining', mall: 'shopping', cafe: 'dining' };
  const catId = catMap[zoneType] || 'shopping';
  const bud = state.budgets.find(b => b.id === catId);
  const remaining = bud && bud.limit !== Infinity ? bud.limit - bud.spent : 9999;
  const pct = bud && bud.limit !== Infinity ? Math.min((bud.spent / bud.limit) * 100, 100) : 0;

  let body = '';
  const iconMap = { restaurant: 'fa-utensils', mall: 'fa-bag-shopping', cafe: 'fa-mug-hot' };
  $('geo-modal-icon').innerHTML = `<i class="fas ${iconMap[zoneType] || 'fa-location-dot'}"></i>`;
  $('geo-modal-title').textContent = `Entered: ${name}`;

  if (remaining <= 0) {
    body = `⚠️ Your ${bud.name} budget is already ${fmt(Math.abs(remaining))} over limit. If you must spend here, keep it minimal.`;
    $('geo-bar-fill').className = 'geo-bar-fill danger';
  } else {
    body = zoneType === 'mall'
      ? `Your shopping budget has ${fmt(remaining)} left this month. A soft-cap has been applied to your UPI for the next 2 hours.`
      : `Your ${bud ? bud.name : 'dining'} budget has ${fmt(remaining)} remaining. Look at the menu carefully before ordering.`;
    $('geo-bar-fill').className = 'geo-bar-fill ' + (pct > 80 ? 'warning' : 'safe');
  }

  $('geo-modal-body').textContent = body;
  $('geo-bar-fill').style.width = pct + '%';
  $('geo-budget-text').textContent = fmt(Math.max(remaining, 0)) + ' left';
  $('geo-soft-cap-text').textContent = zoneType === 'mall' ? '₹1,200 soft-cap applied for 2 hrs' : '₹800 soft-cap applied for 2 hrs';
  $('geo-modal').classList.remove('hidden');
}

// Rule 4: Critical Zone Alert
function triggerCriticalAlert(venueName, time) {
  const dinBud = state.budgets.find(b => b.id === 'dining');
  const spent = dinBud ? dinBud.spent : 0;
  const cap = dinBud ? dinBud.limit : 6600;
  const overAmt = Math.max(spent - cap, 0);

  const msg = `You've just entered ${venueName} at ${time}.

This is a high-risk zone — not just financially, but for your health and the decisions you'll make in the next few hours.

Your financial snapshot right now:
• This month's dining/nightlife: ${fmt(spent)} spent vs ${fmt(cap)} cap
${overAmt > 0 ? `• You're ${fmt(overAmt)} over your category limit` : '• Within dining category limit ✓'}
• Monthly savings protected: ${fmt(state.savingsLocked)} ✓

The money is one thing. But the bigger risk is the environment — peer pressure, substances, and decisions that feel fine at ${time} and terrible in the morning.

You set these alerts because you care about your future self.

Your future self is watching.`;

  $('critical-body').textContent = msg;
  $('critical-overlay').classList.remove('hidden');

  if (navigator.vibrate) navigator.vibrate([500, 200, 500, 200, 500]);
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [440, 550, 660].forEach((freq, i) => {
      const osc = ctx.createOscillator(); osc.frequency.value = freq;
      osc.connect(ctx.destination); osc.start(i * 0.3); osc.stop(i * 0.3 + 0.2);
    });
  } catch (e) {}
}

// Rule 5: Salary Credit
function creditSalary() {
  const gross = PROFILE.salary;
  const locked = gross * PROFILE.savingsPct;
  const spendable = gross - locked;
  state.savingsLocked += locked;
  state.spendable = spendable;
  state.dailySpent = 0;
  state.budgets = JSON.parse(JSON.stringify(PROFILE.budgets));
  state.txList.unshift({ merchant: 'HDFC Bank — Salary', amount: gross, category: 'Salary', type: 'credit', date: 'Today', alerted: false });

  $('salary-locked').textContent = fmt(locked);
  $('salary-spendable').textContent = fmt(spendable);
  $('salary-credit-amount').textContent = fmt(gross) + ' Credited';
  launchConfetti();
  $('salary-overlay').classList.remove('hidden');
  render();
}

function launchConfetti() {
  const wrap = $('confetti-wrap');
  wrap.innerHTML = '';
  const colors = ['#10b981','#6366f1','#f59e0b','#ef4444','#3b82f6'];
  for (let i = 0; i < 40; i++) {
    const c = document.createElement('div');
    const size = Math.random() * 8 + 4;
    Object.assign(c.style, {
      position: 'absolute', width: size + 'px', height: size + 'px',
      background: colors[Math.floor(Math.random() * colors.length)],
      borderRadius: Math.random() > 0.5 ? '50%' : '2px',
      left: Math.random() * 100 + '%', top: '-10px',
      animation: `confettiFall ${1 + Math.random() * 2}s ${Math.random()}s ease-in forwards`,
      transform: `rotate(${Math.random() * 360}deg)`
    });
    wrap.appendChild(c);
  }
}

// ===================== GPS / GEOLOCATION =====================
function initGPS() {
  if (!navigator.geolocation) { showToast('GPS Unavailable', 'Your browser does not support geolocation.', 'warn'); return; }
  $('btn-gps-enable').textContent = 'Locating…';
  navigator.geolocation.watchPosition(pos => {
    state.gpsActive = true;
    state.location = { lat: pos.coords.latitude, lng: pos.coords.longitude };
    $('sb-gps-icon').classList.add('active');
    $('gps-status-text').textContent = 'Location: Active';
    $('gps-location-text').textContent = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
    $('btn-gps-enable').textContent = 'Active ✓';
    $('btn-gps-enable').disabled = true;
    showToast('GPS Active', 'Location tracking enabled. Geo-fence alerts are now live.', 'success');
  }, err => {
    showToast('GPS Error', 'Could not get location: ' + err.message, 'warn');
    $('btn-gps-enable').textContent = 'Retry';
  }, { enableHighAccuracy: true, maximumAge: 30000 });
}

// ===================== SMS PARSER =====================
function parseSMS(raw) {
  const amtMatch = raw.match(/(?:INR|Rs\.?|₹)\s*([\d,]+\.?\d*)/i);
  const amount = amtMatch ? parseFloat(amtMatch[1].replace(/,/g, '')) : null;
  const isDebit = /debited|deducted|spent|paid|sent|purchase/i.test(raw);
  const isCredit = /credited|received|salary|refund/i.test(raw);
  const type = isCredit ? 'CREDIT' : isDebit ? 'DEBIT' : 'UNKNOWN';

  const merchantMatch = raw.match(/(?:at|to|via|INFO:|UPI-|Merchant:)\s*([A-Z0-9 &'./-]{3,30})/i);
  const merchant = merchantMatch ? merchantMatch[1].trim() : 'Unknown Merchant';

  const catKeywords = {
    Dining: /swiggy|zomato|barbeque|restaurant|cafe|pizza|kfc|mcdonald|dominos|burger|biryani|starbucks/i,
    Groceries: /bigbasket|grofers|more|dmart|reliance fresh|grocery|supermarket/i,
    Shopping: /amazon|flipkart|myntra|nykaa|mall|fashion|retail/i,
    Transport: /uber|ola|rapido|metro|irctc|bus|auto/i,
    Medical: /apollo|medplus|pharma|hospital|clinic|doctor|lab/i,
    Salary: /salary|payroll|credited.*employer/i,
    Subscriptions: /netflix|spotify|hotstar|prime|jio|airtel|subscription/i,
  };
  let category = 'Other';
  for (const [cat, regex] of Object.entries(catKeywords)) { if (regex.test(raw)) { category = cat; break; } }
  if (isCredit && /salary/i.test(raw)) category = 'Salary';

  const bankMatch = raw.match(/\b(HDFC|SBI|ICICI|AXIS|KOTAK|PAYTM|GPAY|PHONEPE)\w*/i);
  const bank = bankMatch ? bankMatch[0].toUpperCase() : 'Unknown Bank';

  return { amount, type, merchant, category, bank, raw };
}

function handleSMSParse() {
  const raw = $('sms-input').value.trim();
  if (!raw) { showToast('Empty SMS', 'Please paste a bank SMS first.', 'warn'); return; }
  const p = parseSMS(raw);
  const resultEl = $('sms-result');
  resultEl.classList.remove('hidden', 'alert-result');

  if (!p.amount) {
    resultEl.innerHTML = `<pre>⚠ Could not detect transaction amount in this SMS.\n\nTry pasting a message like:\n"Your HDFC Bank account has been debited with INR 850.00. Info: SWIGGY"</pre>`;
    resultEl.classList.add('alert-result');
    return;
  }

  resultEl.innerHTML = `<pre>✅ Parsed Successfully\n\n  Amount  : ₹${p.amount}\n  Type    : ${p.type}\n  Merchant: ${p.merchant}\n  Category: ${p.category}\n  Bank    : ${p.bank}</pre>`;

  if (p.type === 'DEBIT' && p.amount) {
    processTransaction(p.merchant, p.amount, p.category);
    state.smsFeed.unshift(p);
    renderSMSFeed();
  } else if (p.type === 'CREDIT' && /salary/i.test(raw) && p.amount >= PROFILE.salary * 0.5) {
    creditSalary();
  }
  $('sms-input').value = '';
}

function renderSMSFeed() {
  const el = $('sms-feed');
  if (!state.smsFeed.length) { el.innerHTML = '<div class="tx-empty">No SMS parsed yet</div>'; return; }
  el.innerHTML = state.smsFeed.slice(0, 10).map(p => `
    <div class="sms-feed-item">
      <div class="sms-feed-header">
        <span class="sms-feed-merchant">${p.merchant} · ${p.category}</span>
        <span class="sms-feed-amount">-₹${p.amount}</span>
      </div>
      <div class="sms-feed-meta">${p.bank} · ${p.type}</div>
    </div>`).join('');
}

// ===================== NAV TABS =====================
document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    tab.classList.add('active');
    $('view-' + tab.dataset.view).classList.add('active');
  });
});

// ===================== SIMULATOR =====================
$('sim-toggle-btn').addEventListener('click', () => $('sim-panel').classList.remove('hidden'));
$('sim-close-btn').addEventListener('click', () => $('sim-panel').classList.add('hidden'));
$('sim-salary').addEventListener('click', creditSalary);
$('sim-reset').addEventListener('click', () => {
  state = { savingsLocked:0, spendable:0, dailySpent:0, healthScore:75, txList:[], smsFeed:[], budgets:JSON.parse(JSON.stringify(PROFILE.budgets)), gpsActive:false, location:null };
  render(); renderSMSFeed(); $('sim-panel').classList.add('hidden');
});
$('sim-safe-500').addEventListener('click', () => processTransaction('Uber', 500, 'transport'));
$('sim-dining-3000').addEventListener('click', () => processTransaction('Barbeque Nation', 3000, 'dining'));
$('sim-medical-5000').addEventListener('click', () => processTransaction('Apollo Pharmacy', 5000, 'medical'));
$('sim-shopping-2000').addEventListener('click', () => processTransaction('Myntra', 2000, 'shopping'));
$('sim-grocery-1200').addEventListener('click', () => processTransaction('BigBasket', 1200, 'groceries'));
$('sim-enter-restaurant').addEventListener('click', () => { $('sim-panel').classList.add('hidden'); showGeoFenceAlert('restaurant', 'Truffles Restaurant'); });
$('sim-enter-mall').addEventListener('click', () => { $('sim-panel').classList.add('hidden'); showGeoFenceAlert('mall', 'Phoenix Marketcity'); });
$('sim-enter-cafe').addEventListener('click', () => { $('sim-panel').classList.add('hidden'); showGeoFenceAlert('cafe', 'Blue Tokai Coffee'); });
$('sim-enter-club').addEventListener('click', () => { $('sim-panel').classList.add('hidden'); triggerCriticalAlert('Neon Club & Lounge', '11:30 PM'); });
$('sim-enter-bar').addEventListener('click', () => { $('sim-panel').classList.add('hidden'); triggerCriticalAlert('The Irish Pub', '10:00 PM'); });

// ===================== MODAL CLOSE =====================
$('btn-leave-zone').addEventListener('click', () => {
  $('critical-overlay').classList.add('hidden');
  showToast('Smart Choice 🛡', 'You left the high-risk zone. Your future self thanks you.', 'success');
});
$('btn-dismiss-critical').addEventListener('click', () => $('critical-overlay').classList.add('hidden'));
$('btn-salary-ok').addEventListener('click', () => $('salary-overlay').classList.add('hidden'));
$('geo-ok').addEventListener('click', () => $('geo-modal').classList.add('hidden'));
$('btn-gps-enable').addEventListener('click', initGPS);
$('sms-parse-btn').addEventListener('click', handleSMSParse);

// ===================== CONFETTI ANIMATION =====================
const style = document.createElement('style');
style.textContent = `@keyframes confettiFall{to{transform:translateY(400px) rotate(720deg);opacity:0;}}`;
document.head.appendChild(style);

// ===================== INIT =====================
render();
setInterval(updateTime, 30000);
