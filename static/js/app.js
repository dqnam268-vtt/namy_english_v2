// ==========================================
// CẤU HÌNH API (MÔ HÌNH V2 MONOLITH)
// ==========================================
// Tự động lấy tên miền hiện tại (dù là localhost hay render.com) và ghép với /api
const API_BASE_URL = window.location.origin + "/api";

// ==========================================
// BỘ ĐIỀU HƯỚNG TỰ ĐỘNG (ROUTER)
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;

    // 1. Kiểm tra URL để chạy đúng chức năng cho từng trang
    if (currentPath === "/" || currentPath === "/index.html" || currentPath === "") {
        initLoginPage();
    } else if (currentPath === "/admin" || currentPath === "/admin.html") {
        checkAuth("admin"); // Bảo vệ: Chỉ Thầy Nam (admin) mới được vào
        initAdminPage();
    } else if (currentPath === "/student" || currentPath === "/student.html") {
        checkAuth("student"); // Bảo vệ: Chỉ học sinh mới được vào
        initStudentPage();
    }

    // 2. Kích hoạt nút đăng xuất (nếu có trên trang)
    setupLogoutButton();
});

// ==========================================
// HỆ THỐNG BẢO VỆ VÀ PHÂN QUYỀN
// ==========================================
function checkAuth(requiredRole) {
    const role = localStorage.getItem("user_role");
    const userId = localStorage.getItem("user_id");

    // Nếu chưa đăng nhập hoặc sai vai trò -> Đá văng ra Cổng trường
    if (!userId || !role || role !== requiredRole) {
        alert("⚠️ Bạn không có quyền truy cập trang này. Vui lòng đăng nhập!");
        window.location.href = "/";
    }
}

function setupLogoutButton() {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.clear(); // Xóa sạch trí nhớ trình duyệt
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

    // Tự động chuyển trang nếu đã đăng nhập từ trước
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
                    // Lưu thẻ ra vào vào bộ nhớ trình duyệt
                    localStorage.setItem("user_id", data.user_id);
                    localStorage.setItem("user_role", data.role);
                    localStorage.setItem("username", data.username);

                    // Điều hướng thông minh dựa trên phân quyền
                    if (data.role === "admin") {
                        window.location.href = "/admin";
                    } else {
                        window.location.href = "/student";
                    }
                } else {
                    showError(errorMsg, data.detail || "Sai tên đăng nhập hoặc mật khẩu!");
                }
            } catch (error) {
                console.error("Lỗi đăng nhập:", error);
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
    // 1. Hiển thị tên Admin
    const adminNameSpan = document.getElementById("admin-name");
    if (adminNameSpan) adminNameSpan.innerText = "Thầy " + (localStorage.getItem("username") || "Nam");

    // 2. Logic Cấp tài khoản Học sinh
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
                    showStatus(regMsg, `✅ Tạo thành công tài khoản: ${username}`, "success");
                    userInp.value = "";
                    passInp.value = "";
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

    // 3. Logic Bơm dữ liệu bài học mẫu
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
            } catch (error) {
                showStatus(seedMsg, "Lỗi kết nối máy chủ!", "error");
            } finally {
                seedBtn.disabled = false;
                seedBtn.innerText = "Bơm Dữ Liệu Bài Học Mẫu";
            }
        });
    }
}

// ==========================================
// LOGIC: TRANG HỌC SINH (STUDENT.HTML)
// ==========================================
function initStudentPage() {
    // 1. Hiển thị tên Học sinh
    const studentNameSpan = document.getElementById("student-name");
    if (studentNameSpan) studentNameSpan.innerText = localStorage.getItem("username") || "Học sinh";

    // 2. Kích hoạt lấy bài học và form hỏi đáp
    fetchCourseSyllabus();
    setupFeedback();
}

// Gọi API lấy lộ trình
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

// Vẽ giao diện Tuần học ra màn hình
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
            
            // Xử lý khi nhấn vào bài tập
            exeBtn.onclick = () => {
                let activityList = exe.activities.map((act, index) => `Hoạt động ${index + 1}: ${act}`).join("\n");
                alert(`📖 Em đang mở: ${exe.title}\n\nNhiệm vụ:\n${activityList || "Chưa có hoạt động nào"}\n\n(Chức năng làm bài đang được NamY hoàn thiện ở phiên bản tiếp theo)`);
            };
            
            weekSection.appendChild(exeBtn);
        });

        container.appendChild(weekSection);
    });
}

// Gọi API Gửi thắc mắc cho giáo viên
function setupFeedback() {
    const feedbackBtn = document.getElementById("feedback-btn");
    if (feedbackBtn) {
        feedbackBtn.addEventListener("click", async () => {
            const userMsg = prompt("🎓 Em có thắc mắc gì về bài học hay ngữ pháp? Hãy nhập câu hỏi để Thầy giải đáp nhé:");
            
            if (userMsg && userMsg.trim() !== "") {
                try {
                    // Tự động lấy ID của học sinh đang đăng nhập
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

// Hàm hỗ trợ hiển thị thông báo chung
function showStatus(element, text, type) {
    element.innerText = text;
    element.className = `message ${type}`;
    element.style.display = "block";
}