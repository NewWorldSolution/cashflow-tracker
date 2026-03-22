document.addEventListener('DOMContentLoaded', function () {

  // Helpers: visually lock/unlock vat_rate without using disabled
  // (disabled fields are excluded from form submission)
  function _lockVatRate(field) {
    field.dataset.locked = 'true';
    field.style.opacity = '0.5';
    field.style.pointerEvents = 'none';
  }
  function _unlockVatRate(field) {
    delete field.dataset.locked;
    field.style.opacity = '';
    field.style.pointerEvents = '';
  }

  // 1. Fetch /categories on load and build lookup map
  //    Response fields: category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
  let categoryMap = {};
  fetch('/categories')
    .then(r => r.json())
    .then(cats => {
      cats.forEach(c => { categoryMap[c.category_id] = c; });
    });

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
    const isIncome = direction === 'income';
    const incomeRow = document.getElementById('income-type-row');
    const vatRow = document.getElementById('vat-deductible-row');
    if (incomeRow) incomeRow.style.display = isIncome ? '' : 'none';
    if (vatRow) vatRow.style.display = isIncome ? 'none' : '';
    filterCategories(direction);
  }

  // 4. Direction change: apply rows + filter, clear dependent fields, release vat_rate lock
  document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', function () {
      applyDirection(this.value);
      // Clear both dependent fields on every switch
      const it = document.querySelector('select[name="income_type"]');
      if (it) it.value = '';
      const vd = document.querySelector('select[name="vat_deductible_pct"]');
      if (vd) vd.value = '';
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField) _unlockVatRate(vatRateField);
    });
  });

  // 5. Initialize on page load based on already-checked direction (covers error re-renders)
  const checkedOnLoad = document.querySelector('input[name="direction"]:checked');
  if (checkedOnLoad) {
    applyDirection(checkedOnLoad.value);
  }

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
      const isExpense = checkedDirection && checkedDirection.value === 'expense';
      const vdField = document.querySelector('select[name="vat_deductible_pct"]');
      if (vdField && isExpense && cat.default_vat_deductible_pct != null) {
        vdField.value = cat.default_vat_deductible_pct;
      }

      const descReq = document.getElementById('desc-required');
      if (descReq) {
        descReq.style.display = (cat.name === 'other_expense' || cat.name === 'other_income') ? '' : 'none';
      }
    });
  }

  // 7. income_type change: lock/unlock vat_rate
  const incomeTypeSelect = document.querySelector('select[name="income_type"]');
  if (incomeTypeSelect) {
    incomeTypeSelect.addEventListener('change', function () {
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (!vatRateField) return;
      if (this.value === 'internal') {
        vatRateField.value = '0';
        _lockVatRate(vatRateField);
      } else {
        _unlockVatRate(vatRateField);
      }
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
