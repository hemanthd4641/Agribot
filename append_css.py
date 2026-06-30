import os

css_to_append = """
/* ==========================================================================
   Weather Panel
   ========================================================================== */
.weather-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 340px;
    height: 100vh;
    background-color: var(--bg-main);
    border-left: 1px solid var(--border-color);
    box-shadow: var(--shadow-lg);
    z-index: 50;
    transform: translateX(100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
}

.weather-panel.open {
    transform: translateX(0);
}

.weather-header {
    height: var(--topbar-height);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
    background-color: rgba(9, 9, 11, 0.8);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
}

[data-theme="light"] .weather-header {
    background-color: rgba(255, 255, 255, 0.8);
}

.weather-header h2 {
    font-size: 1rem;
    font-weight: 600;
}

.weather-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.weather-search .search-input-wrapper {
    background-color: var(--bg-surface);
}

.weather-search .icon-btn.small {
    width: 28px;
    height: 28px;
}

/* Weather Cards */
.weather-card {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
}

.weather-current {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
}

.weather-icon-large {
    font-size: 3.5rem;
    color: var(--brand-secondary);
}

.weather-temp {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
    color: var(--text-primary);
}

.weather-desc {
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.weather-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    width: 100%;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
}

.weather-detail-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.weather-detail-item i {
    font-size: 1.2rem;
    color: var(--text-tertiary);
    margin-bottom: 2px;
}

.weather-detail-item span {
    color: var(--text-primary);
    font-weight: 600;
}

/* 7-Day Forecast */
.weather-forecast-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.forecast-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
}

.forecast-item:last-child {
    border-bottom: none;
}

.forecast-day {
    font-size: 0.9rem;
    font-weight: 500;
    width: 40px;
}

.forecast-icon {
    font-size: 1.2rem;
    color: var(--brand-secondary);
    width: 30px;
    text-align: center;
}

.forecast-temp {
    font-size: 0.9rem;
    color: var(--text-primary);
    display: flex;
    gap: 8px;
}

.forecast-temp .min {
    color: var(--text-tertiary);
}

/* Skeleton Loading */
.weather-skeleton {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.skeleton-box {
    background: linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-surface-hover) 50%, var(--bg-surface) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius-md);
    width: 100%;
}

.h-32 { height: 120px; }
.h-24 { height: 80px; }
.h-48 { height: 200px; }
.h-40 { height: 160px; }
.h-64 { height: 260px; }

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@media (max-width: 768px) {
    .weather-panel {
        width: 100%;
    }
}
"""

with open(r"c:\Users\heman\Downloads\LLM_Agri_Bot-main\LLM_Agri_Bot-main\app\static\css\style.css", "a", encoding="utf-8") as f:
    f.write(css_to_append)
print("Done appending CSS")
