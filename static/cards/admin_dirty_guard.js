(function() {
  if (!window.addEventListener) return;
  var form = document.querySelector('form');
  if (!form) return;

  var dirty = false;
  var markDirty = function() { dirty = true; };

  form.addEventListener('change', markDirty, true);
  form.addEventListener('input', markDirty, true);

  window.addEventListener('beforeunload', function(e) {
    if (!dirty) return;
    e.preventDefault();
    e.returnValue = '';
    return '';
  });

  form.addEventListener('submit', function() {
    dirty = false;
  });

  // Клиентская проверка обязательных полей, чтобы не терять загруженные файлы из-за банальных ошибок
  form.addEventListener('submit', function(e) {
    var requiredIds = ['id_title', 'id_address', 'id_price', 'id_description'];
    var missing = requiredIds.filter(function(id) {
      var el = document.getElementById(id);
      if (!el) return false;
      return !el.value || el.value.trim() === '';
    });
    if (missing.length) {
      e.preventDefault();
      dirty = true; // считаем несохраненным, чтобы не уйти случайно
      alert('Заполните обязательные поля: название, адрес, цена, описание');
      var first = document.getElementById(missing[0]);
      if (first) first.focus();
    }
  }, true);
})();
