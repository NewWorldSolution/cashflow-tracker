document.addEventListener('DOMContentLoaded', function () {
  const categoryHierarchy = window.CATEGORY_HIERARCHY || { cash_in: [], cash_out: [] };
  const categoryGroupSelect = document.getElementById('category_group');
  const categorySelect = document.getElementById('category_id');
  const cashInTypeRow = document.getElementById('cash-in-type-row');
  const vatRow = document.getElementById('vat-deductible-row');
  const cardReminder = document.getElementById('card-reminder');
  const descRequired = document.getElementById('desc-required');
  const cashInTypeSelect = document.querySelector('select[name="cash_in_type"]');
  const paymentSelect = document.querySelector('select[name="payment_method"]');
  const vatRateField = document.querySelector('select[name="vat_rate"]');
  const vatDeductibleField = document.querySelector('select[name="vat_deductible_pct"]');
  const accountantField = document.querySelector('input[name="for_accountant"]');
  const accountantGroup = accountantField ? accountantField.closest('.form-group') : null;

  function _lockField(field) {
    if (!field) return;
    field.dataset.locked = 'true';
    field.style.opacity = '0.5';
    field.style.pointerEvents = 'none';
  }

  function _unlockField(field) {
    if (!field) return;
    delete field.dataset.locked;
    field.style.opacity = '';
    field.style.pointerEvents = '';
  }

  function currentDirection() {
    const checked = document.querySelector('input[name="direction"]:checked');
    return checked ? checked.value : 'cash_out';
  }

  function getGroups(direction) {
    return categoryHierarchy[direction] || [];
  }

  function findParentIdForCategory(direction, categoryId) {
    const groups = getGroups(direction);
    for (const group of groups) {
      const match = group.children.find(child => String(child.id) === String(categoryId));
      if (match) {
        return String(group.id);
      }
    }
    return '';
  }

  function findCategory(direction, categoryId) {
    const groups = getGroups(direction);
    for (const group of groups) {
      const match = group.children.find(child => String(child.id) === String(categoryId));
      if (match) {
        return match;
      }
    }
    return null;
  }

  function setPlaceholderOption(select, text) {
    select.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = text;
    select.appendChild(placeholder);
  }

  function populateGroupOptions(direction, selectedGroupId) {
    if (!categoryGroupSelect) return;
    setPlaceholderOption(categoryGroupSelect, categoryGroupSelect.dataset.placeholder || 'Select category group');
    for (const group of getGroups(direction)) {
      const opt = document.createElement('option');
      opt.value = group.id;
      opt.textContent = group.label;
      if (String(selectedGroupId) === String(group.id)) {
        opt.selected = true;
      }
      categoryGroupSelect.appendChild(opt);
    }
  }

  function populateSubcategoryOptions(direction, parentId, selectedCategoryId) {
    if (!categorySelect) return;
    setPlaceholderOption(categorySelect, categorySelect.dataset.placeholder || 'Select subcategory');
    const parent = getGroups(direction).find(group => String(group.id) === String(parentId));
    if (!parent) {
      categorySelect.value = '';
      return;
    }
    for (const child of parent.children) {
      const opt = document.createElement('option');
      opt.value = child.id;
      opt.textContent = child.label;
      if (String(selectedCategoryId) === String(child.id)) {
        opt.selected = true;
      }
      categorySelect.appendChild(opt);
    }
  }

  function updateDescriptionRequirement(category) {
    if (!descRequired) return;
    descRequired.style.display = (category && (category.slug === 'ci_other_income' || category.slug === 'co_other_expense')) ? '' : 'none';
  }

  function applyCategoryDefaults(category) {
    if (!category) {
      updateDescriptionRequirement(null);
      return;
    }
    if (vatRateField && !vatRateField.dataset.locked && category.vat_rate != null) {
      vatRateField.value = String(category.vat_rate).replace('.0', '');
    }
    if (vatDeductibleField && currentDirection() === 'cash_out' && category.vat_deductible_pct != null) {
      vatDeductibleField.value = String(category.vat_deductible_pct).replace('.0', '');
    }
    updateDescriptionRequirement(category);
  }

  function syncPicker(direction, selectedGroupId, selectedCategoryId) {
    populateGroupOptions(direction, selectedGroupId);
    populateSubcategoryOptions(direction, selectedGroupId, selectedCategoryId);
    applyCategoryDefaults(findCategory(direction, selectedCategoryId));
  }

  function resetCategoryPicker(direction) {
    populateGroupOptions(direction, '');
    populateSubcategoryOptions(direction, '', '');
    updateDescriptionRequirement(null);
  }

  function applyDirection(direction) {
    const isCashIn = direction === 'cash_in';
    if (cashInTypeRow) cashInTypeRow.style.display = isCashIn ? '' : 'none';
    if (vatRow) vatRow.style.display = isCashIn ? 'none' : '';
    resetCategoryPicker(direction);
  }

  function applyInternalLock(isInternal) {
    if (isInternal) {
      if (vatRateField) {
        vatRateField.value = '0';
        _lockField(vatRateField);
      }
      if (paymentSelect) {
        paymentSelect.value = 'cash';
        _lockField(paymentSelect);
      }
      if (accountantField) {
        accountantField.checked = false;
        accountantField.disabled = true;
      }
      if (accountantGroup) {
        accountantGroup.style.display = 'none';
      }
    } else {
      _unlockField(vatRateField);
      _unlockField(paymentSelect);
      if (accountantField) {
        accountantField.disabled = false;
      }
      if (accountantGroup) {
        accountantGroup.style.display = '';
      }
    }
  }

  function updateCardReminder() {
    if (!cardReminder || !paymentSelect) return;
    cardReminder.style.display = paymentSelect.value === 'card' ? '' : 'none';
  }

  document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', function () {
      applyDirection(this.value);
      if (cashInTypeSelect) {
        cashInTypeSelect.value = '';
      }
      if (vatDeductibleField) {
        vatDeductibleField.value = '';
      }
      applyInternalLock(false);
      document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
      this.closest('.toggle-btn').classList.add('active');
    });
  });

  if (categoryGroupSelect) {
    categoryGroupSelect.addEventListener('change', function () {
      populateSubcategoryOptions(currentDirection(), this.value, '');
      updateDescriptionRequirement(null);
    });
  }

  if (categorySelect) {
    categorySelect.addEventListener('change', function () {
      applyCategoryDefaults(findCategory(currentDirection(), this.value));
    });
  }

  if (cashInTypeSelect) {
    cashInTypeSelect.addEventListener('change', function () {
      applyInternalLock(this.value === 'internal');
    });
  }

  if (paymentSelect) {
    paymentSelect.addEventListener('change', updateCardReminder);
  }

  if (categoryGroupSelect) {
    categoryGroupSelect.dataset.placeholder = categoryGroupSelect.options[0] ? categoryGroupSelect.options[0].textContent : 'Select category group';
  }
  if (categorySelect) {
    categorySelect.dataset.placeholder = categorySelect.options[0] ? categorySelect.options[0].textContent : 'Select subcategory';
  }

  const direction = currentDirection();
  const selectedCategoryId = categorySelect ? (categorySelect.dataset.selectedValue || categorySelect.value) : '';
  const selectedGroupId = categoryGroupSelect
    ? (categoryGroupSelect.dataset.selectedValue || findParentIdForCategory(direction, selectedCategoryId))
    : '';

  applyDirection(direction);
  syncPicker(direction, selectedGroupId, selectedCategoryId);

  if (cashInTypeSelect && cashInTypeSelect.value === 'internal') {
    applyInternalLock(true);
  }
  updateCardReminder();
});
