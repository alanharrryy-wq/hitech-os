
export function initScroll(root = document) {
  root.querySelectorAll('a[href^="#"]').forEach(link => {
    if (link.dataset.prismaScrollReady) return;
    link.dataset.prismaScrollReady = 'true';
  });
}
