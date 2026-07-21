
export function initForms(root = document) {
  root.querySelectorAll('form[data-prisma-form]').forEach(form => {
    if (form.dataset.prismaFormReady) return;
    form.dataset.prismaFormReady = 'true';
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
      }
    });
  });
}
