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

    let currentWeatherData = null;

    if (!DOM.panel) return;

    // Helper for i18n
    function t(key, fallback) {
        if (window.agri_t) return window.agri_t(key, fallback);
        return fallback;
    }

    // Expose this so chat.js can trigger re-render on language change
    window.updateWeatherLang = () => {
        if (currentWeatherData) {
            renderWeather(currentWeatherData);
        }
    };

    // Toggle Panel
    DOM.openBtn.addEventListener('click', () => {
        DOM.panel.classList.add('open');
        if (DOM.content.innerHTML.trim() === '') {
            fetchWeather('Delhi');
        }
    });
    
    DOM.closeBtn.addEventListener('click', () => DOM.panel.classList.remove('open'));
    
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
                throw new Error(data.error || t('error.fetch_weather', 'Failed to fetch weather'));
            }
            
            currentWeatherData = data;
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
                        ${t('weather.humidity', 'Humidity')}
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-wind"></i>
                        <span>${current.wind_speed_10m} km/h</span>
                        ${t('weather.wind', 'Wind')}
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-cloud-rain"></i>
                        <span>${current.precipitation} mm</span>
                        ${t('weather.rain', 'Rain')}
                    </div>
                    <div class="weather-detail-item">
                        <i class="ph ph-sun"></i>
                        <span>${daily.uv_index_max[0] || 0}</span>
                        Max UV
                    </div>
                </div>
            </div>
            
            <div class="weather-card">
                <h4 style="margin-bottom: 15px; font-size: 0.9rem; color: var(--text-secondary)">${t('weather.daily_forecast', '7-Day Forecast')}</h4>
                <div class="weather-forecast-list">
        `;
        
        for (let i = 0; i < 7; i++) {
            const date = new Date(daily.time[i]);
            const isKn = localStorage.getItem('agri-ui-lang') === 'kn';
            
            let dayName = '';
            if (i === 0) {
                dayName = isKn ? 'ಇಂದು' : 'Today';
            } else {
                dayName = date.toLocaleDateString(isKn ? 'kn-IN' : 'en-US', { weekday: 'short' });
            }
            
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
        const isKn = localStorage.getItem('agri-ui-lang') === 'kn';
        const descs = {
            clear: isKn ? 'ಸ್ವಚ್ಛ ಆಕಾಶ' : 'Clear sky',
            partly: isKn ? 'ಭಾಗಶಃ ಮೋಡ' : 'Partly cloudy',
            fog: isKn ? 'ಮಂಜು' : 'Fog',
            drizzle: isKn ? 'ತುಂತುರು ಮಳೆ' : 'Drizzle',
            rain: isKn ? 'ಮಳೆ' : 'Rain',
            snow: isKn ? 'ಹಿಮ' : 'Snow',
            showers: isKn ? 'ಮಳೆ' : 'Rain showers',
            thunder: isKn ? 'ಗುಡುಗು ಸಹಿತ ಮಳೆ' : 'Thunderstorm',
            cloudy: isKn ? 'ಮೋಡ ಕವಿದ ವಾತಾವರಣ' : 'Cloudy'
        };

        if (code === 0) return { icon: 'ph-sun', color: '#fbbf24', desc: descs.clear };
        if (code === 1 || code === 2 || code === 3) return { icon: 'ph-cloud-sun', color: '#fcd34d', desc: descs.partly };
        if (code === 45 || code === 48) return { icon: 'ph-cloud-fog', color: '#9ca3af', desc: descs.fog };
        if (code >= 51 && code <= 55) return { icon: 'ph-cloud-drizzle', color: '#60a5fa', desc: descs.drizzle };
        if (code >= 61 && code <= 65) return { icon: 'ph-cloud-rain', color: '#3b82f6', desc: descs.rain };
        if (code >= 71 && code <= 77) return { icon: 'ph-cloud-snow', color: '#e5e7eb', desc: descs.snow };
        if (code >= 80 && code <= 82) return { icon: 'ph-cloud-rain', color: '#2563eb', desc: descs.showers };
        if (code >= 95) return { icon: 'ph-cloud-lightning', color: '#8b5cf6', desc: descs.thunder };
        return { icon: 'ph-cloud', color: '#9ca3af', desc: descs.cloudy };
    }

    function generateBasicAdvice(current, daily) {
        const isKn = localStorage.getItem('agri-ui-lang') === 'kn';
        let advice = [];
        const maxRainChance = daily.precipitation_probability_max[0];
        const maxWind = daily.wind_speed_10m_max[0];
        const maxTemp = daily.temperature_2m_max[0];
        const minTemp = daily.temperature_2m_min[0];
        
        if (maxRainChance > 70) {
            advice.push(isKn ? "ಭಾರೀ ಮಳೆಯ ನಿರೀಕ್ಷೆಯಿದೆ. ಇಂದು ರಸಗೊಬ್ಬರ ಅಥವಾ ಕೀಟನಾಶಕಗಳನ್ನು ಬಳಸಬೇಡಿ." : "Heavy rain expected. Avoid applying fertilizers or pesticides today.");
        } else if (maxRainChance > 40) {
            advice.push(isKn ? "ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆ ಇದೆ. ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ." : "Moderate chance of rain. Postpone irrigation.");
        }
        
        if (maxWind > 25) {
            advice.push(isKn ? "ಹೆಚ್ಚಿನ ಗಾಳಿಯ ವೇಗ. ಸಿಂಪರಣೆಗೆ ಸೂಕ್ತವಲ್ಲ." : "High wind speeds expected. Not suitable for foliar spraying.");
        }
        
        if (maxTemp > 35 && current.relative_humidity_2m < 40) {
            advice.push(isKn ? "ಹೆಚ್ಚಿನ ತಾಪಮಾನ. ಬೆಳೆಗಳಿಗೆ ಹೆಚ್ಚು ನೀರುಣಿಸಿ." : "High heat and low humidity. Increase irrigation frequency to prevent crop stress.");
        }
        
        if (minTemp < 5) {
            advice.push(isKn ? "ಕಡಿಮೆ ತಾಪಮಾನ. ಚಳಿಯಿಂದ ಬೆಳೆಗಳನ್ನು ರಕ್ಷಿಸಿ." : "Low temperatures tonight. Protect sensitive crops from frost.");
        }
        
        if (advice.length === 0) {
            advice.push(isKn ? "ಕೃಷಿ ಚಟುವಟಿಕೆಗಳಿಗೆ ಹವಾಮಾನ ಅನುಕೂಲಕರವಾಗಿದೆ." : "Weather conditions are favorable for most standard agricultural operations.");
        }
        
        return advice.join(' ');
    }
});
