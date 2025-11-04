// app/static/dashboard.js

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    document.getElementById('status-text').innerText = data.status;
  } catch (err) {
    console.error(err);
    document.getElementById('status-text').innerText = 'Error';
  }
}

async function fetchLogs() {
  try {
    const res = await fetch('/api/logs');
    const data = await res.json();
    document.getElementById('log-output').innerText = data.lines.join('\n');
  } catch (err) {
    console.error(err);
  }
}

async function fetchStatsAndRenderChart() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    const labels = data.map(d => d.date);
    const counts = data.map(d => d.count);

    const ctx = document.getElementById('ticketsChart');
    if (!ctx) return;
    // destroy existing chart if any
    if (window.myChart) window.myChart.destroy();
    window.myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Tickets',
          data: counts,
          borderWidth: 1
        }]
      },
      options: {
        scales: { y: { beginAtZero: true } }
      }
    });
  } catch (err) {
    console.error(err);
  }
}

// wire buttons and auto-poll
document.addEventListener('DOMContentLoaded', () => {
  fetchStatus();
  // update status every 5s
  setInterval(fetchStatus, 5000);

  // logs page refresh button
  const refreshBtn = document.getElementById('refresh-logs');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', fetchLogs);
    fetchLogs();
  }

  // analysis page
  if (document.getElementById('ticketsChart')) {
    fetchStatsAndRenderChart();
    // refresh chart every 60s
    setInterval(fetchStatsAndRenderChart, 60 * 1000);
  }
});
