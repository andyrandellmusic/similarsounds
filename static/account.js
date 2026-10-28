/* SimilarSounds accounts (optional): log in with email + password to keep your set and recent
 * searches on every device. Accounts, passwords and emails are handled by Supabase Auth
 * (passwords are never seen or stored by SimilarSounds). Everything works without logging in.
 */
(async function () {
  const $ = s => document.querySelector(s);
  // Searches wait for this, so a logged-in visitor's first search is counted against their account
  let authReady;
  window.ssAuthReady = new Promise(r => { authReady = r; });
  let cfg;
  try { cfg = await (await fetch("/api/config")).json(); } catch { authReady(); return; }
  window.ssSubsOn = !!cfg.subscriptions; window.dispatchEvent(new Event("ss:subs"));   // SimilarSounds Unlimited open yet?
  if (!cfg.supabase_url || !cfg.supabase_anon_key) { authReady(); return; }   // accounts not switched on yet

  await new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.0/dist/umd/supabase.min.js";
    s.onload = ok; s.onerror = fail; document.head.appendChild(s);
  }).catch(() => null);
  if (!window.supabase?.createClient) { authReady(); return; }
  const sb = window.supabase.createClient(cfg.supabase_url, cfg.supabase_anon_key, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: "implicit" },
  });

  let user = null, syncing = false, saveTimer = null;
  document.documentElement.classList.add("accounts-on");
  const say = msg => window.toast ? toast(msg) : null;
  const read = k => { try { return JSON.parse(localStorage.getItem(k) || "[]"); } catch { return []; } };
  const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

  /* ---------- dialog */
  const dlg = $("#acct"), box = $("#acct-box");
  let opener = null;
  function open(view) {
    opener = document.activeElement;
    view = view || (user ? "account" : "login");
    show(view);
    dlg.hidden = false;
    setTimeout(() => box.querySelector("input:not([hidden]), button.primary")?.focus(), 30);
    if (view === "login") { paintQuick(); if (!(pkSupported && pkHere())) offerSaved(); }
  }
  /* ---------- Face ID sign-in (passkeys), optional.
   * After logging in with a password, people are asked once whether they'd like to use Face ID /
   * Touch ID / fingerprint next time. If they say yes, their phone creates a passkey (kept by the phone,
   * e.g. in iCloud Keychain; SimilarSounds only gets a public key). Next time the Log in screen shows
   * "Sign in as <name>": one tap + Face ID. They can turn it off any time in their account. */
  const PK = "ss_passkey", PK_NO = "ss_passkey_no", LAST = "ss_last_login";
  let pkSupported = false;   // true once we know this browser can do it and it's switched on in Supabase
  if (window.PublicKeyCredential && typeof sb.auth.signInWithPasskey === "function") {
    setTimeout(async () => {   // after the rest of this file has set up
      let on = null;
      try { on = sessionStorage.getItem("ss_pk_on"); } catch {}
      if (on === null) {
        try {
          const r = await fetch(`${cfg.supabase_url}/auth/v1/passkeys/authentication/options`, {
            method: "POST", headers: { apikey: cfg.supabase_anon_key, "Content-Type": "application/json" }, body: "{}" });
          on = r.ok ? "1" : "0";
        } catch { on = "0"; }
        if (on === "1") { try { sessionStorage.setItem("ss_pk_on", on); } catch {} }   // only remember "on"
      }
      pkSupported = on === "1";
      paint();
      if (!dlg.hidden && !box.querySelector('[data-view="login"]').hidden) paintQuick();
    }, 0);
  }
  const getJ = k => { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch { return null; } };
  const setJ = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, JSON.stringify(v)); } catch {} };
  const rememberLogin = (email, name) => setJ(LAST, { email, name: name || "" });
  const forgetLogin = () => { setJ(LAST, null); setJ(PK, null); setJ(PK_NO, null); };
  const pkHere = () => getJ(PK);
  const pkErr = e => /NotAllowed|cancel|abort/i.test(`${e?.name} ${e?.message}`) ? "" :
    /disabled/i.test(e?.message || "") ? "Face ID sign-in isn't switched on yet. Please use your password for now." :
    "Face ID sign-in didn't work. Please try again, or use your password.";
  function paintQuick(useForm) {
    const pk = pkHere(), f = $("#f-login");
    const quick = pkSupported && !!pk?.email && !useForm;
    $("#acct-quick").hidden = !quick;
    f.hidden = quick;
    $("#pk-login").hidden = !pkSupported || quick;
    $("#quick-msg").textContent = "";
    if (quick) {
      $("#quick-name").textContent = pk.name || pk.email.split("@")[0];
      $("#quick-email").textContent = pk.email;
      setTimeout(() => $("#quick-go").focus(), 40);
    } else {
      const last = getJ(LAST);
      if (last?.email && !f.email.value) f.email.value = last.email;   // at least fill in their email
    }
  }
  async function pkSignIn(btn, where) {
    btn.disabled = true;
    let res;
    try { res = await sb.auth.signInWithPasskey(); } catch (e) { res = { error: e }; }
    btn.disabled = false;
    if (res?.error || !res?.data) {
      const m = pkErr(res?.error);
      if (where === "quick") { const q = $("#quick-msg"); q.textContent = m; q.className = "acct-msg err"; }
      else if (m) msg("login", m);
      return;
    }
    const u = res.data.user || res.data.session?.user || (await sb.auth.getUser()).data.user;
    if (u?.email) setJ(PK, { email: u.email, name: u.user_metadata?.name || "" });
    close(); say(`Signed in - welcome back${u?.user_metadata?.name ? ", " + u.user_metadata.name : ""}`);
  }
  /* ---------- "Continue with Google": one tap, no password. Shown only once Google sign-in is
   * switched on in Supabase (Authentication > Sign In / Providers > Google). */
  fetch(`${cfg.supabase_url}/auth/v1/settings`, { headers: { apikey: cfg.supabase_anon_key } })
    .then(r => r.json()).then(st => {
      if (!st?.external?.google) return;
      box.querySelectorAll("[data-google], [data-google-or]").forEach(el => el.hidden = false);
    }).catch(() => {});
  box.addEventListener("click", async e => {
    const g = e.target.closest("[data-google]"); if (!g) return;
    g.disabled = true;
    const { error } = await sb.auth.signInWithOAuth({ provider: "google", options: { redirectTo: location.origin + location.pathname + location.search } });
    if (error) { g.disabled = false; say("Couldn't connect to Google. Please try again."); }
  });
  $("#quick-go").addEventListener("click", () => pkSignIn($("#quick-go"), "quick"));
  $("#pk-login").addEventListener("click", () => pkSignIn($("#pk-login"), "form"));
  $("#quick-other").addEventListener("click", e => { e.preventDefault(); paintQuick(true); $("#f-login").password.focus(); });

  // Offer Face ID once, right after a password log-in or sign-up (unless they've said no, or it's set up here)
  function offerFaceId(email) {
    if (!pkSupported || !email) return false;
    if (pkHere()?.email === email || getJ(PK_NO) === email) return false;
    show("faceid"); dlg.hidden = false;
    setTimeout(() => $("#pk-yes").focus(), 40);
    return true;
  }
  async function turnOnFaceId(btn, view) {
    btn.disabled = true;
    let res;
    try { res = await sb.auth.registerPasskey(); } catch (e) { res = { error: e }; }
    btn.disabled = false;
    if (res?.error) { const m = pkErr(res.error); if (m) msg(view, m); return false; }
    setJ(PK, { email: user?.email, name: user?.user_metadata?.name || "" }); setJ(PK_NO, null);
    return true;
  }
  $("#pk-yes").addEventListener("click", async () => {
    if (await turnOnFaceId($("#pk-yes"), "faceid")) { close(); say("Face ID sign-in is on - next time, just tap Sign in"); }
  });
  $("#pk-no").addEventListener("click", e => {
    e.preventDefault(); setJ(PK_NO, user?.email || ""); close();
    say("No problem - you can turn on Face ID sign-in in your account any time");
  });
  // In "Your account": Face ID sign-in on / off
  async function paintPkRow() {
    const row = $("#pk-row");
    row.hidden = !pkSupported || !user;
    if (row.hidden) return;
    let list = [];
    try { const { data } = await sb.auth.passkey.list(); list = Array.isArray(data) ? data : data?.passkeys || []; } catch {}
    const on = list.length > 0;
    $("#pk-state").textContent = on ? `On · ${list.length === 1 ? "1 device" : list.length + " devices"}` : "Off · sign in with a tap instead of a password";
    const b = $("#pk-toggle");
    b.textContent = on ? "Turn off" : "Turn on";
    b.onclick = async () => {
      if (!on) { if (await turnOnFaceId(b, "account")) { msg("account", "Face ID sign-in is on", true); paintPkRow(); } return; }
      b.disabled = true;
      for (const k of list) { try { await sb.auth.passkey.delete({ passkeyId: k.id }); } catch {} }
      b.disabled = false;
      setJ(PK, null); setJ(PK_NO, user?.email || "");
      msg("account", "Face ID sign-in is off. You can also remove it from your phone in Settings > Passwords.", true);
      paintPkRow();
    };
  }
  // A password filled in by Keychain / a password manager logs in straight away (typing doesn't)
  $("#f-login").password.addEventListener("input", e => {
    const f = $("#f-login");
    const autofilled = !e.inputType || e.inputType === "insertReplacementText";
    if (autofilled && f.email.value.includes("@") && f.password.value.length >= 8) setTimeout(() => f.requestSubmit(), 150);
  });
  /* ---------- saved logins (iPhone/Mac Keychain, Chrome, password managers)
   * The forms use the standard autocomplete names, so Keychain and password managers offer to save
   * the login and fill it in with one tap. Where the browser supports it (Chrome, Edge, Android),
   * a saved login is also offered as soon as "Log in" opens: one click logs you straight in. */
  const credOK = "PasswordCredential" in window && navigator.credentials;
  async function offerSaved() {
    if (!credOK) return;
    try {
      const c = await navigator.credentials.get({ password: true, mediation: "optional" });
      if (!c || !c.password || dlg.hidden || user) return;
      const f = $("#f-login"); f.email.value = c.id; f.password.value = c.password;
      f.requestSubmit();
    } catch {}
  }
  async function saveLogin(email, password, name) {
    if (!credOK || !email || !password) return;
    try { await navigator.credentials.store(new PasswordCredential({ id: email, password, name: name || email })); } catch {}
  }
  function close() { dlg.hidden = true; opener?.focus?.(); }
  function show(view) {
    box.querySelectorAll("[data-view]").forEach(v => v.hidden = v.dataset.view !== view);
    box.querySelectorAll(".acct-msg").forEach(m => { m.textContent = ""; m.className = "acct-msg"; });
    if (view === "reset") $("#f-reset").email.value = user?.email || "";   // so Keychain updates the right login
    if (view === "account") { $("#acct-email").textContent = user?.email || ""; $("#f-name").name.value = user?.user_metadata?.name || ""; ownerStats(); paintPkRow(); }
  }
  // Private visitor numbers: only the owner account is allowed to read them (checked in Supabase)
  async function ownerStats() {
    const el = $("#acct-stats");
    el.hidden = true;
    const { data: st, error } = await sb.rpc("visitor_stats");
    if (error || !st) return;
    const n = v => Number(v || 0).toLocaleString();
    const days = (st.days || []).slice(0, 14).map(d =>
      `<tr><td>${new Date(d.day).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" })}</td><td>${n(d.visitors)}</td><td>${n(d.views)}</td></tr>`).join("");
    el.innerHTML = `<h3>Visitors (private, only you can see this)</h3>
      <div class="st-grid"><div><b>${n(st.today)}</b>today</div><div><b>${n(st.last_7_days)}</b>last 7 days</div>
      <div><b>${n(st.last_30_days)}</b>last 30 days</div><div><b>${n(st.all_time)}</b>all time</div></div>
      <p class="acct-sub">${n(st.accounts)} accounts · ${n(st.searches_used)} free searches used · 👍 ${n(st.votes_up)} / 👎 ${n(st.votes_down)}. Your own visits aren't counted.</p>
      ${days ? `<table class="st-days"><tr><th>Day</th><th>Visitors</th><th>Page views</th></tr>${days}</table>` : ""}
      <p class="acct-links"><a href="/stats">Open the full stats page (visitors and reviews) →</a></p>`;
    el.hidden = false;
  }
  function msg(view, text, ok) {
    const m = box.querySelector(`[data-view="${view}"] .acct-msg`);
    m.textContent = text; m.className = "acct-msg" + (ok ? " ok" : " err");
  }
  function busy(form, on) { form.querySelectorAll("button, input").forEach(b => b.disabled = on); }
  const friendly = e => {
    const t = (e?.message || "").toLowerCase();
    if (t.includes("invalid login")) return "That email and password don't match.";
    if (t.includes("not confirmed")) return "Please confirm your email first - check your inbox for the link.";
    if (t.includes("already registered") || t.includes("already been registered")) return "There's already an account with that email. Try logging in.";
    if (t.includes("password should be") || t.includes("weak")) return "Please use a password of at least 8 characters.";
    if (t.includes("rate limit") || t.includes("too many")) return "Too many attempts - please wait a few minutes and try again.";
    if (t.includes("valid email") || t.includes("invalid email")) return "Please enter a valid email address.";
    if (t.includes("fetch") || t.includes("network")) return "Can't reach the login service right now. Check your connection.";
    return "Something went wrong. Please try again.";
  };

  dlg.addEventListener("click", e => {
    if (e.target === dlg || e.target.closest(".acct-x")) close();
    const go = e.target.closest("[data-go]");
    if (go) { e.preventDefault(); show(go.dataset.go); box.querySelector(`[data-view="${go.dataset.go}"] input`)?.focus(); }
  });
  document.addEventListener("keydown", e => { if (!dlg.hidden && e.key === "Escape") close(); });
  document.addEventListener("click", e => {
    if (e.target.closest("[data-account]")) { e.preventDefault(); window.toggleMenu?.(false); open(); }
  });
  box.querySelectorAll(".pw-toggle").forEach(b => b.addEventListener("click", () => {
    const i = b.previousElementSibling; const showIt = i.type === "password";
    i.type = showIt ? "text" : "password"; b.textContent = showIt ? "Hide" : "Show";
    b.setAttribute("aria-pressed", showIt);
  }));

  $("#f-login").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target; busy(f, true);
    const { error } = await sb.auth.signInWithPassword({ email: f.email.value.trim(), password: f.password.value });
    busy(f, false);
    if (error) return msg("login", friendly(error));
    saveLogin(f.email.value.trim(), f.password.value);
    if (!offerFaceId(f.email.value.trim())) close();
    say("Signed in - your set is saved to your account");
    setTimeout(() => f.reset(), 3000);   // clear later, so Safari has the details for "Save Password?"
  });
  $("#f-signup").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target;
    if (f.password.value.length < 8) return msg("signup", "Please use a password of at least 8 characters.");
    busy(f, true);
    const { data, error } = await sb.auth.signUp({ email: f.email.value.trim(), password: f.password.value,
      options: { emailRedirectTo: location.origin + "/", data: { name: f.name.value.trim().slice(0, 50) } } });
    busy(f, false);
    if (error) return msg("signup", friendly(error));
    saveLogin(f.email.value.trim(), f.password.value, f.name.value.trim());
    if (data.session) { if (!offerFaceId(data.session.user?.email)) close(); say("Account created - you're logged in"); setTimeout(() => f.reset(), 3000); return; }
    // Supabase hides whether the email already has an account; both cases end in an email
    setTimeout(() => f.reset(), 3000); msg("signup", "Nearly done! We've sent you an email - click the link in it to confirm your account.", true);
  });
  $("#f-forgot").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target; busy(f, true);
    const { error } = await sb.auth.resetPasswordForEmail(f.email.value.trim(), { redirectTo: location.origin + "/" });
    busy(f, false);
    if (error) return msg("forgot", friendly(error));
    msg("forgot", "If there's an account for that email, we've sent a link to reset your password.", true);
  });
  $("#f-reset").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target;
    if (f.password.value.length < 8) return msg("reset", "Please use a password of at least 8 characters.");
    busy(f, true);
    const { error } = await sb.auth.updateUser({ password: f.password.value });
    busy(f, false);
    if (error) return msg("reset", friendly(error));
    saveLogin(user?.email, f.password.value);
    close(); say("Password changed - you're logged in");
    setTimeout(() => f.reset(), 3000);
  });
  $("#f-name").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target; const name = f.name.value.trim().slice(0, 50);
    if (!name) return; busy(f, true);
    const { data, error } = await sb.auth.updateUser({ data: { name } });
    busy(f, false);
    if (error) return msg("account", friendly(error));
    user = data.user; paint(); msg("account", "Name saved", true);
  });
  $("#acct-billing")?.addEventListener("click", async () => {    // cancel or change card, on Stripe's own page
    const b = $("#acct-billing"); b.disabled = true;
    try {
      const r = await fetch("/api/billing-portal", { method: "POST", headers: await window.ssAuthHeader() }), d = await r.json();
      if (r.ok && d.url) { location.href = d.url; return; }
      say(d.detail || "Couldn't open your subscription. Please try again.");
    } catch { say("Couldn't open your subscription. Please try again."); }
    b.disabled = false;
  });
  $("#acct-logout").addEventListener("click", async () => {
    await sb.auth.signOut(); close(); say("Logged out. Your set stays on this device.");
    try { await navigator.credentials?.preventSilentAccess?.(); } catch {}   // next time, ask before using a saved login
  });
  $("#acct-delete").addEventListener("click", () => show("delete"));
  $("#acct-delete-yes").addEventListener("click", async () => {
    const b = $("#acct-delete-yes"); b.disabled = true;
    const { error } = await sb.rpc("delete_my_account");
    b.disabled = false;
    if (error) return msg("delete", "Couldn't delete your account. Please try again, or email us.");
    forgetLogin();
    await sb.auth.signOut(); close(); say("Your account and saved data have been deleted");
  });

  /* ---------- keeping the set, favourites + recent searches in the account, on every device */
  // The account's copy wins, so a track removed on one device stays removed on the others. Two exceptions:
  // the first time this device syncs with this account (its own tracks are added in, nothing is lost), and
  // changes made here that haven't reached the account yet (sent up first).
  const byId = (list, key) => { const seen = new Set(); return list.filter(t => { const k = t?.[key]; if (k == null || seen.has(k)) return false; seen.add(k); return true; }); };
  const DIRTY = "ss_sync_dirty", SYNCED = "ss_sync_uid";
  const flag = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} };
  const flagged = k => { try { return localStorage.getItem(k); } catch { return null; } };
  function showLocal() {        // the page shows whatever is now on this device
    try { set = read("ss_set"); renderSet(); } catch {}
    try { favs = read("ss_favs"); paintFavs(); if ($("#fav-panel")?.classList.contains("open")) renderFavs(); } catch {}
  }
  let pulling = null;
  function pull() { return pulling ||= doPull().finally(() => { pulling = null; }); }
  async function doPull() {
    if (!user) return;
    syncing = true;
    try {
      if (flagged(DIRTY) === user.id) { clearTimeout(saveTimer); await push(); return; }   // this device has newer changes
      const { data, error } = await sb.from("user_data").select("set_tracks, recent, favs").eq("user_id", user.id).maybeSingle();
      if (error) throw error;
      const first = flagged(SYNCED) !== user.id;
      const acct = { set: data?.set_tracks || [], favs: data?.favs || [], recent: data?.recent || [] };
      const mergedSet = first ? byId([...acct.set, ...read("ss_set")], "deezer_id") : acct.set;
      const mergedFavs = first ? byId([...read("ss_favs"), ...acct.favs], "deezer_id").slice(0, 500) : acct.favs;
      const mergedRecent = byId([...read("ss_recent"), ...acct.recent], "id").slice(0, 6);
      write("ss_set", mergedSet); write("ss_favs", mergedFavs); write("ss_recent", mergedRecent);
      showLocal();
      const same = (a, b) => JSON.stringify(a.map(t => t.deezer_id ?? t.id)) === JSON.stringify(b.map(t => t.deezer_id ?? t.id));
      if (!data || !same(mergedSet, acct.set) || !same(mergedFavs, acct.favs) || !same(mergedRecent, acct.recent)) await push();
      flag(SYNCED, user.id);
    } catch { /* offline: keep using this device's copy */ }
    finally { syncing = false; }
  }
  async function push() {
    if (!user) return;
    const { error } = await sb.from("user_data").upsert({ user_id: user.id, set_tracks: read("ss_set"), favs: read("ss_favs"),
                                                          recent: read("ss_recent"), updated_at: new Date().toISOString() });
    if (error) throw error;
    flag(DIRTY, null); flag(SYNCED, user.id);
  }
  window.addEventListener("ss:saved", () => {
    if (!user || syncing) return;
    flag(DIRTY, user.id);
    clearTimeout(saveTimer); saveTimer = setTimeout(() => push().catch(() => {}), 800);
  });
  // coming back to the site (another tab, the phone unlocked, a different device used meanwhile): fetch the latest
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible" && user) pull(); });
  addEventListener("pageshow", e => { if (e.persisted && user) pull(); });

  /* ---------- header + menu */
  const nameOf = u => (u?.user_metadata?.name || u?.user_metadata?.full_name || "").trim() || (u?.email || "").split("@")[0];
  function paint() {
    const name = user ? nameOf(user) : "";
    document.querySelectorAll("[data-account]").forEach(b => {
      const n = b.querySelector(".acct-name");
      n.classList.toggle("is-user", !!user);   // a person's name is never translated
      n.textContent = user ? name : "Log in / Sign up";
      b.querySelector(".acct-state").textContent = user ? "Signed in" : "";
      b.querySelector(".acct-ico").textContent = "";
      if (user) b.querySelector(".acct-ico").textContent = name.charAt(0).toUpperCase();
      else b.querySelector(".acct-ico").innerHTML = ICON;
      b.setAttribute("aria-label", user ? `${name}, signed in - open your account` : "Log in or sign up");
    });
    document.documentElement.classList.toggle("signed-in", !!user);
    if (user?.email) rememberLogin(user.email, user.user_metadata?.name);   // for "Continue as …" next time
  }
  const ICON = document.querySelector("[data-account] .acct-ico")?.innerHTML || "";

  window.ssAuthHeader = async () => {
    const t = (await sb.auth.getSession()).data.session?.access_token;
    return t ? { Authorization: `Bearer ${t}` } : {};
  };
  window.ssOpenAccount = view => open(view);
  window.ssRefreshAuth = async () => { try { await sb.auth.refreshSession(); } catch {} };
  sb.auth.getSession().then(({ data }) => { user = data.session?.user || user; paint(); authReady(); logVisit(); }, () => { authReady(); logVisit(); });
  // Count this visit (a random device number and the day, nothing else). The owner is skipped in Supabase.
  function logVisit() {
    try {
      let id = localStorage.getItem("ss_device");
      if (!id) { id = crypto.randomUUID(); localStorage.setItem("ss_device", id); }
      sb.rpc("log_visit", { p_device: id }).then(() => {}, () => {});
    } catch {}
  }
  sb.auth.onAuthStateChange((event, session) => {
    const was = user?.id;
    user = session?.user || null;
    paint();
    if (user?.id !== was) window.dispatchEvent(new Event("ss:auth"));
    if (event === "PASSWORD_RECOVERY") { open("reset"); return; }
    if (user && user.id !== was) pull();
    if (event === "SIGNED_IN" && /type=signup/.test(location.hash)) { say("Email confirmed - you're logged in"); setTimeout(() => offerFaceId(user?.email), 800); }
    if (/access_token|type=/.test(location.hash)) history.replaceState(null, "", location.pathname + location.search);
  });
  paint();
})();
