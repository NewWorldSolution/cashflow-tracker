document.addEventListener('DOMContentLoaded', function () {

  // 1. Fetch /categories on load and build lookup map
  //    Response fields: category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
  let categoryMap = {};
  fetch('/categories')
    .then(r => r.json())
    .then(cats => {
      cats.forEach(c => { categoryMap[c.category_id] = c; });
    });

  // 2. Direction change: show/hide conditional rows
  //    When switching, clear dependent fields and release any vat_rate lock
  document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', function () {
      const isIncome = this.value === 'income';
      document.getElementById('income-type-row').style.display = isIncome ? '' : 'none';
      document.getElementById('vat-deductible-row').style.display = isIncome ? 'none' : '';
      // Clear and unlock on switch
      if (!isIncome) {
        const it = document.querySelector('select[name="income_type"]');
        if (it) it.value = '';
      } else {
        const vd = document.querySelector('select[name="vat_deductible_pct"]');
        if (vd) vd.value = '';
      }
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField) vatRateField.disabled = false;
    });
  });

  // 3. Category change: set defaults and update desc-required indicator
  const categorySelect = document.querySelector('select[name="category_id"]');
  if (categorySelect) {
    categorySelect.addEventListener('change', function () {
      const cat = categoryMap[this.value];
      if (!cat) return;

      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField && !vatRateField.disabled) {
        vatRateField.value = cat.default_vat_rate;
      }

      const vdField = document.querySelector('select[name="vat_deductible_pct"]');
      if (vdField && cat.default_vat_deductible_pct != null) {
        vdField.value = cat.default_vat_deductible_pct;
      }

      const descReq = document.getElementById('desc-required');
      if (descReq) {
        descReq.style.display = (cat.name === 'other_expense' || cat.name === 'other_income') ? '' : 'none';
      }
    });
  }

  // 4. income_type change: lock/unlock vat_rate
  const incomeTypeSelect = document.querySelector('select[name="income_type"]');
  if (incomeTypeSelect) {
    incomeTypeSelect.addEventListener('change', function () {
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (!vatRateField) return;
      if (this.value === 'internal') {
        vatRateField.value = '0';
        vatRateField.disabled = true;
      } else {
        vatRateField.disabled = false;
      }
    });
  }

  // 5. payment_method change: card reminder
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
