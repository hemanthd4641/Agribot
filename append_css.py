import os

css_content = """
/* ========================================================================== */
/* RESPONSIVE DESIGN & MOBILE OPTIMIZATIONS                                   */
/* ========================================================================== */

:root {
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
    --safe-left: env(safe-area-inset-left, 0px);
    --safe-right: env(safe-area-inset-right, 0px);
}

/* Base Accessibility & Touch Targets */
button, .icon-btn, .form-select, .chat-item, .theme-option {
    min-height: 44px;
    min-width: 44px;
}
.icon-btn.small {
    min-height: 36px;
    min-width: 36px;
}

/* Typography & Layout Fixes for Mobile */
.chat-messages {
    overflow-x: hidden;
}
.message-bubble {
    word-break: break-word;
    overflow-wrap: break-word;
    line-height: 1.6;
}
pre {
    max-width: 100%;
    overflow-x: auto;
}

/* Mobile: Single Column & Hamburger */
@media (max-width: 767px) {
    .app-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
    }
    
    .sidebar {
        position: fixed;
        left: -100%;
        top: 0;
        bottom: 0;
        width: 85%;
        max-width: 320px;
        z-index: 1000;
        transition: left 0.3s ease;
        padding-top: var(--safe-top);
        padding-bottom: var(--safe-bottom);
        box-shadow: 4px 0 20px rgba(0,0,0,0.5);
    }
    
    .sidebar.mobile-open {
        left: 0;
    }
    
    .mobile-close-btn, .mobile-menu-btn {
        display: flex !important;
    }
    
    .main-content {
        flex: 1;
        width: 100%;
        padding-top: var(--safe-top);
    }

    .topbar {
        padding: 10px;
    }
    
    .weather-panel {
        position: fixed;
        right: -100%;
        top: 0;
        bottom: 0;
        width: 100%;
        z-index: 1001;
        transition: right 0.3s ease;
        padding-top: var(--safe-top);
    }
    
    .weather-panel.open {
        right: 0;
    }
    
    .feature-cards {
        grid-template-columns: 1fr;
        gap: 12px;
    }
    
    .input-container {
        padding-bottom: calc(1rem + var(--safe-bottom));
        padding-left: var(--safe-left);
        padding-right: var(--safe-right);
    }
    
    .chat-area {
        height: calc(100vh - 60px - 140px - var(--safe-top) - var(--safe-bottom));
    }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1024px) {
    .app-container {
        grid-template-columns: 240px 1fr;
    }
    .feature-cards {
        grid-template-columns: repeat(2, 1fr);
    }
    .weather-panel {
        width: 300px;
    }
    .mobile-close-btn, .mobile-menu-btn {
        display: none !important;
    }
}

/* Desktop */
@media (min-width: 1025px) {
    .mobile-menu-btn, .mobile-close-btn {
        display: none !important;
    }
}

/* Extra Large */
@media (min-width: 1440px) {
    .app-container {
        max-width: 1920px;
        margin: 0 auto;
    }
}
