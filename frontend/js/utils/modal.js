/**
 * Modal System - Centralized modal management
 * Replaces inline modal code from index.html
 */

const ModalSystem = (function () {
  'use strict';

  // State
  let activeModal = null;
  let previousActiveElement = null;

  /**
   * Open a modal
   * @param {string} modalId - ID of the modal element
   * @param {object} options - Modal options
   */
  function open(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.error(`Modal not found: ${modalId}`);
      return;
    }

    // Store previously focused element for accessibility
    previousActiveElement = document.activeElement;

    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex', 'active');

    // Lock body scroll
    document.body.style.overflow = 'hidden';

    activeModal = modal;

    // Focus first focusable element
    const focusable = modal.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable) {
      setTimeout(() => focusable.focus(), 100);
    }

    // Emit custom event
    modal.dispatchEvent(new CustomEvent('modal:open', { detail: options }));

    console.log(`✅ Modal opened: ${modalId}`);
  }

  /**
   * Close a modal
   * @param {string} modalId - ID of the modal element (optional, closes active if not provided)
   */
  function close(modalId) {
    let modal;

    if (modalId) {
      modal = document.getElementById(modalId);
    } else {
      modal = activeModal;
    }

    if (!modal) return;

    modal.classList.add('hidden');
    modal.classList.remove('flex', 'active');

    // Unlock body scroll
    document.body.style.overflow = '';

    if (activeModal === modal) {
      activeModal = null;
    }

    // Restore focus
    if (previousActiveElement) {
      previousActiveElement.focus();
      previousActiveElement = null;
    }

    // Emit custom event
    modal.dispatchEvent(new CustomEvent('modal:close'));

    console.log(`✅ Modal closed: ${modal.id}`);
  }

  /**
   * Close all open modals
   */
  function closeAll() {
    document.querySelectorAll('.modal, [id$="Modal"]').forEach(modal => {
      if (!modal.classList.contains('hidden')) {
        close(modal.id);
      }
    });
  }

  /**
   * Check if a modal is open
   * @param {string} modalId - ID of the modal element
   * @returns {boolean}
   */
  function isOpen(modalId) {
    const modal = document.getElementById(modalId);
    return modal && !modal.classList.contains('hidden');
  }

  /**
   * Initialize modal close handlers
   */
  function init() {
    // Close on backdrop click
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal') ||
        e.target.closest('[id$="Modal"]')?.classList.contains('fixed')) {
        const modal = e.target.closest('[id$="Modal"]');
        if (modal && !modal.classList.contains('hidden')) {
          close(modal.id);
        }
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && activeModal) {
        close(activeModal.id);
      }
    });

    // Close buttons
    document.querySelectorAll('[id*="closeModal"], .close-modal, [data-close-modal]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const modal = btn.closest('[id$="Modal"]');
        if (modal) {
          close(modal.id);
        }
      });
    });

    console.log('✅ ModalSystem initialized');
  }

  // Public API
  return {
    open,
    close,
    closeAll,
    isOpen,
    init,
    getActive: () => activeModal
  };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', ModalSystem.init);
} else {
  ModalSystem.init();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ModalSystem;
}
