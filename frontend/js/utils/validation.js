/**
 * Form Validation - Reusable form validation utilities
 * Replaces inline form validation code
 */

const FormValidation = (function () {
  'use strict';

  // Validation rules
  const rules = {
    required: {
      validate: (value) => value && value.trim().length > 0,
      message: 'Ovo polje je obavezno'
    },
    email: {
      validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
      message: 'Unesite validnu email adresu'
    },
    minLength: {
      validate: (value, min) => value && value.length >= min,
      message: (min) => `Minimalno ${min} karaktera`
    },
    maxLength: {
      validate: (value, max) => !value || value.length <= max,
      message: (max) => `Maksimalno ${max} karaktera`
    },
    password: {
      validate: (value) => value && value.length >= 8,
      message: 'Lozinka mora imati najmanje 8 karaktera'
    },
    passwordMatch: {
      validate: (value, matchValue) => value === matchValue,
      message: 'Lozinke se ne poklapaju'
    },
    phone: {
      validate: (value) => !value || /^[\d\s\+\-\(\)]+$/.test(value),
      message: 'Unesite validan broj telefona'
    },
    url: {
      validate: (value) => !value || /^https?:\/\/.+/.test(value),
      message: 'Unesite validan URL'
    }
  };

  /**
   * Validate a single field
   * @param {HTMLInputElement} input - Input element
   * @param {object} fieldRules - Validation rules for this field
   * @returns {object} - { valid: boolean, message: string }
   */
  function validateField(input, fieldRules) {
    const value = input.value;
    const errors = [];

    for (const [ruleName, ruleValue] of Object.entries(fieldRules)) {
      const rule = rules[ruleName];
      if (!rule) continue;

      let isValid;
      let message;

      if (ruleName === 'minLength') {
        isValid = rule.validate(value, ruleValue);
        message = rule.message(ruleValue);
      } else if (ruleName === 'maxLength') {
        isValid = rule.validate(value, ruleValue);
        message = rule.message(ruleValue);
      } else if (ruleName === 'passwordMatch') {
        const matchInput = document.querySelector(ruleValue);
        isValid = rule.validate(value, matchInput ? matchInput.value : '');
        message = rule.message;
      } else if (typeof ruleValue === 'boolean' && ruleValue) {
        isValid = rule.validate(value);
        message = rule.message;
      } else if (typeof ruleValue === 'string') {
        isValid = rule.validate(value, ruleValue);
        message = rule.message;
      }

      if (!isValid) {
        errors.push(message);
      }
    }

    return {
      valid: errors.length === 0,
      message: errors.join(', ')
    };
  }

  /**
   * Show error on input
   * @param {HTMLInputElement} input - Input element
   * @param {string} message - Error message
   */
  function showError(input, message) {
    const formGroup = input.closest('.form-group') || input.parentElement;

    // Remove existing error
    const existingError = formGroup.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }

    // Add error class
    input.classList.add('border-red-500', 'focus:border-red-500');
    input.classList.remove('border-gray-200', 'focus:border-primary-blue');

    // Create error element
    const errorElement = document.createElement('p');
    errorElement.className = 'error-message text-red-500 text-sm mt-1';
    errorElement.textContent = message;

    formGroup.appendChild(errorElement);
  }

  /**
   * Clear error on input
   * @param {HTMLInputElement} input - Input element
   */
  function clearError(input) {
    const formGroup = input.closest('.form-group') || input.parentElement;

    // Remove existing error
    const existingError = formGroup.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }

    // Remove error class
    input.classList.remove('border-red-500', 'focus:border-red-500');
    input.classList.add('border-gray-200', 'focus:border-primary-blue');
  }

  /**
   * Validate entire form
   * @param {HTMLFormElement} form - Form element
   * @param {object} formConfig - Form configuration with field rules
   * @returns {boolean} - Whether form is valid
   */
  function validateForm(form, formConfig) {
    let isValid = true;
    const errors = [];

    for (const [fieldName, fieldRules] of Object.entries(formConfig)) {
      const input = form.querySelector(`[name="${fieldName}"]`);
      if (!input) continue;

      const result = validateField(input, fieldRules);

      if (!result.valid) {
        isValid = false;
        errors.push({ field: fieldName, message: result.message });
        showError(input, result.message);
      } else {
        clearError(input);
      }
    }

    // Dispatch custom event
    form.dispatchEvent(new CustomEvent('form:validation', {
      detail: { valid: isValid, errors }
    }));

    return isValid;
  }

  /**
   * Initialize form validation
   * @param {string} formSelector - CSS selector for form
   * @param {object} formConfig - Form configuration
   */
  function initForm(formSelector, formConfig) {
    const form = document.querySelector(formSelector);
    if (!form) {
      console.warn(`Form not found: ${formSelector}`);
      return;
    }

    // Add submit handler
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const isValid = validateForm(form, formConfig);

      if (isValid) {
        form.dispatchEvent(new CustomEvent('form:valid', { bubbles: true }));
      } else {
        form.dispatchEvent(new CustomEvent('form:invalid', { bubbles: true }));
      }
    });

    // Add blur validation for each field
    for (const fieldName of Object.keys(formConfig)) {
      const input = form.querySelector(`[name="${fieldName}"]`);
      if (!input) continue;

      input.addEventListener('blur', () => {
        const result = validateField(input, formConfig[fieldName]);
        if (!result.valid) {
          showError(input, result.message);
        } else {
          clearError(input);
        }
      });

      // Clear error on input
      input.addEventListener('input', () => {
        clearError(input);
      });
    }

    console.log(`✅ FormValidation initialized: ${formSelector}`);
  }

  // Public API
  return {
    validateField,
    validateForm,
    showError,
    clearError,
    initForm,
    rules
  };
})();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormValidation;
}
