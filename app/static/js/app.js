  const TOKEN_KEY = "jwt_auth_practice_token";
  let CURRENT_USER = null;
  let EDITING_POST_ID = null;

  const authScreen = document.getElementById("auth-screen");
  const appScreen = document.getElementById("app-screen");
  const msgBox = document.getElementById("msg");
  const appMsgBox = document.getElementById("app-msg");

  const tabLogin = document.getElementById("tab-login");
  const tabSignup = document.getElementById("tab-signup");
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");

  function flash(box, text, type) {
    box.textContent = text;
    box.className = "msg show " + type;
    setTimeout(() => { box.className = "msg"; }, 4000);
  }
  function clearMessage() { msgBox.className = "msg"; msgBox.textContent = ""; }

  function switchTab(target) {
    clearMessage();
    const isLogin = target === "login";
    tabLogin.setAttribute("aria-selected", isLogin ? "true" : "false");
    tabSignup.setAttribute("aria-selected", isLogin ? "false" : "true");
    loginForm.classList.toggle("hidden", !isLogin);
    signupForm.classList.toggle("hidden", isLogin);
  }
  tabLogin.addEventListener("click", () => switchTab("login"));
  tabSignup.addEventListener("click", () => switchTab("signup"));

  document.querySelectorAll(".toggle-pw").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.target);
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.textContent = show ? "숨김" : "표시";
    });
  });

  // ---------- API 헬퍼 ----------

  async function api(path, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers = options.headers || {};
    if (token) headers["Authorization"] = "Bearer " + token;
    if (options.json !== undefined) {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.json);
    }
    const res = await fetch(path, { ...options, headers });
    let data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) throw new Error((data && data.detail) || "요청 처리 중 오류가 발생했어요.");
    return data;
  }

  // ---------- 사이트 레이아웃: 페이지 전환 ----------

  const PAGES = ["home", "board", "weather", "products", "account", "files", "export", "activity", "profile", "admin"];

  function gotoPage(page) {
    PAGES.forEach((p) => {
      document.getElementById("page-" + p).classList.toggle("hidden", p !== page);
    });
    document.querySelectorAll(".nav-item").forEach((btn) => {
      if (btn.dataset.view === page) btn.setAttribute("aria-current", "page");
      else btn.removeAttribute("aria-current");
    });
    if (page === "home") refreshHome();
    if (page === "board") showListView();
    if (page === "weather") showWeatherListView();
    if (page === "products") showProductListView();
    if (page === "files") loadFileList();
    if (page === "activity") loadActivity();
    if (page === "profile") refreshProfile();
    if (page === "admin") loadAdminPage();
  }

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => gotoPage(btn.dataset.view));
  });

  document.querySelectorAll(".home-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const goto = btn.dataset.goto;
      if (goto === "write") { gotoPage("board"); showWriteView(null); }
      else gotoPage(goto);
    });
  });

  async function refreshHome() {
    document.getElementById("home-greeting").textContent =
      CURRENT_USER.username + "님, 환영합니다";
    try {
      const posts = await api("/api/posts");
      document.getElementById("home-post-count").textContent = posts.length;
    } catch (e) { /* 무시 */ }
  }

  function refreshProfile() {
    document.getElementById("profile-username").textContent = CURRENT_USER.username;
    document.getElementById("profile-created").textContent = CURRENT_USER["가입일"];

    const avatarEl = document.getElementById("profile-avatar");
    avatarEl.style.background = `hsl(${hueFromName(CURRENT_USER.username)}, 55%, 42%)`;
    avatarEl.textContent = CURRENT_USER.username.trim().charAt(0).toUpperCase();

    const badgeEl = document.getElementById("profile-days-badge");
    const joined = new Date(String(CURRENT_USER["가입일"]).replace(" ", "T"));
    const days = Math.floor((Date.now() - joined.getTime()) / 86400000);
    badgeEl.textContent = isNaN(days) ? "" : (days <= 0 ? "🎉 오늘 가입" : `가입한 지 ${days}일째`);
  }

  // ---------- 파일 크기 표시 ----------
  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  // ---------- 인증 포함 파일 다운로드 (blob) ----------
  async function downloadWithAuth(url, fallbackFilename) {
    const token = localStorage.getItem(TOKEN_KEY);
    const res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
    if (!res.ok) {
      const data = await res.json().catch(() => null);
      throw new Error((data && data.detail) || "다운로드에 실패했어요.");
    }
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
    const filename = match ? decodeURIComponent(match[1]) : fallbackFilename;

    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(objectUrl);
  }

  // ---------- 자료실 ----------

  function fileIcon(name) {
    const ext = (name.split(".").pop() || "").toLowerCase();
    if (["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp"].includes(ext)) return "🖼️";
    if (ext === "pdf") return "📕";
    if (["doc", "docx"].includes(ext)) return "📄";
    if (["xls", "xlsx", "csv"].includes(ext)) return "📊";
    if (["ppt", "pptx"].includes(ext)) return "📽️";
    if (["zip", "rar", "7z", "tar", "gz"].includes(ext)) return "🗜️";
    if (["mp3", "wav", "flac"].includes(ext)) return "🎵";
    if (["mp4", "mov", "avi", "mkv"].includes(ext)) return "🎬";
    if (["txt", "md"].includes(ext)) return "📝";
    return "📁";
  }

  async function loadFileList() {
    const tbody = document.getElementById("file-table-body");
    tbody.innerHTML = "";
    try {
      const files = await api("/api/files");
      if (files.length === 0) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 6;
        td.style.padding = "40px 10px";
        td.style.color = "var(--sub)";
        td.textContent = "아직 올라온 파일이 없어요.";
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
      }
      files.forEach((f) => {
        const tr = document.createElement("tr");

        const iconTd = document.createElement("td");
        iconTd.className = "col-file-icon";
        iconTd.textContent = fileIcon(f.original_name);
        tr.appendChild(iconTd);

        const nameTd = document.createElement("td");
        nameTd.className = "col-filename";
        const nameSpan = document.createElement("span");
        nameSpan.className = "filename-text";
        nameSpan.textContent = f.original_name;
        nameSpan.title = f.original_name;
        nameTd.appendChild(nameSpan);
        tr.appendChild(nameTd);

        const uploaderTd = document.createElement("td");
        const authorCell = document.createElement("div");
        authorCell.className = "author-cell";
        authorCell.appendChild(makeAvatar(f.uploader, "avatar-xs"));
        const nameEl = document.createElement("span");
        nameEl.className = "name";
        nameEl.textContent = f.uploader;
        authorCell.appendChild(nameEl);
        uploaderTd.appendChild(authorCell);
        tr.appendChild(uploaderTd);

        const sizeTd = document.createElement("td");
        sizeTd.textContent = formatBytes(f.size_bytes);
        tr.appendChild(sizeTd);

        const dateTd = document.createElement("td");
        dateTd.textContent = timeAgo(f.uploaded_at);
        tr.appendChild(dateTd);

        const actionsTd = document.createElement("td");
        actionsTd.className = "col-actions";
        const dlBtn = document.createElement("button");
        dlBtn.type = "button";
        dlBtn.className = "icon-btn";
        dlBtn.textContent = "⬇ 다운로드";
        dlBtn.addEventListener("click", async () => {
          try {
            await downloadWithAuth("/api/files/" + f.id + "/download", f.original_name);
          } catch (err) {
            flash(appMsgBox, err.message, "err");
          }
        });
        actionsTd.appendChild(dlBtn);

        if (f.uploader === CURRENT_USER.username) {
          const delBtn = document.createElement("button");
          delBtn.type = "button";
          delBtn.className = "icon-btn danger";
          delBtn.textContent = "삭제";
          delBtn.addEventListener("click", async () => {
            if (!confirm("이 파일을 삭제할까요?")) return;
            try {
              await api("/api/files/" + f.id, { method: "DELETE" });
              flash(appMsgBox, "삭제됐어요.", "ok");
              loadFileList();
            } catch (err) {
              flash(appMsgBox, err.message, "err");
            }
          });
          actionsTd.appendChild(delBtn);
        }
        tr.appendChild(actionsTd);

        tbody.appendChild(tr);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  document.getElementById("file-upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("file-input");
    if (!input.files.length) return;
    const submitBtn = document.getElementById("file-upload-submit");
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("upload", input.files[0]);
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const res = await fetch("/api/files", {
        method: "POST",
        headers: { Authorization: "Bearer " + token },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "업로드에 실패했어요.");
      flash(appMsgBox, "업로드 완료!", "ok");
      input.value = "";
      loadFileList();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ---------- 엑셀 출력 ----------

  document.getElementById("export-posts-btn").addEventListener("click", async () => {
    try {
      await downloadWithAuth("/api/export/posts", "posts_export.xlsx");
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  });

  document.getElementById("export-files-btn").addEventListener("click", async () => {
    try {
      await downloadWithAuth("/api/export/files", "files_export.xlsx");
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  });

  // ---------- 계정관리 ----------

  document.getElementById("password-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const current = document.getElementById("current-password").value;
    const next = document.getElementById("new-password").value;
    const confirm2 = document.getElementById("new-password-confirm").value;
    if (next !== confirm2) {
      flash(appMsgBox, "새 비밀번호가 서로 일치하지 않아요.", "err");
      return;
    }
    const btn = document.getElementById("password-submit");
    btn.disabled = true;
    try {
      await api("/account/password", {
        method: "PUT",
        json: { current_password: current, new_password: next },
      });
      flash(appMsgBox, "비밀번호가 변경됐어요.", "ok");
      e.target.reset();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      btn.disabled = false;
    }
  });

  document.getElementById("delete-account-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!confirm("정말 계정을 삭제할까요? 이 작업은 되돌릴 수 없어요.")) return;
    const password = document.getElementById("delete-account-password").value;
    const btn = document.getElementById("delete-account-submit");
    btn.disabled = true;
    try {
      await api("/account", { method: "DELETE", json: { password } });
      localStorage.removeItem(TOKEN_KEY);
      CURRENT_USER = null;
      showAuthScreen();
      flash(msgBox, "계정이 삭제됐어요. 그동안 감사했습니다.", "ok");
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      btn.disabled = false;
    }
  });

  // ---------- 내 활동 ----------

  function renderSimpleRow(container, primaryText, metaParts, onClick) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "post-row";
    const titleEl = document.createElement("div");
    titleEl.className = "title";
    titleEl.textContent = primaryText;
    const meta = document.createElement("div");
    meta.className = "meta";
    metaParts.forEach((part, i) => {
      const span = document.createElement("span");
      if (i > 0) span.className = "dot";
      span.textContent = part;
      meta.appendChild(span);
    });
    btn.appendChild(titleEl);
    btn.appendChild(meta);
    if (onClick) btn.addEventListener("click", onClick);
    else btn.style.cursor = "default";
    li.appendChild(btn);
    container.appendChild(li);
  }

  async function loadActivity() {
    const postsEl = document.getElementById("activity-posts");
    const commentsEl = document.getElementById("activity-comments");
    const filesEl = document.getElementById("activity-files");
    postsEl.innerHTML = "";
    commentsEl.innerHTML = "";
    filesEl.innerHTML = "";

    try {
      const data = await api("/api/me/activity");

      document.getElementById("activity-posts-count").textContent = "(" + data.posts.length + ")";
      document.getElementById("activity-comments-count").textContent = "(" + data.comments.length + ")";
      document.getElementById("activity-files-count").textContent = "(" + data.files.length + ")";

      if (data.posts.length === 0) {
        postsEl.innerHTML = '<li class="empty-state">아직 쓴 글이 없어요.</li>';
      } else {
        data.posts.forEach((p) => {
          renderSimpleRow(
            postsEl, p.title,
            ["👁 " + p.views, timeAgo(p.created_at)],
            () => { gotoPage("board"); showDetailView(p.id); }
          );
        });
      }

      if (data.comments.length === 0) {
        commentsEl.innerHTML = '<li class="empty-state">아직 쓴 댓글이 없어요.</li>';
      } else {
        data.comments.forEach((cm) => {
          renderSimpleRow(
            commentsEl, cm.content,
            ["→ " + cm.post_title, timeAgo(cm.created_at)],
            () => { gotoPage("board"); showDetailView(cm.post_id); }
          );
        });
      }

      if (data.files.length === 0) {
        filesEl.innerHTML = '<li class="empty-state">아직 올린 파일이 없어요.</li>';
      } else {
        data.files.forEach((f) => {
          renderSimpleRow(
            filesEl, f.original_name,
            [formatBytes(f.size_bytes), timeAgo(f.uploaded_at)],
            () => gotoPage("files")
          );
        });
      }
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  // ---------- 관리자 ----------

  async function loadAdminPage() {
    try {
      const stats = await api("/api/admin/stats");
      document.getElementById("admin-stat-users").textContent = stats.users;
      document.getElementById("admin-stat-posts").textContent = stats.posts;
      document.getElementById("admin-stat-files").textContent = stats.files;
      document.getElementById("admin-stat-products").textContent = stats.products;
      document.getElementById("admin-stat-weather").textContent = stats.weather;

      await loadBackupStatus();

      const users = await api("/api/admin/users");
      document.getElementById("admin-user-count").textContent = "(" + users.length + ")";

      const tbody = document.getElementById("admin-user-table-body");
      tbody.innerHTML = "";
      users.forEach((u) => {
        const tr = document.createElement("tr");

        const idTd = document.createElement("td");
        const idCell = document.createElement("div");
        idCell.className = "author-cell";
        idCell.style.justifyContent = "flex-start";
        idCell.appendChild(makeAvatar(u.username, "avatar-xs"));
        const nameSpan = document.createElement("span");
        nameSpan.className = "name";
        nameSpan.textContent = u.username;
        idCell.appendChild(nameSpan);
        idTd.appendChild(idCell);
        tr.appendChild(idTd);

        const roleTd = document.createElement("td");
        const roleBadge = document.createElement("span");
        roleBadge.className = "role-badge" + (u.is_admin ? " admin" : "");
        roleBadge.textContent = u.is_admin ? "관리자" : "일반";
        roleTd.appendChild(roleBadge);
        tr.appendChild(roleTd);

        const postTd = document.createElement("td");
        postTd.textContent = u.post_count;
        tr.appendChild(postTd);

        const fileTd = document.createElement("td");
        fileTd.textContent = u.file_count;
        tr.appendChild(fileTd);

        const dateTd = document.createElement("td");
        dateTd.textContent = timeAgo(u.created_at);
        tr.appendChild(dateTd);

        const actionTd = document.createElement("td");
        if (u.username === CURRENT_USER.username) {
          actionTd.textContent = "-";
          actionTd.style.color = "var(--sub)";
        } else {
          const delBtn = document.createElement("button");
          delBtn.type = "button";
          delBtn.className = "icon-btn danger";
          delBtn.textContent = "삭제";
          delBtn.addEventListener("click", async () => {
            if (!confirm(`"${u.username}" 계정을 삭제할까요? 작성한 글/댓글/파일은 남아있어요.`)) return;
            try {
              await api("/api/admin/users/" + encodeURIComponent(u.username), { method: "DELETE" });
              flash(appMsgBox, "삭제됐어요.", "ok");
              loadAdminPage();
            } catch (err) {
              flash(appMsgBox, err.message, "err");
            }
          });
          actionTd.appendChild(delBtn);
        }
        tr.appendChild(actionTd);

        tbody.appendChild(tr);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  async function loadBackupStatus() {
    try {
      const status = await api("/api/admin/backup/status");
      document.getElementById("backup-stat-postgres").textContent = status.postgres_post_count;
      document.getElementById("backup-stat-mongo").textContent = status.backed_up_count;
      document.getElementById("backup-last-synced").textContent = status.last_synced_at
        ? timeAgo(status.last_synced_at)
        : "아직 백업된 적 없음";
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }

    const tbody = document.getElementById("backup-post-table-body");
    tbody.innerHTML = "";
    try {
      const backupPosts = await api("/api/admin/backup/posts");
      if (backupPosts.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="5"><div class="empty-state"><div class="icon">🍃</div>아직 MongoDB에 백업된 글이 없어요.</div></td>`;
        tbody.appendChild(tr);
        return;
      }
      backupPosts.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="col-num">#${p.id}</td>
          <td class="col-title">${p.title}</td>
          <td>${p.author}</td>
          <td>${p.views}</td>
          <td>${timeAgo(p.backed_up_at)}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  document.getElementById("btn-backup-run").addEventListener("click", async () => {
    const btn = document.getElementById("btn-backup-run");
    btn.disabled = true;
    btn.textContent = "백업 중…";
    try {
      const result = await api("/api/admin/backup/run", { method: "POST" });
      flash(appMsgBox, result.message, "ok");
      await loadBackupStatus();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      btn.disabled = false;
      btn.textContent = "🔄 지금 백업 실행";
    }
  });

  function showAuthScreen() {
    appScreen.classList.add("hidden");
    authScreen.classList.remove("hidden");
  }

  function showAppScreen() {
    authScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
    document.getElementById("nav-username").textContent = CURRENT_USER.username;
    document.getElementById("today-date").textContent =
      new Date().toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric", weekday: "short" });
    document.getElementById("nav-admin").classList.toggle("hidden", !CURRENT_USER.is_admin);
    startNotifPolling();
    gotoPage("home");
  }

  // ---------- 알림 (헤더 종 아이콘) ----------

  const notifBtn = document.getElementById("notif-btn");
  const notifPanel = document.getElementById("notif-panel");
  const notifBadge = document.getElementById("notif-badge");
  const notifPanelSub = document.getElementById("notif-panel-sub");
  const notifList = document.getElementById("notif-list");
  const notifReadAllBtn = document.getElementById("notif-read-all");
  let notifPollTimer = null;

  async function refreshUnreadCount() {
    if (!CURRENT_USER) return;
    try {
      const data = await api("/api/notifications/unread-count");
      notifBadge.textContent = data.count > 99 ? "99+" : data.count;
      notifBadge.classList.toggle("hidden", data.count === 0);
      notifReadAllBtn.disabled = data.count === 0;
      notifPanelSub.textContent = data.count === 0 ? "새 알림 없음" : `새 알림 ${data.count}개`;
    } catch (e) {
      // 배지 숫자는 부가 정보라, 실패해도 화면 전체에 에러를 띄우지는 않는다.
    }
  }

  async function loadNotifications() {
    notifList.innerHTML = "";
    let items;
    try {
      items = await api("/api/notifications?limit=20");
    } catch (err) {
      flash(appMsgBox, err.message, "err");
      return;
    }

    if (items.length === 0) {
      const empty = document.createElement("div");
      empty.className = "notif-empty";
      empty.innerHTML = `<div class="icon">🔔</div>아직 받은 알림이 없어요.<br>내 글에 댓글이 달리면 여기에 표시돼요.`;
      notifList.appendChild(empty);
      return;
    }

    items.forEach((n) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "notif-item" + (n.is_read ? "" : " unread");

      // 댓글 단 사람을 색깔 원형 아바타로 보여준다 (회원 목록 등 다른 화면과 같은 방식).
      const avatarWrap = document.createElement("div");
      avatarWrap.className = "notif-avatar";
      avatarWrap.appendChild(makeAvatar(n.actor, "avatar-sm"));
      btn.appendChild(avatarWrap);

      const body = document.createElement("div");
      body.className = "notif-body";

      const line1 = document.createElement("div");
      line1.className = "notif-line1";
      // textContent로 사람 이름을 따로 넣기 때문에, 닉네임에 특수문자가 있어도 그대로 글자로만 보인다.
      const actorStrong = document.createElement("strong");
      actorStrong.textContent = n.actor;
      line1.appendChild(actorStrong);
      line1.appendChild(document.createTextNode("님이 댓글을 남겼어요"));
      body.appendChild(line1);

      const preview = document.createElement("div");
      preview.className = "notif-preview";
      preview.textContent = `"${n.preview}"`;
      body.appendChild(preview);

      const meta = document.createElement("div");
      meta.className = "notif-meta";

      const postChip = document.createElement("span");
      postChip.className = "notif-post-chip";
      postChip.textContent = `📋 ${n.post_title}`;
      meta.appendChild(postChip);

      const time = document.createElement("span");
      time.className = "notif-time";
      time.textContent = timeAgo(n.created_at);
      meta.appendChild(time);

      body.appendChild(meta);
      btn.appendChild(body);
      btn.addEventListener("click", () => openNotification(n));
      notifList.appendChild(btn);
    });
  }

  async function openNotification(n) {
    closeNotifPanel();
    if (!n.is_read) {
      try {
        await api("/api/notifications/" + n.id + "/read", { method: "POST" });
      } catch (e) {
        // 읽음 처리에 실패하더라도 글로 이동은 시켜준다.
      }
      await refreshUnreadCount();
    }
    if (n.post_id !== null && n.post_id !== undefined) {
      gotoPage("board");
      showDetailView(n.post_id);
    }
  }

  function openNotifPanel() {
    notifPanel.classList.remove("hidden");
    notifBtn.classList.add("active");
    notifBtn.setAttribute("aria-expanded", "true");
    loadNotifications();
  }

  function closeNotifPanel() {
    notifPanel.classList.add("hidden");
    notifBtn.classList.remove("active");
    notifBtn.setAttribute("aria-expanded", "false");
  }

  notifBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (notifPanel.classList.contains("hidden")) openNotifPanel();
    else closeNotifPanel();
  });

  // 패널 안을 클릭한 건 "바깥 클릭"으로 치지 않는다.
  notifPanel.addEventListener("click", (e) => e.stopPropagation());

  document.addEventListener("click", () => {
    if (!notifPanel.classList.contains("hidden")) closeNotifPanel();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !notifPanel.classList.contains("hidden")) {
      closeNotifPanel();
      notifBtn.focus();
    }
  });

  document.getElementById("notif-read-all").addEventListener("click", async () => {
    try {
      const result = await api("/api/notifications/read-all", { method: "POST" });
      flash(appMsgBox, result.message, "ok");
      await refreshUnreadCount();
      await loadNotifications();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  });

  function startNotifPolling() {
    stopNotifPolling();
    refreshUnreadCount();
    // 30초마다 "안 읽은 개수"만 가볍게 다시 물어본다. 목록 전체는 종을 눌렀을 때만 불러온다.
    notifPollTimer = setInterval(refreshUnreadCount, 30000);
  }

  function stopNotifPolling() {
    if (notifPollTimer !== null) {
      clearInterval(notifPollTimer);
      notifPollTimer = null;
    }
  }

  // ---------- 게시판 하위 화면 ----------

  function hideAllBoardViews() {
    document.getElementById("view-list").classList.add("hidden");
    document.getElementById("view-detail").classList.add("hidden");
    document.getElementById("view-write").classList.add("hidden");
  }

  async function showListView() {
    hideAllBoardViews();
    document.getElementById("view-list").classList.remove("hidden");
    CURRENT_PAGE = 1;
    await loadPostList();
  }

  function showWriteView(editingPost) {
    hideAllBoardViews();
    document.getElementById("view-write").classList.remove("hidden");
    const heading = document.getElementById("write-heading");
    const submitBtn = document.getElementById("post-submit");
    if (editingPost) {
      EDITING_POST_ID = editingPost.id;
      heading.textContent = "✏️ 글 수정";
      submitBtn.textContent = "수정 완료";
      document.getElementById("post-title").value = editingPost.title;
      document.getElementById("post-content").value = editingPost.content;
    } else {
      EDITING_POST_ID = null;
      heading.textContent = "✏️ 글쓰기";
      submitBtn.textContent = "등록";
      document.getElementById("post-title").value = "";
      document.getElementById("post-content").value = "";
    }
  }

  let CURRENT_POST_ID = null;

  async function showDetailView(postId) {
    hideAllBoardViews();
    document.getElementById("view-detail").classList.remove("hidden");
    try {
      const post = await api("/api/posts/" + postId);
      CURRENT_POST_ID = post.id;
      document.getElementById("detail-title").textContent = post.title;

      const meta = document.getElementById("detail-meta");
      meta.innerHTML = "";
      const authorSpan = document.createElement("span");
      authorSpan.textContent = post.author;
      const timeSpan = document.createElement("span");
      timeSpan.className = "dot";
      timeSpan.textContent = timeAgo(post.created_at);
      const viewChip = document.createElement("span");
      viewChip.className = "chip";
      viewChip.textContent = "👁 조회 " + post.views;
      meta.append(authorSpan, timeSpan, viewChip);

      document.getElementById("detail-content").textContent = post.content;

      const isMine = post.author === CURRENT_USER.username;
      const editBtn = document.getElementById("btn-edit");
      const deleteBtn = document.getElementById("btn-delete");
      editBtn.classList.toggle("hidden", !isMine);
      deleteBtn.classList.toggle("hidden", !isMine);
      editBtn.onclick = () => showWriteView(post);
      deleteBtn.onclick = () => handleDelete(post.id);

      await loadComments(post.id);
    } catch (err) {
      flash(appMsgBox, err.message, "err");
      showListView();
    }
  }

  // ---------- 댓글 ----------

  async function loadComments(postId) {
    const listEl = document.getElementById("comment-list");
    const countEl = document.getElementById("comment-count");
    listEl.innerHTML = "";
    try {
      const comments = await api("/api/posts/" + postId + "/comments");
      countEl.textContent = "(" + comments.length + ")";

      if (comments.length === 0) {
        const li = document.createElement("li");
        li.className = "comment-empty";
        li.textContent = "아직 댓글이 없어요. 첫 댓글을 남겨보세요!";
        listEl.appendChild(li);
        return;
      }

      comments.forEach((cmt) => {
        const li = document.createElement("li");
        li.className = "comment-item";
        li.appendChild(makeAvatar(cmt.author));

        const body = document.createElement("div");
        body.className = "comment-body";
        const head = document.createElement("div");
        head.className = "comment-head";
        const authorSpan = document.createElement("span");
        authorSpan.className = "author";
        authorSpan.textContent = cmt.author;
        const timeSpan = document.createElement("span");
        timeSpan.className = "time";
        timeSpan.textContent = timeAgo(cmt.created_at);
        head.append(authorSpan, timeSpan);

        const textEl = document.createElement("div");
        textEl.className = "comment-text";
        textEl.textContent = cmt.content;

        body.appendChild(head);
        body.appendChild(textEl);
        li.appendChild(body);

        if (cmt.author === CURRENT_USER.username) {
          const delBtn = document.createElement("button");
          delBtn.className = "comment-del";
          delBtn.textContent = "삭제";
          delBtn.addEventListener("click", () => handleDeleteComment(postId, cmt.id));
          li.appendChild(delBtn);
        }

        listEl.appendChild(li);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  document.getElementById("comment-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("comment-input");
    const content = input.value.trim();
    if (!content || !CURRENT_POST_ID) return;
    try {
      await api("/api/posts/" + CURRENT_POST_ID + "/comments", {
        method: "POST",
        json: { content },
      });
      input.value = "";
      await loadComments(CURRENT_POST_ID);
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  });

  async function handleDeleteComment(postId, commentId) {
    if (!confirm("이 댓글을 삭제할까요?")) return;
    try {
      await api("/api/posts/" + postId + "/comments/" + commentId, { method: "DELETE" });
      await loadComments(postId);
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  // ---------- 날씨 ----------

  function hideAllWeatherViews() {
    document.getElementById("weather-view-list").classList.add("hidden");
    document.getElementById("weather-view-write").classList.add("hidden");
  }

  function sourceBadgeHtml(source, createdBy) {
    if (source === "manual") return `<span class="source-badge manual">📝 ${createdBy}</span>`;
    return `<span class="source-badge auto">🤖 자동수집</span>`;
  }

  async function showWeatherListView() {
    hideAllWeatherViews();
    document.getElementById("weather-view-list").classList.remove("hidden");
    await loadWeatherPage();
  }

  async function loadWeatherPage() {
    // 현재(가장 최근) 날씨 카드
    try {
      const latest = await api("/api/weather/latest");
      document.getElementById("weather-now-emoji").textContent = latest.emoji || "🌡️";
      document.getElementById("weather-now-temp").textContent = latest.temperature_c + "°C";
      document.getElementById("weather-now-desc").textContent = `${latest.city} · ${latest.description}`;
      const metaBits = [];
      if (latest.humidity_percent != null) metaBits.push(`습도 ${latest.humidity_percent}%`);
      if (latest.wind_speed_ms != null) metaBits.push(`풍속 ${latest.wind_speed_ms}m/s`);
      metaBits.push(timeAgo(latest.recorded_at) + " 업데이트");
      document.getElementById("weather-now-meta").textContent = metaBits.join(" · ");
    } catch (e) {
      document.getElementById("weather-now-emoji").textContent = "🌡️";
      document.getElementById("weather-now-temp").textContent = "-";
      document.getElementById("weather-now-desc").textContent = "아직 수집된 날씨가 없어요. 서버가 켜진 뒤 잠시 기다려주세요.";
      document.getElementById("weather-now-meta").textContent = "";
    }

    // 기록 표
    const tbody = document.getElementById("weather-table-body");
    const countEl = document.getElementById("weather-count");
    tbody.innerHTML = "";
    try {
      const records = await api("/api/weather?limit=30");
      countEl.textContent = "(" + records.length + ")";

      if (records.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="7"><div class="empty-state"><div class="icon">🌤️</div>아직 기록이 없어요.</div></td>`;
        tbody.appendChild(tr);
        return;
      }

      records.forEach((r) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${timeAgo(r.recorded_at)}</td>
          <td>${r.city}</td>
          <td>${r.emoji || ""} ${r.description}</td>
          <td>${r.temperature_c}°C</td>
          <td>${r.humidity_percent != null ? r.humidity_percent + "%" : "-"}</td>
          <td>${r.wind_speed_ms != null ? r.wind_speed_ms + "m/s" : "-"}</td>
          <td>${sourceBadgeHtml(r.source, r.created_by)}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  function showWeatherWriteView() {
    hideAllWeatherViews();
    document.getElementById("weather-view-write").classList.remove("hidden");
    document.getElementById("weather-form").reset();
    document.getElementById("weather-city").value = "서울";
  }

  document.getElementById("weather-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const city = document.getElementById("weather-city").value.trim();
    const temperature_c = parseFloat(document.getElementById("weather-temp").value);
    const description = document.getElementById("weather-desc").value.trim();
    const humidityRaw = document.getElementById("weather-humidity").value;
    const windRaw = document.getElementById("weather-wind").value;
    const submitBtn = document.getElementById("weather-submit");
    submitBtn.disabled = true;
    try {
      await api("/api/weather", {
        method: "POST",
        json: {
          city,
          temperature_c,
          description,
          humidity_percent: humidityRaw === "" ? null : parseFloat(humidityRaw),
          wind_speed_ms: windRaw === "" ? null : parseFloat(windRaw),
        },
      });
      flash(appMsgBox, "날씨 기록이 등록됐어요.", "ok");
      showWeatherListView();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      submitBtn.disabled = false;
    }
  });

  document.getElementById("btn-weather-write").addEventListener("click", showWeatherWriteView);
  document.getElementById("btn-weather-cancel-write").addEventListener("click", showWeatherListView);

  // ---------- 상품등록 및 후기 ----------

  let CURRENT_PRODUCT_ID = null;
  let EDITING_PRODUCT_ID = null;
  let PRODUCT_IMAGE_DATA = null;

  function hideAllProductViews() {
    document.getElementById("product-view-list").classList.add("hidden");
    document.getElementById("product-view-detail").classList.add("hidden");
    document.getElementById("product-view-write").classList.add("hidden");
  }

  async function showProductListView() {
    hideAllProductViews();
    document.getElementById("product-view-list").classList.remove("hidden");
    await loadProductList();
  }

  async function loadProductList() {
    const grid = document.getElementById("product-grid");
    const countEl = document.getElementById("product-count");
    grid.innerHTML = "";
    try {
      const products = await api("/api/products");
      countEl.textContent = "(" + products.length + ")";

      if (products.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.style.gridColumn = "1 / -1";
        empty.innerHTML = '<div class="icon">📸</div>';
        empty.append("아직 등록된 후기가 없어요. 첫 후기를 남겨보세요!");
        grid.appendChild(empty);
        return;
      }

      products.forEach((p) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "product-card";

        const img = document.createElement("img");
        img.src = p.image_data;
        img.alt = p.name;
        card.appendChild(img);

        const body = document.createElement("div");
        body.className = "body";

        const nameEl = document.createElement("div");
        nameEl.className = "name";
        nameEl.textContent = p.name;

        const descEl = document.createElement("p");
        descEl.className = "desc";
        descEl.textContent = p.description;

        const metaEl = document.createElement("div");
        metaEl.className = "meta";
        const authorSpan = document.createElement("span");
        authorSpan.textContent = p.author;
        const timeSpan = document.createElement("span");
        timeSpan.className = "dot";
        timeSpan.textContent = timeAgo(p.created_at);
        metaEl.append(authorSpan, timeSpan);

        body.append(nameEl, descEl, metaEl);
        card.appendChild(body);
        card.addEventListener("click", () => showProductDetail(p.id));
        grid.appendChild(card);
      });
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  async function showProductDetail(productId) {
    hideAllProductViews();
    document.getElementById("product-view-detail").classList.remove("hidden");
    try {
      const p = await api("/api/products/" + productId);
      CURRENT_PRODUCT_ID = p.id;

      const imgEl = document.getElementById("product-detail-image");
      imgEl.src = p.image_data;
      imgEl.alt = p.name;
      document.getElementById("product-detail-title").textContent = p.name;

      const meta = document.getElementById("product-detail-meta");
      meta.innerHTML = "";
      const authorSpan = document.createElement("span");
      authorSpan.textContent = p.author;
      const timeSpan = document.createElement("span");
      timeSpan.className = "dot";
      timeSpan.textContent = timeAgo(p.created_at);
      meta.append(authorSpan, timeSpan);

      document.getElementById("product-detail-content").textContent = p.description;

      const isMine = p.author === CURRENT_USER.username;
      const editBtn = document.getElementById("btn-product-edit");
      const deleteBtn = document.getElementById("btn-product-delete");
      editBtn.classList.toggle("hidden", !isMine);
      deleteBtn.classList.toggle("hidden", !isMine);
      editBtn.onclick = () => showProductWriteView(p);
      deleteBtn.onclick = () => handleProductDelete(p.id);
    } catch (err) {
      flash(appMsgBox, err.message, "err");
      showProductListView();
    }
  }

  function showProductWriteView(editingProduct) {
    hideAllProductViews();
    document.getElementById("product-view-write").classList.remove("hidden");
    const heading = document.getElementById("product-write-heading");
    const submitBtn = document.getElementById("product-submit");
    const preview = document.getElementById("product-image-preview");
    document.getElementById("product-image-input").value = "";
    if (editingProduct) {
      EDITING_PRODUCT_ID = editingProduct.id;
      PRODUCT_IMAGE_DATA = editingProduct.image_data;
      heading.textContent = "📸 후기 수정";
      submitBtn.textContent = "수정 완료";
      document.getElementById("product-name").value = editingProduct.name;
      document.getElementById("product-description").value = editingProduct.description;
      preview.src = editingProduct.image_data;
      preview.classList.remove("hidden");
    } else {
      EDITING_PRODUCT_ID = null;
      PRODUCT_IMAGE_DATA = null;
      heading.textContent = "📸 후기 남기기";
      submitBtn.textContent = "등록";
      document.getElementById("product-name").value = "";
      document.getElementById("product-description").value = "";
      preview.src = "";
      preview.classList.add("hidden");
    }
  }

  document.getElementById("product-image-input").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 3 * 1024 * 1024) {
      flash(appMsgBox, "이미지 용량이 너무 커요 (3MB 이하로 올려주세요).", "err");
      e.target.value = "";
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      PRODUCT_IMAGE_DATA = reader.result;
      const preview = document.getElementById("product-image-preview");
      preview.src = PRODUCT_IMAGE_DATA;
      preview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  });

  document.getElementById("product-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("product-name").value.trim();
    const description = document.getElementById("product-description").value.trim();
    if (!PRODUCT_IMAGE_DATA) {
      flash(appMsgBox, "사진을 선택해주세요.", "err");
      return;
    }
    const submitBtn = document.getElementById("product-submit");
    submitBtn.disabled = true;
    try {
      if (EDITING_PRODUCT_ID) {
        await api("/api/products/" + EDITING_PRODUCT_ID, {
          method: "PUT",
          json: { name, description, image_data: PRODUCT_IMAGE_DATA },
        });
        flash(appMsgBox, "수정됐어요.", "ok");
        showProductDetail(EDITING_PRODUCT_ID);
      } else {
        const result = await api("/api/products", {
          method: "POST",
          json: { name, description, image_data: PRODUCT_IMAGE_DATA },
        });
        flash(appMsgBox, "후기가 등록됐어요.", "ok");
        showProductDetail(result.id);
      }
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      submitBtn.disabled = false;
    }
  });

  async function handleProductDelete(productId) {
    if (!confirm("정말 이 후기를 삭제할까요?")) return;
    try {
      await api("/api/products/" + productId, { method: "DELETE" });
      flash(appMsgBox, "삭제됐어요.", "ok");
      showProductListView();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  document.getElementById("btn-product-write").addEventListener("click", () => showProductWriteView(null));
  document.getElementById("btn-product-cancel-write").addEventListener("click", showProductListView);
  document.getElementById("btn-back-from-product-detail").addEventListener("click", showProductListView);

  // ---------- 시각/아바타 유틸 ----------

  function timeAgo(dateStr) {
    const then = new Date(dateStr.replace(" ", "T"));
    const diffSec = Math.floor((Date.now() - then.getTime()) / 1000);
    if (isNaN(diffSec)) return dateStr;
    if (diffSec < 60) return "방금 전";
    if (diffSec < 3600) return Math.floor(diffSec / 60) + "분 전";
    if (diffSec < 86400) return Math.floor(diffSec / 3600) + "시간 전";
    if (diffSec < 86400 * 7) return Math.floor(diffSec / 86400) + "일 전";
    return then.toLocaleDateString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit" });
  }

  function hueFromName(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return Math.abs(hash) % 360;
  }

  function makeAvatar(username, sizeClass) {
    const el = document.createElement("span");
    el.className = sizeClass || "avatar-sm";
    el.style.background = `hsl(${hueFromName(username)}, 55%, 42%)`;
    el.textContent = username.trim().charAt(0).toUpperCase();
    el.setAttribute("aria-hidden", "true");
    return el;
  }

  // ---------- 글 목록 ----------

  let searchDebounce = null;
  let CURRENT_PAGE = 1;
  const BOARD_PAGE_SIZE = 10;

  async function loadPostList(page) {
    const tbody = document.getElementById("post-table-body");
    const countEl = document.getElementById("post-count");
    const pagEl = document.getElementById("board-pagination");
    const q = document.getElementById("search-input").value.trim();
    const sort = document.getElementById("sort-select").value;
    if (page) CURRENT_PAGE = page;
    tbody.innerHTML = "";
    pagEl.innerHTML = "";
    try {
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      params.set("sort", sort);
      params.set("page", CURRENT_PAGE);
      params.set("page_size", BOARD_PAGE_SIZE);
      const data = await api("/api/posts?" + params.toString());
      countEl.textContent = "(" + data.total + ")";

      if (data.items.length === 0) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 6;
        td.style.padding = "40px 10px";
        td.style.color = "var(--sub)";
        td.textContent = q ? "검색 결과가 없어요." : "아직 글이 없어요. 첫 글을 남겨보세요!";
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
      }

      data.items.forEach((post, idx) => {
        const tr = document.createElement("tr");

        const numTd = document.createElement("td");
        numTd.className = "col-num";
        numTd.textContent = data.total - (CURRENT_PAGE - 1) * BOARD_PAGE_SIZE - idx;
        tr.appendChild(numTd);

        const catTd = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = "cat-badge";
        badge.textContent = "일반";
        catTd.appendChild(badge);
        tr.appendChild(catTd);

        const titleTd = document.createElement("td");
        titleTd.className = "col-title";
        const titleCell = document.createElement("div");
        titleCell.className = "title-cell";

        const isNew = (Date.now() - new Date(post.created_at.replace(" ", "T")).getTime()) < 86400 * 1000;
        if (isNew) {
          const newBadge = document.createElement("span");
          newBadge.className = "post-badge new";
          newBadge.textContent = "NEW";
          titleCell.appendChild(newBadge);
        }
        if (post.views >= 20) {
          const hotBadge = document.createElement("span");
          hotBadge.className = "post-badge hot";
          hotBadge.textContent = "🔥";
          titleCell.appendChild(hotBadge);
        }

        const titleBtn = document.createElement("button");
        titleBtn.type = "button";
        titleBtn.textContent = post.title;
        titleBtn.addEventListener("click", () => showDetailView(post.id));
        titleCell.appendChild(titleBtn);

        if (post.comment_count > 0) {
          const cmt = document.createElement("span");
          cmt.className = "cmt-count";
          cmt.textContent = "[" + post.comment_count + "]";
          titleCell.appendChild(cmt);
        }
        titleTd.appendChild(titleCell);
        tr.appendChild(titleTd);

        const authorTd = document.createElement("td");
        const authorCell = document.createElement("div");
        authorCell.className = "author-cell";
        authorCell.appendChild(makeAvatar(post.author, "avatar-xs"));
        const authorName = document.createElement("span");
        authorName.className = "name";
        authorName.textContent = post.author;
        authorCell.appendChild(authorName);
        authorTd.appendChild(authorCell);
        tr.appendChild(authorTd);

        const dateTd = document.createElement("td");
        dateTd.textContent = timeAgo(post.created_at);
        tr.appendChild(dateTd);

        const viewsTd = document.createElement("td");
        viewsTd.textContent = post.views;
        tr.appendChild(viewsTd);

        tbody.appendChild(tr);
      });

      renderPagination(data.total, data.page, data.page_size);
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  function renderPagination(total, page, pageSize) {
    const pagEl = document.getElementById("board-pagination");
    pagEl.innerHTML = "";
    const totalPages = Math.max(Math.ceil(total / pageSize), 1);
    if (totalPages <= 1) return;

    const makeBtn = (label, targetPage, opts = {}) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = label;
      if (opts.current) btn.setAttribute("aria-current", "page");
      if (opts.disabled) btn.disabled = true;
      else btn.addEventListener("click", () => loadPostList(targetPage));
      return btn;
    };

    pagEl.appendChild(makeBtn("‹", page - 1, { disabled: page <= 1 }));

    const windowSize = 5;
    let start = Math.max(1, page - Math.floor(windowSize / 2));
    let end = Math.min(totalPages, start + windowSize - 1);
    start = Math.max(1, end - windowSize + 1);

    for (let p = start; p <= end; p++) {
      pagEl.appendChild(makeBtn(String(p), p, { current: p === page }));
    }

    pagEl.appendChild(makeBtn("›", page + 1, { disabled: page >= totalPages }));
  }

  document.getElementById("search-input").addEventListener("input", () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => loadPostList(1), 300);
  });
  document.getElementById("sort-select").addEventListener("change", () => loadPostList(1));

  async function handleDelete(postId) {
    if (!confirm("정말 이 글을 삭제할까요?")) return;
    try {
      await api("/api/posts/" + postId, { method: "DELETE" });
      flash(appMsgBox, "삭제됐어요.", "ok");
      showListView();
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    }
  }

  document.getElementById("btn-write").addEventListener("click", () => showWriteView(null));
  document.getElementById("btn-cancel-write").addEventListener("click", showListView);
  document.getElementById("btn-back-from-detail").addEventListener("click", showListView);

  document.getElementById("post-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("post-title").value.trim();
    const content = document.getElementById("post-content").value.trim();
    const submitBtn = document.getElementById("post-submit");
    submitBtn.disabled = true;
    try {
      if (EDITING_POST_ID) {
        await api("/api/posts/" + EDITING_POST_ID, { method: "PUT", json: { title, content } });
        flash(appMsgBox, "수정됐어요.", "ok");
        showDetailView(EDITING_POST_ID);
      } else {
        const result = await api("/api/posts", { method: "POST", json: { title, content } });
        flash(appMsgBox, "글이 등록됐어요.", "ok");
        showDetailView(result.id);
      }
    } catch (err) {
      flash(appMsgBox, err.message, "err");
    } finally {
      submitBtn.disabled = false;
    }
  });

  document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem(TOKEN_KEY);
    CURRENT_USER = null;
    showAuthScreen();
    loginForm.reset();
    clearMessage();
  });

  // ---------- 로그인 / 회원가입 ----------

  (async function init() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return;
    try {
      CURRENT_USER = await api("/me");
      showAppScreen();
    } catch (e) {
      localStorage.removeItem(TOKEN_KEY);
    }
  })();

  // ---------- 회원가입: 계정 유형(일반/관리자) 선택 ----------
  const roleBtnUser = document.getElementById("role-btn-user");
  const roleBtnAdmin = document.getElementById("role-btn-admin");
  const adminCodeField = document.getElementById("admin-code-field");
  const adminCodeInput = document.getElementById("signup-admin-code");
  let selectedRole = "user";

  function setSelectedRole(role) {
    selectedRole = role;
    roleBtnUser.setAttribute("aria-checked", String(role === "user"));
    roleBtnAdmin.setAttribute("aria-checked", String(role === "admin"));
    adminCodeField.classList.toggle("hidden", role !== "admin");
    if (role !== "admin") adminCodeInput.value = "";
  }
  roleBtnUser.addEventListener("click", () => setSelectedRole("user"));
  roleBtnAdmin.addEventListener("click", () => setSelectedRole("admin"));

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();
    const username = document.getElementById("signup-username").value.trim();
    const password = document.getElementById("signup-password").value;
    const btn = document.getElementById("signup-submit");
    btn.disabled = true;
    try {
      const body = { username, password };
      if (selectedRole === "admin") body.admin_code = adminCodeInput.value;
      await api("/signup", { method: "POST", json: body });
      flash(msgBox, "가입 완료! 이제 로그인해보세요.", "ok");
      switchTab("login");
      document.getElementById("login-username").value = username;
      setSelectedRole("user");
      signupForm.reset();
    } catch (err) {
      flash(msgBox, err.message, "err");
    } finally {
      btn.disabled = false;
    }
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const btn = document.getElementById("login-submit");
    btn.disabled = true;
    try {
      const body = new URLSearchParams();
      body.set("username", username);
      body.set("password", password);
      const res = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "로그인에 실패했어요.");
      localStorage.setItem(TOKEN_KEY, data.access_token);
      CURRENT_USER = await api("/me");
      showAppScreen();
    } catch (err) {
      flash(msgBox, err.message, "err");
    } finally {
      btn.disabled = false;
    }
  });
