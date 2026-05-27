const API_BASE_URL = window.location.origin + "/api";
let currentSyllabusData = [];

document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;

    if (currentPath === "/" || currentPath === "/index.html" || currentPath === "") {
        initLoginPage();
    } else if (currentPath === "/admin" || currentPath === "/admin.html") {
        checkAuth("admin");
        initAdminPage();
    } else if (currentPath === "/student" || currentPath === "/student.html") {
        checkAuth("student");
        initStudentPage();
    }
    setupLogoutButton();
});

function checkAuth(requiredRole) {
    const role = localStorage.getItem("user_role");
    const userId = localStorage.getItem("user_id");
    if (!userId || !role || role !== requiredRole) {
        alert("⚠️ Vui lòng đăng nhập đúng quyền tài khoản!");
        window.location.href = "/";
    }
}

function setupLogoutButton() {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.clear();
            window.location.href = "/";
        });
    }
}

function initLoginPage() {
    const loginBtn = document.getElementById("login-btn");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const errorMsg = document.getElementById("login-error");

    if (loginBtn) {
        loginBtn.addEventListener("click", async () => {
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem("user_id", data.user_id);
                    localStorage.setItem("user_role", data.role);
                    localStorage.setItem("username", data.username);
                    window.location.href = data.role === "admin" ? "/admin" : "/student";
                } else {
                    errorMsg.innerText = data.detail || "Sai thông tin!";
                    errorMsg.style.display = "block";
                }
            } catch (e) { console.error(e); }
        });
    }
}

function initAdminPage() {
    fetchDashboardData();
    loadCmsComboboxes();

    // Lắng nghe sự kiện đổi tuần trên combobox để đổi danh sách bài tập tương ứng
    const weekSelect = document.getElementById("cms-week-select");
    if (weekSelect) {
        weekSelect.addEventListener("change", () => {
            populateExerciseCombobox(parseInt(weekSelect.value));
        });
    }

    // Tạo Tuần mới
    const addWeekBtn = document.getElementById("add-week-btn");
    if (addWeekBtn) {
        addWeekBtn.addEventListener("click", async () => {
            const title = document.getElementById("week-title").value.trim();
            const order_num = parseInt(document.getElementById("week-order").value);
            const msg = document.getElementById("week-message");

            const response = await fetch(`${API_BASE_URL}/add_week`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, order_num })
            });
            if (response.ok) {
                showStatus(msg, "Đã tạo tuần học mới!", "success");
                loadCmsComboboxes();
                fetchDashboardData();
            }
        });
    }

    // Tạo Bài tập mới
    const addExeBtn = document.getElementById("add-exe-btn");
    if (addExeBtn) {
        addExeBtn.addEventListener("click", async () => {
            const week_id = parseInt(document.getElementById("cms-week-select").value);
            const title = document.getElementById("exe-title").value.trim();
            const msg = document.getElementById("exe-message");

            const response = await fetch(`${API_BASE_URL}/add_exercise`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, week_id, order_num: 1 })
            });
            if (response.ok) {
                showStatus(msg, "Đã ghim bài tập vào tuần này!", "success");
                loadCmsComboboxes();
            }
        });
    }

    // Tạo Hoạt động mới
    const addActBtn = document.getElementById("add-act-btn");
    if (addActBtn) {
        addActBtn.addEventListener("click", async () => {
            const exercise_id = parseInt(document.getElementById("cms-exe-select").value);
            const activity_type = document.getElementById("act-type").value;
            let contentStr = document.getElementById("act-content").value.trim();
            const msg = document.getElementById("act-message");

            let contentObj = {};
            try { contentObj = JSON.parse(contentStr); } catch(e) { contentObj = {"text": contentStr}; }

            const response = await fetch(`${API_BASE_URL}/add_activity`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ exercise_id, activity_type, content: contentObj, order_num: 1 })
            });
            if (response.ok) { showStatus(msg, "Đã đẩy hoạt động vào hệ thống!", "success"); }
        });
    }

    // Nút tạo nhanh bài tập mẫu
    const seedBtn = document.getElementById("seed-btn");
    if (seedBtn) {
        seedBtn.addEventListener("click", async () => {
            const res = await fetch(`${API_BASE_URL}/seed_data`, { method: "POST" });
            const data = await res.json();
            alert(data.message);
            loadCmsComboboxes();
            fetchDashboardData();
        });
    }

    // Xuất file báo cáo lớp học ra Excel
    const exportBtn = document.getElementById("btn-export-excel");
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            const rows = document.querySelectorAll("#users-table tr");
            let csv = [];
            for (let i = 0; i < rows.length; i++) {
                let row = [], cols = rows[i].querySelectorAll("td, th");
                for (let j = 0; j < cols.length; j++) row.push('"' + cols[j].innerText + '"');
                csv.push(row.join(","));
            }
            const csvFile = new Blob(["\uFEFF" + csv.join("\n")], { type: "text/csv;charset=utf-8;" });
            const a = document.createElement("a");
            a.download = "Bao_Cao_Lop_Hoc.csv";
            a.href = window.URL.createObjectURL(csvFile);
            a.click();
        });
    }

    // Tạo tài khoản hàng loạt
    const bulkBtn = document.getElementById("btn-bulk-register");
    if (bulkBtn) {
        bulkBtn.addEventListener("click", async () => {
            const txt = document.getElementById("bulk-users-data").value.split("\n");
            let list = [];
            txt.forEach(line => {
                let parts = line.split(/[\t,]+/);
                if (parts.length >= 2) list.push({ username: parts[0].trim(), password: parts[1].trim() });
            });
            const res = await fetch(`${API_BASE_URL}/register_bulk`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(list)
            });
            const data = await res.json();
            showStatus(document.getElementById("bulk-message"), data.message, "success");
            fetchDashboardData();
        });
    }
}

async function loadCmsComboboxes() {
    const res = await fetch(`${API_BASE_URL}/get_syllabus`);
    if (res.ok) {
        currentSyllabusData = await res.json();
        const weekSelect = document.getElementById("cms-week-select");
        if (weekSelect) {
            weekSelect.innerHTML = currentSyllabusData.map(w => `<option value="${w.week_id}">${w.title}</option>`).join("");
            if (currentSyllabusData.length > 0) populateExerciseCombobox(currentSyllabusData[0].week_id);
        }
    }
}

function populateExerciseCombobox(weekId) {
    const exeSelect = document.getElementById("cms-exe-select");
    if (!exeSelect) return;
    const targetWeek = currentSyllabusData.find(w => w.week_id === weekId);
    if (targetWeek && targetWeek.exercises) {
        exeSelect.innerHTML = targetWeek.exercises.map(e => `<option value="${e.id}">${e.title}</option>`).join("");
    } else {
        exeSelect.innerHTML = "";
    }
}

async function fetchDashboardData() {
    const resStats = await fetch(`${API_BASE_URL}/stats`);
    if (resStats.ok) {
        const s = await resStats.json();
        document.getElementById("stat-students").innerText = s.total_students;
        document.getElementById("stat-weeks").innerText = s.total_weeks;
        document.getElementById("stat-feedbacks").innerText = s.total_feedbacks;
    }

    const resUsers = await fetch(`${API_BASE_URL}/users`);
    if (resUsers.ok) {
        const users = await resUsers.json();
        const body = document.getElementById("users-list-body");
        body.innerHTML = users.map(u => `<tr><td style="padding:8px; border-bottom:1px solid #eee;">${u.username}</td><td style="padding:8px; border-bottom:1px solid #eee;">${u.done_count} Hoạt động</td></tr>`).join("");
    }

    const resFb = await fetch(`${API_BASE_URL}/get_feedbacks`);
    if (resFb.ok) {
        const feedbacks = await resFb.json();
        document.getElementById("feedback-list").innerHTML = feedbacks.map(f => `<div style="background:#f9f9f9; padding:10px; margin-bottom:8px; border-left:3px solid #2e7d32;"><b>${f.username}:</b> ${f.message}</div>`).join("");
    }
}

function updateLivePreview() {
    const box = document.getElementById("preview-course-content");
    if (!box) return;
    renderSyllabusHTML(currentSyllabusData, box);
}

function initStudentPage() {
    const nameSpan = document.getElementById("student-name");
    if (nameSpan) nameSpan.innerText = localStorage.getItem("username") || "Học sinh";
    fetchStudentSyllabus();
}

async function fetchStudentSyllabus() {
    const box = document.querySelector(".course-content");
    const res = await fetch(`${API_BASE_URL}/get_syllabus`);
    if (res.ok) {
        const data = await res.json();
        renderSyllabusHTML(data, box);
    }
}

function renderSyllabusHTML(data, container) {
    if (data.length === 0) {
        container.innerHTML = "<p>Chưa có lộ trình tuần học nào được cấu hình.</p>";
        return;
    }
    container.innerHTML = "";
    data.forEach(week => {
        const sec = document.createElement("div");
        sec.className = "week-section";
        sec.innerHTML = `<div class="week-title">⭐ ${week.title}</div>`;
        
        week.exercises.forEach(exe => {
            const btn = document.createElement("button");
            btn.className = "exercise-btn";
            btn.innerText = `${exe.title} (${exe.activities.length} Nhiệm vụ)`;
            btn.onclick = () => {
                alert(`📖 Bài tập: ${exe.title}\n\nCác công cụ cần học:\n` + exe.activities.map(a => `- [${a.type}]`).join("\n"));
            };
            sec.appendChild(btn);
        });
        container.appendChild(sec);
    });
}