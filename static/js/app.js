// ==========================================
// CẤU HÌNH API (MÔ HÌNH V2 MONOLITH)
// ==========================================
const API_BASE_URL = window.location.origin + "/api";

// ==========================================
// BỘ ĐIỀU HƯỚNG TỰ ĐỘNG (ROUTER)
// ==========================================
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
        alert("⚠️ Bạn không có quyền truy cập trang này. Vui lòng đăng nhập!");
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

// ==========================================
// LOGIC: TRANG ĐĂNG NHẬP (INDEX.HTML)
// ==========================================
function initLoginPage() {
    const loginBtn = document.getElementById("login-btn");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const errorMsg = document.getElementById("login-error");

    const savedRole = localStorage.getItem("user_role");
    if (savedRole === "admin") window.location.href = "/admin";
    if (savedRole === "student") window.location.href = "/student";

    if (loginBtn) {
        loginBtn.addEventListener("click", async () => {
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            if (!username || !password) {
                showError(errorMsg, "Vui lòng nhập đầy đủ tài khoản và mật khẩu!");
                return;
            }

            try {
                loginBtn.innerText = "Đang kết nối...";
                loginBtn.disabled = true;
                errorMsg.style.display = "none";

                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok && data.status === "success") {
                    localStorage.setItem("user_id", data.user_id);
                    localStorage.setItem("user_role", data.role);
                    localStorage.setItem("username", data.username);

                    if (data.role === "admin") {
                        window.location.href = "/admin";
                    } else {
                        window.location.href = "/student";
                    }
                } else {
                    showError(errorMsg, data.detail || "Sai tên đăng nhập hoặc mật khẩu!");
                }
            } catch (error) {
                showError(errorMsg, "Không thể kết nối với máy chủ!");
            } finally {
                loginBtn.innerText = "Vào Học";
                loginBtn.disabled = false;
            }
        });
    }
}

function showError(element, text) {
    element.innerText = text;
    element.style.display = "block";
}

// ==========================================
// LOGIC: TRANG QUẢN TRỊ (ADMIN.HTML)
// ==========================================
function initAdminPage() {
    const adminNameSpan = document.getElementById("admin-name");
    if (adminNameSpan) adminNameSpan.innerText = "Thầy " + (localStorage.getItem("username") || "Nam");

    // 1. Tải Thống kê & Bảng Học sinh
    fetchDashboardData();

    // 2. Cấp tài khoản hàng loạt (Copy/Paste từ Excel)
    const bulkBtn = document.getElementById("btn-bulk-register");
    const bulkInput = document.getElementById("bulk-users-data");
    const bulkMsg = document.getElementById("bulk-message");

    if (bulkBtn) {
        bulkBtn.addEventListener("click", async () => {
            const lines = bulkInput.value.split('\n');
            const usersToCreate = [];

            for (let line of lines) {
                if (line.trim() === '') continue;
                const parts = line.split(/[\t,]+/); 
                if (parts.length >= 2) {
                    usersToCreate.push({
                        username: parts[0].trim(),
                        password: parts[1].trim(),
                        role: "student"
                    });
                }
            }

            if (usersToCreate.length === 0) {
                showStatus(bulkMsg, "Dữ liệu trống hoặc sai định dạng!", "error");
                return;
            }

            try {
                bulkBtn.disabled = true;
                bulkBtn.innerText = "Đang xử lý...";
                const response = await fetch(`${API_BASE_URL}/register_bulk`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(usersToCreate)
                });

                const data = await response.json();
                showStatus(bulkMsg, data.message, response.ok ? "success" : "error");
                if (response.ok) {
                    bulkInput.value = "";
                    fetchDashboardData(); 
                }
            } catch (error) {
                showStatus(bulkMsg, "Lỗi kết nối máy chủ!", "error");
            } finally {
                bulkBtn.disabled = false;
                bulkBtn.innerText = "🚀 Tạo Hàng Loạt";
            }
        });
    }

    // 3. Xuất file Excel (CSV UTF-8 chuẩn font tiếng Việt)
    const exportBtn = document.getElementById("btn-export-excel");
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            const rows = document.querySelectorAll("#users-table tr");
            let csv = [];
            for (let i = 0; i < rows.length; i++) {
                let row = [], cols = rows[i].querySelectorAll("td, th");
                for (let j = 0; j < cols.length; j++) {
                    row.push('"' + cols[j].innerText + '"');
                }
                csv.push(row.join(","));
            }
            const csvFile = new Blob(["\uFEFF" + csv.join("\n")], { type: "text/csv;charset=utf-8;" });
            const downloadLink = document.createElement("a");
            downloadLink.download = "Danh_Sach_Hoc_Sinh.csv";
            downloadLink.href = window.URL.createObjectURL(csvFile);
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);
            downloadLink.click();
        });
    }

    // 4. Tạo tài khoản đơn lẻ
    const registerBtn = document.getElementById("register-btn");
    const userInp = document.getElementById("reg-username");
    const passInp = document.getElementById("reg-password");
    const regMsg = document.getElementById("reg-message");

    if (registerBtn) {
        registerBtn.addEventListener("click", async () => {
            const username = userInp.value.trim();
            const password = passInp.value.trim();

            if (!username || !password) {
                showStatus(regMsg, "Vui lòng điền đủ thông tin!", "error");
                return;
            }

            try {
                registerBtn.disabled = true;
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password, role: "student" })
                });

                const data = await response.json();
                if (response.ok) {
                    showStatus(regMsg, `✅ Tạo thành công: ${username}`, "success");
                    userInp.value = "";
                    passInp.value = "";
                    fetchDashboardData(); 
                } else {
                    showStatus(regMsg, data.detail || "Lỗi tạo tài khoản!", "error");
                }
            } catch (error) {
                showStatus(regMsg, "Lỗi kết nối máy chủ!", "error");
            } finally {
                registerBtn.disabled = false;
            }
        });
    }

    // 5. Nút Bơm dữ liệu mẫu
    const seedBtn = document.getElementById("seed-btn");
    const seedMsg = document.getElementById("seed-message");
    
    if (seedBtn) {
        seedBtn.addEventListener("click", async () => {
            try {
                seedBtn.disabled = true;
                seedBtn.innerText = "Đang xử lý...";
                const response = await fetch(`${API_BASE_URL}/seed_data`, { method: "POST" });
                const data = await response.json();
                showStatus(seedMsg, data.message || "Đã chạy lệnh seed!", "success");
                fetchDashboardData();
            } catch (error) {
                showStatus(seedMsg, "Lỗi kết nối máy chủ!", "error");
            } finally {
                seedBtn.disabled = false;
                seedBtn.innerText = "Bơm Dữ Liệu Bài Học Mẫu";
            }
        });
    }

    // 6. Tạo lộ trình bài học mới
    const addWeekBtn = document.getElementById("add-week-btn");
    const weekTitleInp = document.getElementById("week-title");
    const weekOrderInp = document.getElementById("week-order");
    const weekMsg = document.getElementById("week-message");

    if (addWeekBtn) {
        addWeekBtn.addEventListener("click", async () => {
            const title = weekTitleInp.value.trim();
            const order_num = parseInt(weekOrderInp.value.trim());

            if (!title || isNaN(order_num)) {
                showStatus(weekMsg, "Vui lòng nhập tên và số thứ tự hợp lệ!", "error");
                return;
            }

            try {
                addWeekBtn.disabled = true;
                addWeekBtn.innerText = "Đang lưu...";

                const response = await fetch(`${API_BASE_URL}/add_week`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, order_num })
                });

                const data = await response.json();
                if (response.ok) {
                    showStatus(weekMsg, `✅ ${data.message}`, "success");
                    weekTitleInp.value = "";
                    weekOrderInp.value = "";
                    fetchDashboardData();
                } else {
                    showStatus(weekMsg, data.detail || "Lỗi tạo tuần học!", "error");
                }
            } catch (error) {
                showStatus(weekMsg, "Lỗi kết nối máy chủ!", "error");
            } finally {
                addWeekBtn.disabled = false;
                addWeekBtn.innerText = "Tạo Tuần Học";
            }
        });
    }

    // 7. Lấy danh sách Hòm thư học sinh
    fetchFeedbacks();
}

// ==========================================
// HÀM LIÊN KẾT: CẬP NHẬT CHỈ SỐ VÀ BẢNG LỚP
// ==========================================
async function fetchDashboardData() {
    try {
        const statsRes = await fetch(`${API_BASE_URL}/stats`);
        if (statsRes.ok) {
            const stats = await statsRes.json();
            document.getElementById("stat-students").innerText = stats.total_students;
            document.getElementById("stat-weeks").innerText = stats.total_weeks;
            document.getElementById("stat-feedbacks").innerText = stats.total_feedbacks;
        }
    } catch (e) { console.error("Lỗi tải thống kê"); }

    try {
        const usersRes = await fetch(`${API_BASE_URL}/users`);
        const tbody = document.getElementById("users-list-body");
        if (usersRes.ok) {
            const users = await usersRes.json();
            tbody.innerHTML = "";
            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="padding: 15px; text-align: center;">Chưa có học sinh nào.</td></tr>';
                return;
            }
            users.forEach(u => {
                tbody.innerHTML += `
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">#${u.id}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee; font-weight: 500;">${u.username}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">
                            <span style="background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">${u.role}</span>
                        </td>
                    </tr>
                `;
            });
        }
    } catch (e) { console.error("Lỗi tải danh sách"); }
}

async function fetchFeedbacks() {
    const feedbackContainer = document.getElementById("feedback-list");
    if (!feedbackContainer) return;

    try {
        const response = await fetch(`${API_BASE_URL}/get_feedbacks`);
        if (!response.ok) throw new Error();
        const feedbacks = await response.json();

        if (feedbacks.length === 0) {
            feedbackContainer.innerHTML = '<p style="color: #666; font-style: italic; text-align: center;">Chưa có tin nhắn nào từ học sinh.</p>';
            return;
        }

        feedbackContainer.innerHTML = ""; 
        
        feedbacks.forEach(fb => {
            const fbDiv = document.createElement("div");
            fbDiv.style.borderLeft = "4px solid #2e7d32";
            fbDiv.style.backgroundColor = "#f9f9f9";
            fbDiv.style.padding = "15px";
            fbDiv.style.marginBottom = "15px";
            fbDiv.style.borderRadius = "6px";
            fbDiv.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)";

            fbDiv.innerHTML = `
                <div style="font-weight: bold; color: #1b5e20; margin-bottom: 8px;">
                    👤 Học sinh: ${fb.username} 
                    <span style="font-size: 0.8em; color: #888; font-weight: normal; margin-left: 10px;">(Gửi từ: ${fb.location})</span>
                </div>
                <div style="color: #333; line-height: 1.5;">${fb.message}</div>
            `;
            feedbackContainer.appendChild(fbDiv);
        });
    } catch (error) {
        feedbackContainer.innerHTML = '<p style="color: red; text-align: center;">Lỗi khi tải tin nhắn!</p>';
    }
}

// ==========================================
// LOGIC: TRANG HỌC SINH (STUDENT.HTML)
// ==========================================
function initStudentPage() {
    const studentNameSpan = document.getElementById("student-name");
    if (studentNameSpan) studentNameSpan.innerText = localStorage.getItem("username") || "Học sinh";

    fetchCourseSyllabus();
    setupFeedback();
}

async function fetchCourseSyllabus() {
    const courseContentDiv = document.querySelector(".course-content");
    try {
        const response = await fetch(`${API_BASE_URL}/get_syllabus`);
        if (!response.ok) throw new Error();
        
        const weeksData = await response.json();
        
        if (weeksData.length === 0) {
            courseContentDiv.innerHTML = '<p style="text-align:center; padding:20px; color:#666;">Chưa có bài học nào được tạo. Hệ thống đang chờ cập nhật.</p>';
            return;
        }

        renderSyllabusHTML(weeksData, courseContentDiv);
    } catch (error) {
        courseContentDiv.innerHTML = '<p style="text-align:center; padding:20px; color:red;">Không thể kết nối Backend để lấy bài học.</p>';
    }
}

function renderSyllabusHTML(weeksData, container) {
    container.innerHTML = "";

    weeksData.forEach(week => {
        const weekSection = document.createElement("div");
        weekSection.className = "week-section";

        const weekTitle = document.createElement("div");
        weekTitle.className = "week-title";
        weekTitle.innerText = week.title;
        weekSection.appendChild(weekTitle);

        week.exercises.forEach(exe => {
            const exeBtn = document.createElement("button");
            exeBtn.className = "exercise-btn";
            exeBtn.innerText = exe.title;
            
            exeBtn.onclick = () => {
                let activityList = exe.activities.map((act, index) => `Hoạt động ${index + 1}: ${act}`).join("\n");
                alert(`📖 Em đang mở: ${exe.title}\n\nNhiệm vụ:\n${activityList || "Chưa có hoạt động nào"}\n\n(Chức năng làm bài đang được NamY hoàn thiện ở phiên bản tiếp theo)`);
            };
            
            weekSection.appendChild(exeBtn);
        });

        container.appendChild(weekSection);
    });
}

function setupFeedback() {
    const feedbackBtn = document.getElementById("feedback-btn");
    if (feedbackBtn) {
        feedbackBtn.addEventListener("click", async () => {
            const userMsg = prompt("🎓 Em có thắc mắc gì về bài học hay ngữ pháp? Hãy nhập câu hỏi để Thầy giải đáp nhé:");
            
            if (userMsg && userMsg.trim() !== "") {
                try {
                    const userId = localStorage.getItem("user_id") || 0;
                    
                    const response = await fetch(`${API_BASE_URL}/send_feedback`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            message: userMsg,
                            location: "Không gian học tập chính",
                            user_id: parseInt(userId)
                        })
                    });

                    if (response.ok) {
                        alert("🎉 Tin nhắn thắc mắc của em đã được gửi đi! Thầy sẽ trả lời em sớm nhất.");
                    } else {
                        alert("Không gửi được thắc mắc. Thử lại sau nhé!");
                    }
                } catch (error) {
                    alert("Lỗi kết nối mạng, không gửi được câu hỏi.");
                }
            }
        });
    }
}

function showStatus(element, text, type) {
    element.innerText = text;
    element.className = `message ${type}`;
    element.style.display = "block";
}