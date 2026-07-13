// Dashboard Analytics and Streaks Calendar Rendering

document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardStats();
});

function fetchDashboardStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            renderContributionCalendar(data.calendar);
            renderWeeklyChart(data.weekly);
            updateDailyGoalTracker(data.today_count, data.daily_goal);
        })
        .catch(err => console.error("Error loading dashboard data:", err));
}

// 1. Render GitHub-style calendar grid (Past 180 days)
function renderContributionCalendar(calendarData) {
    const gridContainer = document.getElementById('streakCalendarGrid');
    if (!gridContainer) return;
    gridContainer.innerHTML = '';
    
    // Generate dates list for the past 182 days (26 weeks) to align rows cleanly
    const datesList = [];
    const today = new Date();
    
    // We want the calendar to end on today.
    // Let's find the start date (181 days ago)
    const startDate = new Date();
    startDate.setDate(today.getDate() - 181);
    
    // Loop and construct date blocks
    let tempDate = new Date(startDate);
    while (tempDate <= today) {
        datesList.push(new Date(tempDate));
        tempDate.setDate(tempDate.getDate() + 1);
    }
    
    datesList.forEach(itemDate => {
        const dateStr = formatDateString(itemDate);
        const count = calendarData[dateStr] || 0;
        
        const cell = document.createElement('div');
        cell.className = `calendar-cell ${getContributionLevelClass(count)}`;
        
        // Formulate tooltip
        const formattedDateLabel = itemDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        cell.setAttribute('data-tooltip', `${count} cards reviewed on ${formattedDateLabel}`);
        
        gridContainer.appendChild(cell);
    });
}

function formatDateString(dateObj) {
    const year = dateObj.getFullYear();
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const day = dateObj.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function getContributionLevelClass(count) {
    if (count === 0) return 'level-0';
    if (count < 4) return 'level-1';
    if (count < 10) return 'level-2';
    return 'level-3';
}

// 2. Render Chart.js Weekly progress bar chart
function renderWeeklyChart(weeklyData) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;
    
    // Determine chart theme color based on theme settings
    const isLightTheme = document.body.classList.contains('light-theme');
    const gridColor = isLightTheme ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
    const textColor = isLightTheme ? '#4b5563' : '#9ca3af';
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeklyData.labels,
            datasets: [{
                label: 'Cards Reviewed',
                data: weeklyData.counts,
                backgroundColor: 'rgba(120, 76, 251, 0.55)',
                borderColor: 'rgb(120, 76, 251)',
                borderWidth: 1.5,
                borderRadius: 6,
                hoverBackgroundColor: 'rgba(120, 76, 251, 0.85)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: textColor }
                },
                y: {
                    grid: { color: gridColor },
                    ticks: {
                        color: textColor,
                        stepSize: 1,
                        beginAtZero: true
                    }
                }
            }
        }
    });
}

// 3. Keep Daily Goal status labels updated
function updateDailyGoalTracker(todayCount, dailyGoal) {
    const badgeText = document.getElementById('dailyGoalText');
    if (badgeText) {
        badgeText.textContent = `${todayCount} / ${dailyGoal}`;
    }
}
