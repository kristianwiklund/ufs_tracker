/**
 * UFS Tracker - Common JavaScript Utilities
 */

// Global tracked charts list
let trackedChartsList = [];

/**
 * Load tracked charts from API
 */
async function loadTrackedCharts() {
    try {
        const response = await fetch('/get_tracked_charts');
        trackedChartsList = await response.json();
        return trackedChartsList;
    } catch (error) {
        console.error('Error loading tracked charts:', error);
        return [];
    }
}

/**
 * Navigate to a specific chart
 */
function navigateToChart(chartIdentifier) {
    const showImplemented = document.querySelector('input[name="show_implemented"]')?.checked ? '1' : '0';
    window.location.href = `/notices?chart_identifier=${encodeURIComponent(chartIdentifier)}&show_implemented=${showImplemented}`;
}

/**
 * Show loading spinner
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

/**
 * Hide loading spinner
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.animation = 'slideIn 0.3s ease-out';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

/**
 * Format date to Swedish format
 */
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('sv-SE');
}

/**
 * Get URL parameter
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Debounce function for search/filter inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Get notice type badge HTML
 */
function getNoticeTypeBadge(noticeType, expiry Date = null) {
    const now = new Date();
    const expiry = expiryDate ? new Date(expiryDate) : null;
    
    if (noticeType === 'temporary') {
        if (expiry && expiry < now) {
            return '<span class="badge badge-expired" title="Expired temporary notice">🔴 T (Expired)</span>';
        }
        return '<span class="badge badge-temporary" title="Temporary notice">🔴 T</span>';
    } else if (noticeType === 'preliminary') {
        return '<span class="badge badge-preliminary" title="Preliminary notice">🟡 P</span>';
    } else {
        return '<span class="badge badge-permanent" title="Permanent correction">🟢</span>';
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Parse affected charts and make them clickable
 */
function makeAffectedChartsClickable(affectedChartsText, trackedCharts) {
    // Split by comma
    const chartRefs = affectedChartsText.split(',').map(s => s.trim()).filter(s => s);
    const results = [];
    
    chartRefs.forEach(chartRef => {
        // Check for concatenation (number + Bsp name)
        const pageMatch = chartRef.match(/^([^\/]+)(\/.*)?$/);
        const mainPart = pageMatch ? pageMatch[1] : chartRef;
        const pageNumbers = pageMatch && pageMatch[2] ? pageMatch[2] : '';
        
        const numberBspMatch = mainPart.match(/^(\d+)(Bsp.+)$/i);
        
        if (numberBspMatch) {
            // Split into two charts
            const chartNumber = numberBspMatch[1];
            const bspName = numberBspMatch[2].trim();
            
            results.push(createChartElement(chartNumber, chartNumber, trackedCharts));
            results.push(createChartElement(bspName + pageNumbers, bspName, trackedCharts));
        } else {
            // Single chart
            const identifier = extractChartIdentifier(chartRef);
            results.push(createChartElement(chartRef, identifier, trackedCharts));
        }
    });
    
    return results.join(', ');
}

/**
 * Extract chart identifier from reference
 */
function extractChartIdentifier(chartRef) {
    const cleaned = chartRef.split('/')[0].trim();
    
    // Number + Bsp pattern
    const numberBspMatch = cleaned.match(/^(\d+)(Bsp.+)$/i);
    if (numberBspMatch) {
        return numberBspMatch[2].trim();
    }
    
    // Bsp pattern
    const bspMatch = cleaned.match(/^(Bsp[^,]+)/i);
    if (bspMatch) {
        return bspMatch[1].trim();
    }
    
    // Just a number
    if (/^\d+$/.test(cleaned)) {
        return cleaned;
    }
    
    return cleaned;
}

/**
 * Create chart element (clickable or plain text)
 */
function createChartElement(displayText, identifier, trackedCharts) {
    const isTracked = trackedCharts.includes(identifier);
    
    if (isTracked) {
        return `<a href="#" class="chart-link" title="Klicka för att visa notiser för ${escapeHtml(identifier)}" onclick="event.preventDefault(); navigateToChart('${escapeHtml(identifier)}');">${escapeHtml(displayText)}</a>`;
    } else {
        return `<span class="chart-not-tracked" title="Detta kort är inte nedladdat än">${escapeHtml(displayText)}</span>`;
    }
}

/**
 * Update implementation status
 */
async function updateImplementationStatus(noticeId, implemented, notes, chartIdentifier) {
    try {
        const response = await fetch(`/update_status/${noticeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                implemented: implemented,
                notes: notes,
                chart_identifier: chartIdentifier
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Status uppdaterad!', 'success');
        } else {
            showAlert('Fel vid uppdatering: ' + result.error, 'error');
        }
        
        return result;
    } catch (error) {
        console.error('Error updating status:', error);
        showAlert('Nätverksfel vid uppdatering', 'error');
        return { success: false, error: error.message };
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
