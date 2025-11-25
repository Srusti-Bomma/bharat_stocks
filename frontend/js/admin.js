// Admin panel JS
// Requires js/auth.js utilities

async function requireAdmin() {
  const res = await fetch(`${API_URL}/auth/me`, { headers: { ...Auth.getAuthHeader(), 'Content-Type':'application/json' } });
  if (!res.ok) { window.location.href = 'index.html'; return null; }
  const me = await res.json();
  if (me.role !== 'admin') { window.location.href = 'index.html'; return null; }
  // Set profile identity + avatar initial (always show Admin User)
  try {
    const ident = me.full_name || 'Admin User';
    const initial = (ident.trim()[0] || 'A').toUpperCase();
    const idEl = document.getElementById('profileIdentity'); if (idEl) idEl.textContent = ident;
    const avEl = document.getElementById('avatarInitial'); if (avEl) avEl.textContent = initial;
  } catch(e) {}
  return me;
}

function humanBytes(b){ if(!b && b!==0) return 'N/A'; const u=['B','KB','MB','GB','TB']; let i=0; let n=b; while(n>=1024&&i<u.length-1){n/=1024;i++;} return `${n.toFixed(2)} ${u[i]}`; }
function fmt(n){ if(n===null||n===undefined) return 'N/A'; return typeof n==='number'? n.toLocaleString(): n; }

// Format date/time in Indian Standard Time as DD/MM/YYYY HH:MM:SS
function formatIST(iso){
  if (!iso) return '';
  // Backend sends naive timestamps (no timezone suffix). Treat them as UTC.
  const isoUtc = typeof iso === 'string' && !iso.endsWith('Z') ? `${iso}Z` : iso;
  const d = new Date(isoUtc);
  if (isNaN(d.getTime())) return '';
  // Use built-in timezone handling to convert from UTC -> IST
  const opts = {
    timeZone: 'Asia/Kolkata',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  };
  // Example output: 18/11/2025, 15:32:10 -> normalize to "DD/MM/YYYY HH:MM:SS"
  const parts = new Intl.DateTimeFormat('en-IN', opts).formatToParts(d);
  const get = (type) => parts.find(p => p.type === type)?.value || '';
  const day = get('day');
  const month = get('month');
  const year = get('year');
  const hour = get('hour');
  const minute = get('minute');
  const second = get('second');
  return `${day}/${month}/${year} ${hour}:${minute}:${second}`;
}

async function loadOverview(){
  const url = `${API_URL}/admin/overview`;
  const res = await fetch(url, { headers: Auth.getAuthHeader() });
  if(!res.ok){ console.error('overview failed'); return; }
  const d = await res.json();
  document.getElementById('ovActive').textContent = fmt(d.active_users_today);
  document.getElementById('ovReqs').textContent = fmt(d.total_requests_today);
  document.getElementById('ovAvgMs').textContent = fmt(d.avg_response_ms_today);
  document.getElementById('ovErrorRate').textContent = d.error_rate_today !== null && d.error_rate_today !== undefined ? `${d.error_rate_today}%` : 'N/A';
  document.getElementById('ovTotalSymbols').textContent = fmt(d.total_nse_stocks);
  document.getElementById('ovSnapshotsToday').textContent = fmt(d.snapshots_today);
  document.getElementById('ovExtCalls').textContent = fmt(d.external_api_calls_today);
  document.getElementById('ovQuota').textContent = d.rate_limit_pct!==null && d.rate_limit_pct!==undefined? `${d.rate_limit_pct}%` : 'N/A';
}

async function loadMostActive(){
  const wrap = document.getElementById('mostActiveWrap');
  try{
    const res = await fetch(`${API_URL}/admin/users/most-active`, { headers: Auth.getAuthHeader() });
    if(!res.ok) throw new Error('Failed');
    const list = await res.json();
    let html='';
    list.forEach(u=>{
      html += `<div class="bg-slate-900 rounded-xl p-4 border border-slate-700">
        <div class="text-white font-semibold">${u.username}</div>
        <div class="text-gray-400 text-sm">${u.email}</div>
        <div class="text-gray-300 mt-1">Sessions: <span class="font-semibold">${u.sessions}</span></div>
      </div>`;
    });
    if(!html) html = '<div class="text-gray-400">No data</div>';
    wrap.innerHTML = html;
  }catch(e){ wrap.innerHTML = '<div class="text-red-400">Failed to load</div>'; }
}

async function loadUsers() {
  const tbody = document.getElementById('usersTbody');
  tbody.innerHTML = `<tr><td colspan="8" class="px-6 py-12 text-center"><div class=\"spinner mx-auto\"></div></td></tr>`;
  try {
    const res = await fetch(`${API_URL}/auth/users`, { headers: Auth.getAuthHeader() });
    if (!res.ok) throw new Error('Failed to load users');
    const users = await res.json();
    const roleFilter = document.getElementById('roleFilter').value;
    const filtered = roleFilter==='all' ? users : users.filter(u=>u.role===roleFilter);

    let html = '';
    filtered.forEach(u=>{
      const status = u.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>';
      const created = u.created_at ? formatIST(u.created_at) : '—';
      const lastLoginOut2 = u.last_login ? formatIST(u.last_login) : 'Never';
      html += `
        <tr class="border-t border-slate-700">
          <td class="px-6 py-3 text-gray-300">${u.id}</td>
          <td class="px-6 py-3 text-white">${u.username}</td>
          <td class="px-6 py-3 text-gray-300">${u.email}</td>
          <td class="px-6 py-3 text-gray-300">${u.role}</td>
          <td class="px-6 py-3">${status}</td>
          <td class="px-6 py-3 text-gray-300">${created}</td>
          <td class="px-6 py-3 text-gray-300">${lastLoginOut2}</td>
          <td class="px-6 py-3 text-right">
            <button class="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-white" onclick="toggleActive(${u.id}, ${u.is_active})">${u.is_active?'Deactivate':'Activate'}</button>
          </td>
        </tr>`;
    });
    if (!html) html = '<tr><td colspan="8" class="px-6 py-8 text-center text-gray-400">No users</td></tr>';
    tbody.innerHTML = html;
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan=\"8\" class=\"px-6 py-8 text-center text-red-400\">${e.message}</td></tr>`;
  }
}

async function toggleActive(userId, isActive) {
  const url = `${API_URL}/auth/users/${userId}/${isActive?'deactivate':'activate'}`;
  const res = await fetch(url, { method: 'PATCH', headers: Auth.getAuthHeader() });
  if (!res.ok) {
    const j = await res.json().catch(()=>({detail:'Failed'}));
    alert(j.detail||'Failed');
    return;
  }
  loadUsers();
}

// Init
(async () => {
  const me = await requireAdmin();
  if (!me) return;
  // Init profile dropdown interactions
  try {
    const btn = document.getElementById('profileBtn');
    const menu = document.getElementById('profileMenu');
    const container = document.getElementById('profileContainer');
    btn && btn.addEventListener('click', (e)=>{ e.stopPropagation(); menu && menu.classList.toggle('hidden'); });
    document.addEventListener('click', (e)=>{ if(container && !container.contains(e.target)) { menu && menu.classList.add('hidden'); } });
    document.addEventListener('keydown', (e)=>{ if(e.key==='Escape'){ menu && menu.classList.add('hidden'); } });
    const lo = document.getElementById('logoutBtn'); lo && lo.addEventListener('click', ()=> Auth.logout());
  } catch(e) {}
  document.getElementById('refreshBtn').addEventListener('click', loadUsers);
  document.getElementById('roleFilter').addEventListener('change', loadUsers);
  const overviewRefreshBtn = document.getElementById('overviewRefresh');
  if (overviewRefreshBtn) {
    overviewRefreshBtn.addEventListener('click', () => { loadOverview(); loadMostActive(); });
  }
  await loadOverview();
  await loadMostActive();
  // Auto-refresh KPI cards every 5 seconds
  setInterval(loadOverview, 5000);
  loadUsers();
})();
