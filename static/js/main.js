/**
 * Intelligent Compliance Automation System
 * Frontend JavaScript
 */

// ===== UTILITY FUNCTIONS =====

/**
 * Fetch with error handling
 */
async function fetchWithErrorHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '400px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// ===== DOM READY =====

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// ===== EVENT LISTENERS =====

function initializeEventListeners() {
    // Add any global event listeners here
    
    // Example: Handle form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('invalid', function() {
            console.log('Form validation error');
        }, true);
    });
}

// ===== FORM HELPERS =====

/**
 * Disable/enable form elements
 */
function setFormDisabled(formId, disabled) {
    const form = document.getElementById(formId);
    if (form) {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(el => {
            el.disabled = disabled;
        });
    }
}

/**
 * Clear form
 */
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

/**
 * Scroll to element smoothly
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ===== DASHBOARD SPECIFIC =====

/**
 * Format validation result
 */
function formatValidationResult(data) {
    return {
        ...data,
        amount_formatted: formatCurrency(data.amount),
        risk_percentage: Math.min(100, data.risk_score)
    };
}

/**
 * Get CSS class for risk level
 */
function getRiskLevelClass(riskLevel) {
    const mapping = {
        'Low': 'success',
        'Medium': 'warning',
        'High': 'danger'
    };
    return mapping[riskLevel] || 'warning';
}

/**
 * Update risk score bar
 */
function updateRiskScoreBar(score, elementId) {
    const bar = document.getElementById(elementId);
    if (bar) {
        const percentage = Math.min(100, score);
        bar.style.width = percentage + '%';
        
        // Update color based on score
        bar.className = 'progress-fill';
        if (percentage <= 33) {
            bar.classList.add('success');
        } else if (percentage <= 66) {
            bar.classList.add('warning');
        } else {
            bar.classList.add('danger');
        }
    }
}

/**
 * Populate table from results
 */
function populateResultsTable(results, tableBodyId) {
    const tbody = document.getElementById(tableBodyId);
    if (!tbody) return;
    
    tbody.innerHTML = results.map(result => `
        <tr>
            <td>${result.email}</td>
            <td>${formatCurrency(result.amount)}</td>
            <td>${result.gst}%</td>
            <td>
                <span class="badge badge-${result.is_compliant ? 'success' : 'danger'}">
                    ${result.status}
                </span>
            </td>
            <td>
                <span class="badge badge-${getRiskLevelClass(result.risk_level)}">
                    ${result.risk_level}
                </span>
            </td>
        </tr>
    `).join('');
}

// ===== CSV UPLOAD HELPERS =====

/**
 * Validate CSV file
 */
function validateCSVFile(file) {
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    if (!file) {
        return { valid: false, error: 'No file selected' };
    }
    
    if (!file.name.endsWith('.csv')) {
        return { valid: false, error: 'Please select a CSV file' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, error: 'File size exceeds 5MB limit' };
    }
    
    return { valid: true };
}

/**
 * Read CSV file (for preview)
 */
function readCSVPreview(file, callback) {
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(event) {
        const csv = event.target.result;
        const lines = csv.split('\n').slice(0, 6); // First 5 rows + header
        callback(lines.join('\n'));
    };
    reader.readAsText(file);
}

// ===== EXPORT FUNCTIONS =====

/**
 * Export data to CSV
 */
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    downloadCSV(csv, filename);
}

/**
 * Convert array to CSV string
 */
function convertToCSV(data) {
    if (!data || !data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csv = [
        headers.join(','),
        ...data.map(row =>
            headers.map(header =>
                JSON.stringify(row[header] || '')
            ).join(',')
        )
    ].join('\n');
    
    return csv;
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ===== REAL-TIME VALIDATION =====

/**
 * Real-time email validation
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Real-time amount validation
 */
function validateAmount(amount) {
    const num = parseFloat(amount);
    return !isNaN(num) && num >= 0;
}

/**
 * Real-time GST validation
 */
function validateGST(gst) {
    const validRates = [5, 12, 18, 28];
    return validRates.includes(parseFloat(gst));
}

// ===== MODAL FUNCTIONS =====

/**
 * Show modal
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
    }
}

/**
 * Hide modal
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ===== STATISTICS =====

/**
 * Calculate compliance statistics
 */
function calculateStats(transactions) {
    return {
        total: transactions.length,
        compliant: transactions.filter(t => t.is_compliant).length,
        nonCompliant: transactions.filter(t => !t.is_compliant).length,
        highRisk: transactions.filter(t => t.risk_level === 'High').length,
        mediumRisk: transactions.filter(t => t.risk_level === 'Medium').length,
        lowRisk: transactions.filter(t => t.risk_level === 'Low').length
    };
}

/**
 * Format statistics for display
 */
function formatStats(stats) {
    return {
        total: stats.total || 0,
        compliantPercent: stats.total ? Math.round((stats.compliant / stats.total) * 100) : 0,
        nonCompliantPercent: stats.total ? Math.round((stats.nonCompliant / stats.total) * 100) : 0,
        highRiskPercent: stats.total ? Math.round((stats.highRisk / stats.total) * 100) : 0
    };
}

// ===== DEBUGGING =====

/**
 * Log with timestamp
 */
function logWithTime(message) {
    const time = new Date().toLocaleTimeString();
    console.log(`[${time}] ${message}`);
}

/**
 * Enable debug mode
 */
function enableDebugMode() {
    window.DEBUG = true;
    console.log('Debug mode enabled');
}

/**
 * Disable debug mode
 */
function disableDebugMode() {
    window.DEBUG = false;
    console.log('Debug mode disabled');
}
