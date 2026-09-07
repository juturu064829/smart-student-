// Smart Student Management System JavaScript Controller

document.addEventListener("DOMContentLoaded", function () {
    initThemeToggle();
    initSidebarToggle();
    initDashboardCharts();
    initDynamicCalculations();
});

// Theme Switcher (Dark / Light Mode)
function initThemeToggle() {
    const themeBtn = document.getElementById("theme-toggle-btn");
    if (!themeBtn) return;

    const savedTheme = localStorage.getItem("app_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);

    themeBtn.addEventListener("click", function () {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("app_theme", newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const icon = document.querySelector("#theme-toggle-btn i");
    if (!icon) return;
    if (theme === "dark") {
        icon.className = "fa-solid fa-sun text-warning";
    } else {
        icon.className = "fa-solid fa-moon text-primary";
    }
}

// Sidebar toggle on mobile
function initSidebarToggle() {
    const toggleBtn = document.getElementById("sidebar-toggle-btn");
    const sidebar = document.getElementById("sidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }
}

// Render Chart.js dynamic dashboard charts
function initDashboardCharts() {
    const deptChartCtx = document.getElementById("deptEnrollmentChart");
    const genderChartCtx = document.getElementById("genderDistributionChart");

    if (!deptChartCtx && !genderChartCtx) return;

    fetch("/api/dashboard-charts")
        .then(response => response.json())
        .then(data => {
            if (deptChartCtx) {
                new Chart(deptChartCtx, {
                    type: "bar",
                    data: {
                        labels: data.dept_labels,
                        datasets: [{
                            label: "Students Enrolled",
                            data: data.dept_student_counts,
                            backgroundColor: "rgba(99, 102, 241, 0.75)",
                            borderColor: "#6366f1",
                            borderWidth: 2,
                            borderRadius: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, grid: { color: "rgba(255, 255, 255, 0.05)" } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }

            if (genderChartCtx) {
                new Chart(genderChartCtx, {
                    type: "doughnut",
                    data: {
                        labels: ["Male", "Female", "Other"],
                        datasets: [{
                            data: [
                                data.gender_distribution.Male,
                                data.gender_distribution.Female,
                                data.gender_distribution.Other
                            ],
                            backgroundColor: ["#6366f1", "#ec4899", "#06b6d4"],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { position: "bottom" } }
                    }
                });
            }
        })
        .catch(err => console.error("Error loading dashboard charts:", err));
}

// Dynamic form calculations (Salary net amount, Total fee calculation, Total marks)
function initDynamicCalculations() {
    // Total Marks calculation in Marks Entry
    const internalInput = document.getElementById("calc_internal");
    const assignInput = document.getElementById("calc_assignment");
    const practicalInput = document.getElementById("calc_practical");
    const externalInput = document.getElementById("calc_external");
    const totalDisplay = document.getElementById("calc_total_display");

    if (internalInput && assignInput && practicalInput && externalInput && totalDisplay) {
        const inputs = [internalInput, assignInput, practicalInput, externalInput];
        inputs.forEach(input => {
            input.addEventListener("input", function () {
                const total = (parseFloat(internalInput.value) || 0) +
                    (parseFloat(assignInput.value) || 0) +
                    (parseFloat(practicalInput.value) || 0) +
                    (parseFloat(externalInput.value) || 0);
                totalDisplay.innerText = total.toFixed(1);
            });
        });
    }
}
