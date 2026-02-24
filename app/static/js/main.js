/**
 * HemoVision AI – Main JavaScript
 * =================================
 * Handles form validation, AJAX prediction, result rendering,
 * and SHAP chart visualization.
 */

// ─── DOM Ready ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initFormValidation();
    initSmoothScroll();
    initAOSFallback();
});

// ─── Navbar Scroll Effect ────────────────────────────────────────────
function initNavbar() {
    const navbar = document.querySelector('.navbar-custom');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
}

// ─── Smooth Scroll ───────────────────────────────────────────────────
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// ─── AOS Fallback (if AOS library not loaded) ────────────────────────
function initAOSFallback() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100,
            easing: 'ease-out-cubic'
        });
    }
}

// ─── Form Validation ─────────────────────────────────────────────────
function initFormValidation() {
    const form = document.getElementById('assessmentForm');
    if (!form) return;

    const fields = {
        hemoglobin: { min: 2, max: 25, name: 'Hemoglobin' },
        mch: { min: 10, max: 45, name: 'MCH' },
        mchc: { min: 20, max: 42, name: 'MCHC' },
        mcv: { min: 40, max: 120, name: 'MCV' },
        age: { min: 1, max: 120, name: 'Age' }
    };

    // Real-time validation
    Object.keys(fields).forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (!input) return;

        input.addEventListener('input', () => {
            validateField(input, fields[fieldId]);
            updateSubmitButton(form);
        });

        input.addEventListener('blur', () => {
            validateField(input, fields[fieldId]);
        });
    });

    // Gender change → toggle pregnancy field
    const genderSelect = document.getElementById('gender');
    const pregnantGroup = document.getElementById('pregnantGroup');
    if (genderSelect && pregnantGroup) {
        genderSelect.addEventListener('change', function () {
            const isFemale = this.value === '1';
            pregnantGroup.style.display = isFemale ? 'block' : 'none';
            if (!isFemale) {
                document.getElementById('pregnant').value = '0';
            }
        });
    }

    // Form submission via AJAX
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate all fields
        let isValid = true;
        Object.keys(fields).forEach(fieldId => {
            const input = document.getElementById(fieldId);
            if (input && !validateField(input, fields[fieldId])) {
                isValid = false;
            }
        });

        if (!isValid) return;

        await submitPrediction(form);
    });
}

function validateField(input, config) {
    const value = parseFloat(input.value);
    const feedback = input.nextElementSibling;

    if (input.value === '' || isNaN(value)) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = `${config.name} is required`;
        }
        return false;
    }

    if (value < config.min || value > config.max) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = `${config.name} must be between ${config.min} and ${config.max}`;
        }
        return false;
    }

    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    return true;
}

function updateSubmitButton(form) {
    const submitBtn = form.querySelector('.submit-btn');
    const invalidFields = form.querySelectorAll('.is-invalid');
    const emptyRequired = form.querySelectorAll('input[required]');
    let hasEmpty = false;
    emptyRequired.forEach(f => { if (!f.value) hasEmpty = true; });

    if (submitBtn) {
        submitBtn.disabled = invalidFields.length > 0 || hasEmpty;
    }
}

// ─── AJAX Prediction ─────────────────────────────────────────────────
async function submitPrediction(form) {
    const loading = document.getElementById('loadingOverlay');
    const resultSection = document.getElementById('resultSection');

    // Show loading
    if (loading) loading.classList.add('active');

    try {
        const formData = new FormData(form);
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Prediction failed');

        const html = await response.text();

        // Parse the response HTML to extract the result section
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newResult = doc.getElementById('resultSection');

        if (newResult && resultSection) {
            resultSection.innerHTML = newResult.innerHTML;
            resultSection.classList.add('show');
            resultSection.style.display = 'block';

            // Scroll to result
            setTimeout(() => {
                resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);

            // Initialize SHAP chart
            initSHAPChart();

            // Animate confidence ring
            animateConfidenceRing();
        }

    } catch (error) {
        console.error('Prediction error:', error);
        alert('An error occurred during prediction. Please try again.');
    } finally {
        if (loading) loading.classList.remove('active');
    }
}

// ─── SHAP Feature Importance Chart ───────────────────────────────────
function initSHAPChart() {
    const chartCanvas = document.getElementById('shapChart');
    if (!chartCanvas) return;

    const dataStr = chartCanvas.getAttribute('data-features');
    if (!dataStr) return;

    try {
        const featureData = JSON.parse(dataStr);
        const labels = Object.keys(featureData);
        const values = Object.values(featureData);

        // Sort by importance
        const sorted = labels.map((label, i) => ({ label, value: values[i] }))
            .sort((a, b) => b.value - a.value);

        const colors = sorted.map((_, i) => {
            const gradient = [
                'rgba(26, 86, 219, 0.8)',
                'rgba(59, 130, 246, 0.7)',
                'rgba(14, 165, 233, 0.7)',
                'rgba(6, 182, 212, 0.6)',
                'rgba(99, 102, 241, 0.6)',
                'rgba(139, 92, 246, 0.5)',
                'rgba(168, 85, 247, 0.4)'
            ];
            return gradient[i] || gradient[6];
        });

        new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: sorted.map(s => s.label),
                datasets: [{
                    label: 'Feature Importance (%)',
                    data: sorted.map(s => s.value),
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace(/[\d.]+\)$/, '1)')),
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.7
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleFont: { weight: '600' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: (ctx) => `Importance: ${ctx.raw.toFixed(1)}%`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: {
                            callback: (v) => v + '%',
                            font: { size: 11 }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { font: { size: 12, weight: '500' } }
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                }
            }
        });
    } catch (e) {
        console.error('SHAP chart error:', e);
    }
}

// ─── Confidence Ring Animation ───────────────────────────────────────
function animateConfidenceRing() {
    const ring = document.querySelector('.ring-fill');
    if (!ring) return;

    const confidence = parseFloat(ring.getAttribute('data-confidence') || 0);
    const circumference = 314; // 2 * π * 50
    const offset = circumference - (confidence / 100) * circumference;

    setTimeout(() => {
        ring.style.strokeDashoffset = offset;
    }, 300);
}

// ─── Page load initialization for result pages ──────────────────────
window.addEventListener('load', () => {
    // If there's a SHAP chart on page load (result.html page)
    initSHAPChart();
    animateConfidenceRing();

    // Initialize progress bars animation
    document.querySelectorAll('.progress-bar-custom .fill').forEach(bar => {
        const target = bar.getAttribute('data-width');
        if (target) {
            setTimeout(() => {
                bar.style.width = target + '%';
            }, 500);
        }
    });
});
