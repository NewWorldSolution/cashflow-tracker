document.addEventListener('DOMContentLoaded', function () {

  // Helpers: visually lock/unlock fields without using disabled
  // (disabled fields are excluded from form submission)
  function _lockField(field) {
    field.dataset.locked = 'true';
    field.style.opacity = '0.5';
    field.style.pointerEvents = 'none';
  }
  function _unlockField(field) {
    delete field.dataset.locked;
    field.style.opacity = '';
    field.style.pointerEvents = '';
  }

  // 1. Category lookup map — populated by the fetch in step 5d
  let categoryMap = {};

  // 2. Filter category options to match the selected direction
  function filterCategories(direction) {
    const categorySelect = document.querySelector('select[name="category_id"]');
    if (!categorySelect) return;
    Array.from(categorySelect.options).forEach(opt => {
      if (!opt.value) return; // keep the "— select —" placeholder
      const optDir = opt.getAttribute('data-direction');
      opt.hidden = optDir !== direction;
      opt.disabled = optDir !== direction;
    });
    // Reset selection if currently selected option is now hidden
    const selected = categorySelect.options[categorySelect.selectedIndex];
    if (selected && selected.hidden) {
      categorySelect.value = '';
    }
  }

  // 3. Show/hide conditional rows based on direction
  function applyDirection(direction) {
    const isCashIn = direction === 'cash_in';
    const cashInRow = document.getElementById('cash-in-type-row');
    const vatRow = document.getElementById('vat-deductible-row');
    if (cashInRow) cashInRow.style.display = isCashIn ? '' : 'none';
    if (vatRow) vatRow.style.display = isCashIn ? 'none' : '';
    filterCategories(direction);
  }

  // 4. Direction change: apply rows + filter, clear dependent fields, release vat_rate lock
  document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', function () {
      applyDirection(this.value);
      // Clear both dependent fields on every switch
      const it = document.querySelector('select[name="cash_in_type"]');
      if (it) it.value = '';
      const vd = document.querySelector('select[name="vat_deductible_pct"]');
      if (vd) vd.value = '';
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField) _unlockField(vatRateField);
      const paymentField = document.querySelector('select[name="payment_method"]');
      if (paymentField) _unlockField(paymentField);
      // Toggle button active class
      document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
      this.closest('.toggle-btn').classList.add('active');
    });
  });

  // 5. Initialize on page load based on already-checked direction (covers error re-renders)
  const checkedOnLoad = document.querySelector('input[name="direction"]:checked');
  if (checkedOnLoad) {
    applyDirection(checkedOnLoad.value);
  }

  // 5b. Restore cash_in_type=internal locks on load (VAT rate + payment method)
  const cashInTypeOnLoad = document.querySelector('select[name="cash_in_type"]');
  if (cashInTypeOnLoad && cashInTypeOnLoad.value === 'internal') {
    applyInternalLock(true);
  }

  // 5c. Restore card reminder on load
  const paymentOnLoad = document.querySelector('select[name="payment_method"]');
  const reminderOnLoad = document.getElementById('card-reminder');
  if (paymentOnLoad && reminderOnLoad && paymentOnLoad.value === 'card') {
    reminderOnLoad.style.display = '';
  }

  // 5d. Restore desc-required indicator on load (needs categoryMap from fetch)
  fetch('/categories')
    .then(r => r.json())
    .then(cats => {
      cats.forEach(c => { categoryMap[c.category_id] = c; });
      const catSelect = document.querySelector('select[name="category_id"]');
      if (catSelect && catSelect.value) {
        const cat = categoryMap[catSelect.value];
        if (cat) {
          const descReq = document.getElementById('desc-required');
          if (descReq) {
            descReq.style.display = (cat.name === 'other_expense' || cat.name === 'other_income') ? '' : 'none';
          }
        }
      }
    });

  // 6. Category change: set defaults and update desc-required indicator
  const categorySelect = document.querySelector('select[name="category_id"]');
  if (categorySelect) {
    categorySelect.addEventListener('change', function () {
      const cat = categoryMap[this.value];
      if (!cat) return;

      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField && !vatRateField.dataset.locked) {
        vatRateField.value = cat.default_vat_rate;
      }

      const checkedDirection = document.querySelector('input[name="direction"]:checked');
      const isCashOut = checkedDirection && checkedDirection.value === 'cash_out';
      const vdField = document.querySelector('select[name="vat_deductible_pct"]');
      if (vdField && isCashOut && cat.default_vat_deductible_pct != null) {
        vdField.value = cat.default_vat_deductible_pct;
      }

      const descReq = document.getElementById('desc-required');
      if (descReq) {
        descReq.style.display = (cat.name === 'other_expense' || cat.name === 'other_income') ? '' : 'none';
      }
    });
  }

  // 7. cash_in_type change: lock/unlock vat_rate and payment_method
  function applyInternalLock(isInternal) {
    const vatRateField = document.querySelector('select[name="vat_rate"]');
    const paymentField = document.querySelector('select[name="payment_method"]');
    const accountantField = document.querySelector('input[name="for_accountant"]');
    const accountantGroup = accountantField ? accountantField.closest('.form-group') : null;
    if (isInternal) {
      if (vatRateField) { vatRateField.value = '0'; _lockField(vatRateField); }
      if (paymentField) { paymentField.value = 'cash'; _lockField(paymentField); }
      if (accountantField) {
        accountantField.checked = false;
        accountantField.disabled = true;
      }
      if (accountantGroup) {
        accountantGroup.style.display = 'none';
      }
    } else {
      if (vatRateField) _unlockField(vatRateField);
      if (paymentField) _unlockField(paymentField);
      if (accountantField) {
        accountantField.disabled = false;
      }
      if (accountantGroup) {
        accountantGroup.style.display = '';
      }
    }
  }

  const cashInTypeSelect = document.querySelector('select[name="cash_in_type"]');
  if (cashInTypeSelect) {
    cashInTypeSelect.addEventListener('change', function () {
      applyInternalLock(this.value === 'internal');
    });
  }

  // 8. payment_method change: card reminder
  const paymentSelect = document.querySelector('select[name="payment_method"]');
  if (paymentSelect) {
    paymentSelect.addEventListener('change', function () {
      const reminder = document.getElementById('card-reminder');
      if (reminder) {
        reminder.style.display = this.value === 'card' ? '' : 'none';
      }
    });
  }

});
