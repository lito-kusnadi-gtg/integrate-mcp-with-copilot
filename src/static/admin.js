let adminToken = null;
let currentPage = 1;
const logsPerPage = 50;

document.addEventListener("DOMContentLoaded", () => {
  // Check if admin token is stored in sessionStorage (more secure than localStorage)
  const storedToken = sessionStorage.getItem("adminToken");
  if (storedToken) {
    adminToken = storedToken;
    showAdminContent();
  } else {
    showAuthSection();
  }

  // Setup event listeners
  document.getElementById("auth-form").addEventListener("submit", handleAuth);
  document.getElementById("refresh-btn").addEventListener("click", loadAuditLogs);
  document.getElementById("prev-btn").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      loadAuditLogs();
    }
  });
  document.getElementById("next-btn").addEventListener("click", () => {
    currentPage++;
    loadAuditLogs();
  });

  // Update export link with auth header
  updateExportLink();
});

function showAuthSection() {
  document.getElementById("auth-section").style.display = "block";
  document.getElementById("admin-content").style.display = "none";
}

function showAdminContent() {
  document.getElementById("auth-section").style.display = "none";
  document.getElementById("admin-content").style.display = "block";
  loadStats();
  loadAuditLogs();
}

async function handleAuth(event) {
  event.preventDefault();
  const token = document.getElementById("admin-token").value;
  const errorDiv = document.getElementById("auth-error");

  try {
    // Test the token by making a request
    const response = await fetch("/admin/audit-logs?limit=1", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      adminToken = token;
      sessionStorage.setItem("adminToken", token);
      showAdminContent();
      updateExportLink();
    } else {
      errorDiv.textContent = "Invalid admin token";
      errorDiv.style.display = "block";
    }
  } catch (error) {
    errorDiv.textContent = "Authentication failed";
    errorDiv.style.display = "block";
    console.error("Auth error:", error);
  }
}

function updateExportLink() {
  if (adminToken) {
    const exportBtn = document.getElementById("export-btn");
    exportBtn.onclick = async (e) => {
      e.preventDefault();
      try {
        const response = await fetch("/admin/audit-logs/export", {
          headers: {
            Authorization: `Bearer ${adminToken}`,
          },
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "audit_logs.csv";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error("Export error:", error);
        alert("Failed to export logs");
      }
    };
  }
}

async function loadStats() {
  try {
    const response = await fetch("/admin/audit-logs/stats", {
      headers: {
        Authorization: `Bearer ${adminToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load stats");
    }

    const stats = await response.json();
    const statsContainer = document.getElementById("stats-container");
    statsContainer.innerHTML = "";

    // Total logs
    const totalCard = createStatCard("Total Logs", stats.total_logs);
    statsContainer.appendChild(totalCard);

    // Action counts
    if (stats.action_counts) {
      Object.entries(stats.action_counts).forEach(([action, count]) => {
        const card = createStatCard(
          action.charAt(0).toUpperCase() + action.slice(1),
          count
        );
        statsContainer.appendChild(card);
      });
    }

    // Retention period
    const retentionCard = createStatCard(
      "Retention Period",
      `${stats.retention_days} days`
    );
    statsContainer.appendChild(retentionCard);
  } catch (error) {
    console.error("Error loading stats:", error);
  }
}

function createStatCard(title, value) {
  const card = document.createElement("div");
  card.className = "stat-card";
  card.innerHTML = `
    <h4>${title}</h4>
    <p>${value}</p>
  `;
  return card;
}

async function loadAuditLogs() {
  const tbody = document.getElementById("audit-logs-body");
  const pageInfo = document.getElementById("page-info");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  try {
    const offset = (currentPage - 1) * logsPerPage;
    const response = await fetch(
      `/admin/audit-logs?limit=${logsPerPage}&offset=${offset}`,
      {
        headers: {
          Authorization: `Bearer ${adminToken}`,
        },
      }
    );

    if (!response.ok) {
      if (response.status === 403) {
        // Token expired or invalid
        sessionStorage.removeItem("adminToken");
        showAuthSection();
        return;
      }
      throw new Error("Failed to load audit logs");
    }

    const data = await response.json();
    tbody.innerHTML = "";

    if (data.logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No audit logs found</td></tr>';
    } else {
      data.logs.forEach((log) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${log.id}</td>
          <td>${formatTimestamp(log.timestamp)}</td>
          <td><span class="action-badge action-${log.action}">${log.action}</span></td>
          <td>${log.user_email}</td>
          <td>${log.activity_name || "-"}</td>
          <td>${log.details || "-"}</td>
        `;
        tbody.appendChild(row);
      });
    }

    // Update pagination
    const totalPages = Math.ceil(data.total / logsPerPage);
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage >= totalPages || data.logs.length < logsPerPage;
  } catch (error) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Failed to load audit logs</td></tr>';
    console.error("Error loading audit logs:", error);
  }
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  // Include timezone information for clarity
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  });
}
