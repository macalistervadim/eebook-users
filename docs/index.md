# Веб-приложение «Инвестиционный Помогатор» (eebook)

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<div class="landing-hero">
  <h1>💹 Инвестиционный Помогатор</h1>
  <p>Ваш персональный инструмент для учёта портфелей, анализа доходности и планирования выплат.</p>
  <a class="hero-button" href="installation/guide.md">Начать пользоваться</a>
  <div class="hero-bubbles">
    <span></span><span></span><span></span><span></span><span></span>
  </div>
</div>

<div class="landing-cards">
  <div class="card reveal"><i class="fa-solid fa-user"></i><h3>Портфели и активы</h3><p>Создавайте и ведите портфели с акциями, облигациями, валютой и криптовалютой.</p></div>
  <div class="card reveal"><i class="fa-solid fa-chart-line"></i><h3>Аналитика и метрики</h3><p>Следите за доходностью, волатильностью и сравнивайте с индексами.</p></div>
  <div class="card reveal"><i class="fa-solid fa-calendar-days"></i><h3>Календарь выплат</h3><p>Дивиденды, купоны, погашения — всё в одном месте.</p></div>
  <div class="card reveal"><i class="fa-solid fa-lock"></i><h3>Безопасность</h3><p>Шифрование данных, защита от XSS, CSRF и SQL-инъекций.</p></div>
  <div class="card reveal"><i class="fa-solid fa-cogs"></i><h3>Администрирование</h3><p>Управление пользователями и тикетами, модерация контента.</p></div>
  <div class="card reveal"><i class="fa-solid fa-server"></i><h3>Инфраструктура</h3><p>Docker, CI/CD, тестирование, мониторинг и масштабирование.</p></div>
</div>

<div class="landing-timeline">
  <div class="timeline-item reveal"><h3>Pet-проект (1–2 месяца)</h3><p>MVP для одного пользователя, базовая аналитика, CRUD по активам и сделкам.</p></div>
  <div class="timeline-item reveal"><h3>Продукт для портфолио (2–3 месяца)</h3><p>Многопользовательский режим, регистрация, аутентификация, UX-интерфейс.</p></div>
  <div class="timeline-item reveal"><h3>SaaS-пилот (3–6 месяцев)</h3><p>Монетизация, импорт/экспорт сделок, календарь выплат, CI/CD, мониторинг.</p></div>
  <div class="timeline-item reveal"><h3>Масштабирование (6–12 месяцев)</h3><p>Интеграции с API брокеров, социальные функции, мобильная версия (PWA/React Native).</p></div>
</div>
<hr>
<div class="landing-stack">
  <div class="stack-item reveal"><i class="fa-brands fa-python"></i> Python / FastAPI</div>
  <div class="stack-item reveal"><i class="fa-brands fa-react"></i> React / Tailwind</div>
  <div class="stack-item reveal"><i class="fa-solid fa-database"></i> PostgreSQL / Alembic</div>
  <div class="stack-item reveal"><i class="fa-solid fa-docker"></i> Docker / CI/CD</div>
  <div class="stack-item reveal"><i class="fa-solid fa-cloud"></i> Render / AWS / Fly.io</div>
</div>


<div class="landing-footer">
  <p>Разработчик: <strong>Старцев Вадим Сергеевич</strong> — <a href="https://github.com/macalistervadim">GitHub</a></p>
</div>

<script>
  // Scroll reveal для всех элементов с классом .reveal
  document.addEventListener("DOMContentLoaded", () => {
    const revealElements = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add("active");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    revealElements.forEach(el => observer.observe(el));
  });
</script>
