
const select = document.getElementById('themeSelect');
select?.addEventListener('change', () => {
  document.body.dataset.prismaTheme = select.value;
});
