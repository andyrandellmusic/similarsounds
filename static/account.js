/* SimilarSounds accounts (optional): log in with email + password to keep your set and recent
 * searches on every device. Accounts, passwords and emails are handled by Supabase Auth
 * (passwords are never seen or stored by SimilarSounds). Everything works without logging in.
 */
(async function () {
  const $ = s => document.querySelector(s);
  let cfg;
  try { cfg = await (await fetch("/api/config")).json(); } catch { return; }
  if (!cfg.supabase_url || !cfg.supabase_anon_key) return;   // accounts not switched on yet

  await new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.75.0/dist/umd/supabase.min.js";
    s.onload = ok; s.onerror = fail; document.head.appendChild(s);
  }).catch(() => null);
  if (!window.supabase?.createClient) return;
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
    show(view || (user ? "account" : "login"));
    dlg.hidden = false;
    setTimeout(() => box.querySelector("input:not([hidden]), button.primary")?.focus(), 30);
  }
  function close() { dlg.hidden = true; opener?.focus?.(); }
  function show(view) {
    box.querySelectorAll("[data-view]").forEach(v => v.hidden = v.dataset.view !== view);
    box.querySelectorAll(".acct-msg").forEach(m => { m.textContent = ""; m.className = "acct-msg"; });
    if (view === "account") { $("#acct-email").textContent = user?.email || ""; $("#f-name").name.value = user?.user_metadata?.name || ""; }
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
    f.reset(); close(); say("Signed in - your set is saved to your account");
  });
  $("#f-signup").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target;
    if (f.password.value.length < 8) return msg("signup", "Please use a password of at least 8 characters.");
    busy(f, true);
    const { data, error } = await sb.auth.signUp({ email: f.email.value.trim(), password: f.password.value,
      options: { emailRedirectTo: location.origin + "/", data: { name: f.name.value.trim().slice(0, 50) } } });
    busy(f, false);
    if (error) return msg("signup", friendly(error));
    if (data.session) { f.reset(); close(); say("Account created - you're logged in"); return; }
    // Supabase hides whether the email already has an account; both cases end in an email
    f.reset(); msg("signup", "Nearly done! We've sent you an email - click the link in it to confirm your account.", true);
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
    f.reset(); close(); say("Password changed - you're logged in");
  });
  $("#f-name").addEventListener("submit", async e => {
    e.preventDefault(); const f = e.target; const name = f.name.value.trim().slice(0, 50);
    if (!name) return; busy(f, true);
    const { data, error } = await sb.auth.updateUser({ data: { name } });
    busy(f, false);
    if (error) return msg("account", friendly(error));
    user = data.user; paint(); msg("account", "Name saved", true);
  });
  $("#acct-logout").addEventListener("click", async () => {
    await sb.auth.signOut(); close(); say("Logged out. Your set stays on this device.");
  });
  $("#acct-delete").addEventListener("click", () => show("delete"));
  $("#acct-delete-yes").addEventListener("click", async () => {
    const b = $("#acct-delete-yes"); b.disabled = true;
    const { error } = await sb.rpc("delete_my_account");
    b.disabled = false;
    if (error) return msg("delete", "Couldn't delete your account. Please try again, or email us.");
    await sb.auth.signOut(); close(); say("Your account and saved data have been deleted");
  });

  /* ---------- keeping the set + recent searches in the account */
  const byId = (list, key) => { const seen = new Set(); return list.filter(t => { const k = t[key]; if (seen.has(k)) return false; seen.add(k); return true; }); };
  async function pull() {
    syncing = true;
    try {
      const { data, error } = await sb.from("user_data").select("set_tracks, recent").eq("user_id", user.id).maybeSingle();
      if (error) throw error;
      const localSet = read("ss_set"), localRecent = read("ss_recent");
      const mergedSet = byId([...(data?.set_tracks || []), ...localSet], "deezer_id");
      const mergedRecent = byId([...localRecent, ...(data?.recent || [])], "id").slice(0, 6);
      write("ss_set", mergedSet); write("ss_recent", mergedRecent);
      try { set = mergedSet; renderSet(); } catch {}
      if (!data || mergedSet.length !== (data.set_tracks || []).length || mergedRecent.length !== (data.recent || []).length) await push();
    } catch { /* offline: keep using this device's copy */ }
    syncing = false;
  }
  async function push() {
    if (!user) return;
    await sb.from("user_data").upsert({ user_id: user.id, set_tracks: read("ss_set"), recent: read("ss_recent"),
                                         updated_at: new Date().toISOString() });
  }
  window.addEventListener("ss:saved", () => {
    if (!user || syncing) return;
    clearTimeout(saveTimer); saveTimer = setTimeout(() => push().catch(() => {}), 800);
  });

  /* ---------- header + menu */
  const nameOf = u => (u?.user_metadata?.name || "").trim() || (u?.email || "").split("@")[0];
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
  }
  const ICON = document.querySelector("[data-account] .acct-ico")?.innerHTML || "";

  window.ssAuthHeader = async () => {
    const t = (await sb.auth.getSession()).data.session?.access_token;
    return t ? { Authorization: `Bearer ${t}` } : {};
  };
  window.ssOpenAccount = view => open(view);
  sb.auth.onAuthStateChange((event, session) => {
    const was = user?.id;
    user = session?.user || null;
    paint();
    if (user?.id !== was) window.dispatchEvent(new Event("ss:auth"));
    if (event === "PASSWORD_RECOVERY") { open("reset"); return; }
    if (user && user.id !== was) pull();
    if (event === "SIGNED_IN" && /type=signup/.test(location.hash)) say("Email confirmed - you're logged in");
    if (/access_token|type=/.test(location.hash)) history.replaceState(null, "", location.pathname + location.search);
  });
  paint();
})();
