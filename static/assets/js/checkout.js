// Global variables
let countiesData = [];
let debugEnabled = true; // Set to false in production

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeCheckout();
});

function initializeCheckout() {
    debug('Starting checkout initialization...');
    
    // Get counties data from Django context
    try {
        countiesData = {{ counties_data|safe }};
        debug('Counties data loaded successfully:', countiesData.length + ' counties');
        
        // Debug: Log the structure of the first county
        if (countiesData.length > 0) {
            debug('First county structure:', countiesData[0]);
        }
        
        // Validate data structure
        if (!Array.isArray(countiesData)) {
            throw new Error('Counties data is not an array');
        }
        
        // Check if counties have the expected structure
        countiesData.forEach((county, index) => {
            if (!county.id || !county.name) {
                debug(`Warning: County at index ${index} missing id or name:`, county);
            }
            if (!county.areas || !Array.isArray(county.areas)) {
                debug(`Warning: County ${county.name} missing or invalid areas:`, county.areas);
            }
        });
        
    } catch (error) {
        debug('Error loading counties data:', error);
        showMessage('Error loading location data. Please refresh the page.', 'error');
        return;
    }
    
    // Validate that required DOM elements exist
    const billingCounty = document.getElementById('id_billing-county');
    const billingArea = document.getElementById('id_billing-delivery_area');
    
    if (!billingCounty) {
        debug('Error: Billing county select not found');
        showMessage('Page not loaded correctly. Please refresh.', 'error');
        return;
    }
    
    if (!billingArea) {
        debug('Error: Billing area select not found');
        showMessage('Page not loaded correctly. Please refresh.', 'error');
        return;
    }
    
    debug('Required DOM elements found');
    
    // Initialize form elements
    setupEventListeners();
    
    // Initialize delivery areas (in case county is pre-selected)
    initializeDeliveryAreas();
    
    debug('Checkout initialization complete');
}

// Add this test function to debug county selection
function testCountySelection() {
    debug('=== Testing County Selection ===');
    const billingCounty = document.getElementById('id_billing-county');
    
    if (billingCounty) {
        debug('Current county value:', billingCounty.value);
        debug('Available options:');
        Array.from(billingCounty.options).forEach((option, index) => {
            debug(`Option ${index}:`, { value: option.value, text: option.textContent });
        });
    }
    
    debug('Counties data:');
    countiesData.forEach(county => {
        debug(`County ID: ${county.id} (${typeof county.id}), Name: ${county.name}, Areas: ${county.areas ? county.areas.length : 'none'}`);
    });
}

function setupEventListeners() {
    debug('Setting up event listeners...');
    
    // Billing address listeners
    const billingCounty = document.getElementById('id_billing-county');
    const billingArea = document.getElementById('id_billing-delivery_area');
    
    if (billingCounty && billingArea) {
        // Enable the delivery area select initially
        billingArea.disabled = false;
        
        billingCounty.addEventListener('change', function(e) {
            debug('Billing county changed to:', this.value);
            populateDeliveryAreas('id_billing-county', 'id_billing-delivery_area');
        });
        
        billingArea.addEventListener('change', function(e) {
            debug('Billing delivery area changed to:', this.value);
            calculateOrderTotals('id_billing-delivery_area', false);
        });
        
        debug('Billing address listeners set up successfully');
    } else {
        debug('Warning: Billing address elements not found');
    }
    
    // Shipping address listeners
    const shippingCounty = document.getElementById('id_shipping-county');
    const shippingArea = document.getElementById('id_shipping-delivery_area');
    
    if (shippingCounty && shippingArea) {
        shippingArea.disabled = false;
        
        shippingCounty.addEventListener('change', function(e) {
            debug('Shipping county changed to:', this.value);
            populateDeliveryAreas('id_shipping-county', 'id_shipping-delivery_area');
        });
        
        shippingArea.addEventListener('change', function(e) {
            debug('Shipping delivery area changed to:', this.value);
            calculateOrderTotals('id_shipping-delivery_area', true);
        });
        
        debug('Shipping address listeners set up successfully');
    }
    
    // Ship to different address toggle
    const shipToDifferent = document.getElementById('ship_to_different');
    const shippingFields = document.getElementById('shipping-fields');
    
    if (shipToDifferent && shippingFields) {
        shipToDifferent.addEventListener('change', function(e) {
            debug('Ship to different address toggled:', this.checked);
            
            if (this.checked) {
                shippingFields.style.display = 'block';
                setFieldsRequired(shippingFields, true);
            } else {
                shippingFields.style.display = 'none';
                setFieldsRequired(shippingFields, false);
                // Recalculate using billing address
                calculateOrderTotals('id_billing-delivery_area', false);
            }
        });
    }
    
    // Create account toggle
    const createAccount = document.getElementById('create_pwd');
    const passwordField = document.getElementById('password-field');
    
    if (createAccount && passwordField) {
        createAccount.addEventListener('change', function(e) {
            debug('Create account toggled:', this.checked);
            
            if (this.checked) {
                passwordField.style.display = 'block';
                const pwdInput = document.getElementById('pwd');
                if (pwdInput) pwdInput.required = true;
            } else {
                passwordField.style.display = 'none';
                const pwdInput = document.getElementById('pwd');
                if (pwdInput) pwdInput.required = false;
            }
        });
    }
    
    // Form submission handler
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', handleFormSubmission);
        debug('Form submission handler attached');
    }
    
    // Modal close handlers
    setupModalHandlers();
    
    debug('All event listeners set up successfully');
}

function initializeDeliveryAreas() {
    // Check if any county is pre-selected and populate areas
    const billingCounty = document.getElementById('id_billing-county');
    if (billingCounty && billingCounty.value) {
        populateDeliveryAreas('id_billing-county', 'id_billing-delivery_area');
    }
    
    const shippingCounty = document.getElementById('id_shipping-county');
    if (shippingCounty && shippingCounty.value) {
        populateDeliveryAreas('id_shipping-county', 'id_shipping-delivery_area');
    }
}

function populateDeliveryAreas(countySelectId, areaSelectId) {
    debug(`Populating delivery areas for county select: ${countySelectId}`);
    
    const countySelect = document.getElementById(countySelectId);
    const areaSelect = document.getElementById(areaSelectId);
    
    if (!countySelect || !areaSelect) {
        debug('Error: Select elements not found', { countySelectId, areaSelectId });
        return;
    }
    
    const selectedCountyId = countySelect.value;
    debug('Selected county ID (raw):', selectedCountyId);
    
    // Clear existing options
    areaSelect.innerHTML = '';
    
    if (!selectedCountyId) {
        // No county selected
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select County First';
        areaSelect.appendChild(defaultOption);
        areaSelect.disabled = true;
        debug('No county selected - area select disabled');
        return;
    }
    
    // Find the selected county data - compare as strings to avoid type issues
    const countyData = countiesData.find(county => county.id.toString() === selectedCountyId.toString());
    
    if (!countyData) {
        debug('Error: County data not found for ID:', selectedCountyId);
        debug('Available county IDs:', countiesData.map(c => c.id));
        
        const errorOption = document.createElement('option');
        errorOption.value = '';
        errorOption.textContent = 'County data not available';
        areaSelect.appendChild(errorOption);
        areaSelect.disabled = true;
        return;
    }
    
    debug('Found county data:', countyData);
    
    if (!countyData.areas || countyData.areas.length === 0) {
        // No delivery areas available
        const noAreasOption = document.createElement('option');
        noAreasOption.value = '';
        noAreasOption.textContent = 'No delivery areas available';
        areaSelect.appendChild(noAreasOption);
        areaSelect.disabled = true;
        debug('No delivery areas available for county:', countyData.name);
        return;
    }
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Delivery Area';
    areaSelect.appendChild(defaultOption);
    
    // Add delivery area options
    countyData.areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.id;
        option.textContent = area.display_name || area.name;
        
        // Store additional data as attributes
        option.setAttribute('data-shipping-fee', area.shipping_fee || 0);
        option.setAttribute('data-delivery-days', area.delivery_days || '');
        option.setAttribute('data-area-name', area.name || '');
        
        areaSelect.appendChild(option);
        debug('Added area option:', area.name);
    });
    
    // Enable the select
    areaSelect.disabled = false;
    
    debug(`Successfully populated ${countyData.areas.length} delivery areas and enabled select`);
    
    // Don't trigger change event automatically to avoid infinite loops
    // The user will select an area which will trigger the calculation
}

function calculateOrderTotals(areaSelectId, isShipping = false) {
    debug(`Calculating order totals for area select: ${areaSelectId}`);
    
    const areaSelect = document.getElementById(areaSelectId);
    
    if (!areaSelect) {
        debug('Error: Area select element not found');
        return;
    }
    
    // Check if we should use this area for calculation
    const shipToDifferent = document.getElementById('ship_to_different');
    const shouldUseThisArea = !isShipping || (shipToDifferent && shipToDifferent.checked);
    
    if (!shouldUseThisArea) {
        debug('Skipping calculation - shipping address not active');
        return;
    }
    
    if (!areaSelect.value) {
        debug('No area selected - resetting totals');
        resetOrderTotals();
        return;
    }
    
    const selectedOption = areaSelect.options[areaSelect.selectedIndex];
    if (!selectedOption) {
        debug('Selected option not found');
        resetOrderTotals();
        return;
    }
    
    // Get shipping data from selected option
    const shippingFee = parseFloat(selectedOption.getAttribute('data-shipping-fee')) || 0;
    const deliveryDays = selectedOption.getAttribute('data-delivery-days') || '';
    const areaName = selectedOption.getAttribute('data-area-name') || selectedOption.textContent;
    
    debug('Area calculation data:', {
        areaName,
        shippingFee,
        deliveryDays
    });
    
    // Get current subtotal
    const subtotalElement = document.getElementById('subtotal-amount');
    const subtotal = subtotalElement ? parseFloat(subtotalElement.textContent) || 0 : 0;
    
    // Calculate totals
    const taxRate = 0.00; // 16% VAT
    const taxAmount = subtotal * taxRate;
    const discountAmount = getDiscountAmount(); // Get current discount if any
    const totalAmount = subtotal + shippingFee + taxAmount - discountAmount;
    
    debug('Calculated totals:', {
        subtotal,
        shippingFee,
        taxAmount,
        discountAmount,
        totalAmount
    });
    
    // Update display elements
    updateElementText('shipping-amount', shippingFee.toFixed(2));
    updateElementText('tax-amount', taxAmount.toFixed(2));
    updateElementText('total-amount', totalAmount.toFixed(2));
    
    // Update shipping info
    const shippingInfoEl = document.getElementById('shipping-info');
    if (shippingInfoEl) {
        let infoText = `to ${areaName}`;
        if (deliveryDays) {
            const days = parseInt(deliveryDays);
            const dayText = days === 1 ? 'day' : 'days';
            infoText += ` (${days} ${dayText})`;
        }
        shippingInfoEl.textContent = infoText;
    }
    
    debug('Order totals updated successfully');
}

function resetOrderTotals() {
    debug('Resetting order totals to default');
    
    updateElementText('shipping-amount', '0.00');
    
    const shippingInfoEl = document.getElementById('shipping-info');
    if (shippingInfoEl) {
        shippingInfoEl.textContent = '';
    }
    
    // Recalculate tax and total without shipping
    const subtotalEl = document.getElementById('subtotal-amount');
    if (subtotalEl) {
        const subtotal = parseFloat(subtotalEl.textContent) || 0;
        const taxAmount = subtotal * 0.16;
        const discountAmount = getDiscountAmount();
        const totalAmount = subtotal + taxAmount - discountAmount;
        
        updateElementText('tax-amount', taxAmount.toFixed(2));
        updateElementText('total-amount', totalAmount.toFixed(2));
    }
}

function getDiscountAmount() {
    const discountEl = document.getElementById('discount-amount');
    return discountEl ? parseFloat(discountEl.textContent) || 0 : 0;
}

function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    } else {
        debug(`Warning: Element not found: ${elementId}`);
    }
}

function setFieldsRequired(container, required) {
    const fields = container.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], select, textarea');
    fields.forEach(field => {
        const label = field.closest('.single-input-item').querySelector('label');
        if (label && label.classList.contains('required')) {
            if (required) {
                field.setAttribute('required', 'required');
            } else {
                field.removeAttribute('required');
            }
        }
    });
    debug(`Set ${fields.length} fields required: ${required}`);
}

function handleFormSubmission(e) {
    debug('Form submission started');
    
    // Clear previous validation states
    const form = e.target;
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
    
    let hasErrors = false;
    
    // Validate required fields
    const requiredFields = form.querySelectorAll('[required]:not([disabled])');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            hasErrors = true;
            debug('Required field empty:', field.name || field.id);
        }
    });
    
    // Validate terms checkbox
    const termsCheckbox = document.getElementById('terms');
    if (termsCheckbox && !termsCheckbox.checked) {
        showMessage('Please accept the terms and conditions to continue.', 'error');
        hasErrors = true;
    }
    
    // Validate delivery area selection
    const shipToDifferent = document.getElementById('ship_to_different');
    const activeAreaSelect = (shipToDifferent && shipToDifferent.checked) 
        ? document.getElementById('id_shipping-delivery_area')
        : document.getElementById('id_billing-delivery_area');
        
    if (activeAreaSelect && !activeAreaSelect.disabled && !activeAreaSelect.value) {
        activeAreaSelect.classList.add('is-invalid');
        showMessage('Please select a delivery area to calculate shipping costs.', 'error');
        hasErrors = true;
    }
    
    if (hasErrors) {
        e.preventDefault();
        debug('Form validation failed');
        
        // Scroll to first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
        return false;
    }
    
    // Check payment method
    const paymentMethod = form.querySelector('input[name="paymentmethod"]:checked');
    if (paymentMethod && paymentMethod.value === 'mpesa') {
        e.preventDefault();
        handleMpesaPayment();
        return false;
    }
    
    debug('Form validation passed - submitting normally');
    return true;
}

function handleMpesaPayment() {
    debug('Handling M-Pesa payment');
    
    showModal('mpesaModal');
    showLoadingState(true);
    
    const form = document.getElementById('checkout-form');
    const formData = new FormData(form);
    
    fetch(form.action || window.location.pathname, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        debug('M-Pesa response status:', response.status);
        return response.json();
    })
    .then(data => {
        debug('M-Pesa response data:', data);
        showLoadingState(false);
        
        if (data.success) {
            updateModalMessage(data.message || 'STK push sent. Please check your phone.', 'success');
            if (data.checkout_request_id) {
                checkPaymentStatus(data.checkout_request_id);
            }
        } else {
            updateModalMessage(data.message || 'Payment failed. Please try again.', 'error');
        }
    })
    .catch(error => {
        debug('M-Pesa payment error:', error);
        showLoadingState(false);
        updateModalMessage('An error occurred. Please try again.', 'error');
    });
}

function checkPaymentStatus(checkoutRequestId) {
    debug('Starting payment status checks for:', checkoutRequestId);
    
    let pollCount = 0;
    const maxPolls = 60; // 5 minutes
    
    function pollStatus() {
        pollCount++;
        debug(`Payment status check ${pollCount}/${maxPolls}`);
        
        const url = `/check-payment-status/?checkout_request_id=${encodeURIComponent(checkoutRequestId)}`;
        
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            debug('Payment status result:', data);
            
            if (data.status === 'SUCCESS') {
                updateModalMessage('Payment completed successfully! Redirecting...', 'success');
                setTimeout(() => {
                    const redirectUrl = data.redirect_url || `/order-confirmation/${data.order_number}/`;
                    window.location.href = redirectUrl;
                }, 2000);
                
            } else if (data.status === 'FAILED') {
                updateModalMessage(data.message || 'Payment failed. Please try again.', 'error');
                setTimeout(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else {
                        location.reload();
                    }
                }, 3000);
                
            } else if (data.status === 'PENDING' && pollCount < maxPolls) {
                updateModalMessage(data.message || 'Please complete the payment on your phone...', 'info');
                setTimeout(pollStatus, 5000);
                
            } else if (pollCount >= maxPolls) {
                updateModalMessage('Payment verification timed out. Please check your M-Pesa messages or contact support.', 'warning');
            } else {
                // Status unknown, continue polling
                setTimeout(pollStatus, 5000);
            }
        })
        .catch(error => {
            debug('Payment status check error:', error);
            if (pollCount < maxPolls) {
                setTimeout(pollStatus, 5000);
            } else {
                updateModalMessage('Unable to verify payment status. Please contact support.', 'error');
            }
        });
    }
    
    pollStatus();
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        debug('Modal shown:', modalId);
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
        debug('Modal hidden:', modalId);
    }
}

function showLoadingState(show) {
    const loading = document.getElementById('mpesa-loading');
    const message = document.getElementById('mpesa-message');
    
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
    
    if (message && show) {
        message.innerHTML = '<p class="text-info">Processing your request...</p>';
    }
}

function updateModalMessage(text, type = 'info') {
    const message = document.getElementById('mpesa-message');
    if (message) {
        const typeClass = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info'
        }[type] || 'text-info';
        
        message.innerHTML = `<p class="${typeClass}">${text}</p>`;
        debug('Modal message updated:', text);
    }
}

function setupModalHandlers() {
    // Close modal buttons
    const closeButtons = document.querySelectorAll('#mpesaModal [data-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => hideModal('mpesaModal'));
    });
    
    // Close modal on backdrop click
    const modal = document.getElementById('mpesaModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideModal('mpesaModal');
            }
        });
    }
    
    debug('Modal handlers set up');
}

function showMessage(text, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${text}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    
    const container = document.querySelector('.checkout-page-wrapper .container');
    if (container) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = alertHtml;
        container.insertBefore(tempDiv.firstElementChild, container.firstElementChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function debug(message, data = null) {
    if (debugEnabled) {
        console.log('[Checkout Debug]', message, data || '');
        
        // Also show in debug info div for troubleshooting
        const debugInfo = document.getElementById('debug-info');
        const debugContent = document.getElementById('debug-content');
        
        if (debugInfo && debugContent) {
            debugInfo.style.display = 'block';
            const timestamp = new Date().toLocaleTimeString();
            const debugLine = document.createElement('div');
            debugLine.innerHTML = `<small>[${timestamp}] ${message} ${data ? JSON.stringify(data) : ''}</small>`;
            debugContent.appendChild(debugLine);
            
            // Keep only last 10 debug messages
            const debugLines = debugContent.children;
            if (debugLines.length > 10) {
                debugContent.removeChild(debugLines[0]);
            }
        }
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCheckout);
} else {
    initializeCheckout();
}