// Sidebar toggle logic
document.getElementById('toggleSidebar').addEventListener('click', function () {
  const sidebar = document.getElementById('sidebar');
  const main = document.getElementById('mainContent');

  sidebar.classList.toggle('collapsed');
  main.classList.toggle('collapsed');

  this.textContent = sidebar.classList.contains('collapsed') ? '⮞' : '⮜';
});

document.querySelectorAll('.nav-link').forEach(link => {
  const label = link.querySelector('.label');
  const sectionName = label ? label.textContent.toLowerCase() : '';

  link.setAttribute('data-section', sectionName);
  link.setAttribute('data-tooltip', label?.textContent || '');

  link.addEventListener('click', function () {
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    this.classList.add('active');

    document.querySelectorAll('[data-view]').forEach(view => view.style.display = 'none');

    const view = document.getElementById(`${sectionName}-view`);
    if (view) {
      view.style.display = 'block';
    }
  });
});

