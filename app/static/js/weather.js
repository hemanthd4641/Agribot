document.addEventListener('DOMContentLoaded', () => {
    const DOM = {
        panel: document.getElementById('weatherPanel'),
        openBtn: document.getElementById('openWeatherBtn'),
        closeBtn: document.getElementById('closeWeatherBtn'),
        searchInput: document.getElementById('weatherSearchInput'),
        searchBtn: document.getElementById('weatherSearchBtn'),
        content: document.getElementById('weatherContent'),
        skeleton: document.getElementById('weatherSkeleton')
    };

    if (!DOM.panel) return;

    // Toggle Panel
    DOM.openBtn.addEventListener('click', () => {
        DOM.panel.classList.add('open');
        if (DOM.content.innerHTML.trim() === '') {
            // First time open, try to get a default city
            fetchWeather('Delhi'); // Default fallback
        }
    });
    
    DOM.closeBtn.addEventListener('click', () => DOM.panel.classList.remove('open'));
    
    // Search
    DOM.searchBtn.addEventListener('click', () => {
        const city = DOM.searchInput.value.trim();
        if (city) fetchWeather(city);
    });
    
    DOM.searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const city = DOM.searchInput.value.trim();
            if (city) fetchWeather(city);
        }
    });

    async function fetchWeather(city) {
        showSkeleton();
        try {
            const response = await fetch(`/weather?city=${encodeURIComponent(city)}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch weather');
            }
            
            renderWeather(data);
        } catch (error) {
            showError(error.message);
        }
    }

    function showSkeleton() {
        DOM.content.classList.add('hidden');
        DOM.skeleton.classList.remove('hidden');
    }

    function renderWeather(data) {
        DOM.skeleton.classList.add('hidden');
        DOM.content.classList.remove('hidden');
        
        const loc = data.location.name;
        const current = data.weather.current;
        const daily = data.weather.daily;
        
        // Map WMO code to icon
        const iconInfo = getWeatherIcon(current.weather_code);
        
        let html = `
            <div class="weather-card">
                <div class="weather-current">
                    <h3 style="margin-bottom: 5px">${loc}</h3>
                    <i class="ph-fill ${iconInfo.icon} weather-icon-large" style="color: ${iconInfo.color}"></i>
                    <div class="weather-temp">${Math.round(current.temperature_2m)}°C</div>
                    <div class="weather-desc">${iconInfo.desc}</div>
                </div>
                
                <div class="weather-details">
                    <div class="weather-detail-item">
                        <i class="ph ph-drop"></i>
                        <span>${current.relative_humidity_2m}%</span>
                        Humid
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-wind"></i>
                        <span>${current.wind_speed_10m} km/h</span>
                        Wind
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-cloud-rain"></i>
                        <span>${current.precipitation} mm</span>
                        Rain
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-sun"></i>
                        <span>${daily.uv_index_max[0] || 0}</span>
                        Max UV
                    </div>
                </div>
            </div>
            
            <div class="weather-card">
                <h4 style="margin-bottom: 15px; font-size: 0.9rem; color: var(--text-secondary)">7-Day Forecast</h4>
                <div class="weather-forecast-list">
        `;
        
        // 7 days loop
        for (let i = 0; i < 7; i++) {
            const date = new Date(daily.time[i]);
            const dayName = i === 0 ? 'Today' : date.toLocaleDateString('en-US', { weekday: 'short' });
            const dIcon = getWeatherIcon(daily.weather_code[i]);
            
            html += `
                <div class="forecast-item">
                    <div class="forecast-day">${dayName}</div>
                    <div class="forecast-icon"><i class="ph-fill ${dIcon.icon}" style="color: ${dIcon.color}"></i></div>
                    <div class="forecast-temp">
                        <span class="max">${Math.round(daily.temperature_2m_max[i])}°</span>
                        <span class="min">${Math.round(daily.temperature_2m_min[i])}°</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--brand-primary); width: 40px; text-align: right">
                        <i class="ph-fill ph-drop"></i> ${daily.precipitation_probability_max[i]}%
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
            
            <div class="weather-card" style="border-color: var(--brand-primary); background-color: rgba(16, 185, 129, 0.05);">
                <h4 style="margin-bottom: 10px; font-size: 0.9rem; color: var(--brand-primary); display: flex; align-items: center; gap: 5px;">
                    <i class="ph-fill ph-leaf"></i> Agri-Insight
                </h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                    ${generateBasicAdvice(current, daily)}
                </p>
                <div style="margin-top: 10px; font-size: 0.75rem; color: var(--text-tertiary); font-style: italic;">
                    * Ask the AI chat for detailed recommendations.
                </div>
            </div>
        `;
        
        DOM.content.innerHTML = html;
    }

    function showError(msg) {
        DOM.skeleton.classList.add('hidden');
        DOM.content.classList.remove('hidden');
        DOM.content.innerHTML = `
            <div class="weather-card" style="border-color: var(--danger); text-align: center; padding: 20px;">
                <i class="ph ph-warning-circle" style="font-size: 2rem; color: var(--danger); margin-bottom: 10px;"></i>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">${msg}</p>
            </div>
        `;
    }

    function getWeatherIcon(code) {
        // WMO Weather interpretation codes
        if (code === 0) return { icon: 'ph-sun', color: '#fbbf24', desc: 'Clear sky' };
        if (code === 1 || code === 2 || code === 3) return { icon: 'ph-cloud-sun', color: '#fcd34d', desc: 'Partly cloudy' };
        if (code === 45 || code === 48) return { icon: 'ph-cloud-fog', color: '#9ca3af', desc: 'Fog' };
        if (code >= 51 && code <= 55) return { icon: 'ph-cloud-drizzle', color: '#60a5fa', desc: 'Drizzle' };
        if (code >= 61 && code <= 65) return { icon: 'ph-cloud-rain', color: '#3b82f6', desc: 'Rain' };
        if (code >= 71 && code <= 77) return { icon: 'ph-cloud-snow', color: '#e5e7eb', desc: 'Snow' };
        if (code >= 80 && code <= 82) return { icon: 'ph-cloud-rain', color: '#2563eb', desc: 'Rain showers' };
        if (code >= 95) return { icon: 'ph-cloud-lightning', color: '#8b5cf6', desc: 'Thunderstorm' };
        return { icon: 'ph-cloud', color: '#9ca3af', desc: 'Cloudy' };
    }

    function generateBasicAdvice(current, daily) {
        let advice = [];
        const maxRainChance = daily.precipitation_probability_max[0];
        const maxWind = daily.wind_speed_10m_max[0];
        const maxTemp = daily.temperature_2m_max[0];
        const minTemp = daily.temperature_2m_min[0];
        
        if (maxRainChance > 70) {
            advice.push("Heavy rain expected. Avoid applying fertilizers or pesticides today.");
        } else if (maxRainChance > 40) {
            advice.push("Moderate chance of rain. Postpone irrigation.");
        }
        
        if (maxWind > 25) {
            advice.push("High wind speeds expected. Not suitable for foliar spraying.");
        }
        
        if (maxTemp > 35 && current.relative_humidity_2m < 40) {
            advice.push("High heat and low humidity. Increase irrigation frequency to prevent crop stress.");
        }
        
        if (minTemp < 5) {
            advice.push("Low temperatures tonight. Protect sensitive crops from frost.");
        }
        
        if (advice.length === 0) {
            advice.push("Weather conditions are favorable for most standard agricultural operations.");
        }
        
        return advice.join(' ');
    }
});
