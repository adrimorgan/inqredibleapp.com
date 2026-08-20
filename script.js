(() => {
    const documentLanguage = document.documentElement.lang.toLowerCase();
    const searchParams = new URLSearchParams(window.location.search);
    if (!documentLanguage.startsWith('en') || searchParams.get('lang') === 'en') return;

    const preferredLanguages = navigator.languages && navigator.languages.length
        ? navigator.languages
        : [navigator.language];
    const prefersSpanish = preferredLanguages.some((language) => (language || '').toLowerCase().startsWith('es'));
    if (!prefersSpanish) return;

    const routes = {
        '/': '/es/',
        '/index.html': '/es/',
        '/privacy.html': '/es/privacy.html',
        '/terms.html': '/es/terms.html',
        '/support.html': '/es/soporte.html',
        '/qr-code-with-logo.html': '/es/codigo-qr-con-logo.html',
        '/wifi-qr-code.html': '/es/codigo-qr-wifi.html',
        '/barcode-generator-iphone.html': '/es/generador-codigo-barras-iphone.html'
    };
    const targetPath = routes[window.location.pathname];
    if (targetPath) {
        window.location.replace(`${targetPath}${window.location.search}${window.location.hash}`);
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('[data-header]');
    const menuButton = document.querySelector('[data-menu-button]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    const navLinks = document.querySelectorAll('.nav-links a, .mobile-panel a');
    const sections = document.querySelectorAll('section[id]');

    const setHeaderState = () => {
        if (!header) return;
        header.classList.toggle('is-scrolled', window.scrollY > 12);
    };

    const closeMobileMenu = () => {
        if (!menuButton || !mobileMenu) return;
        menuButton.classList.remove('is-open');
        mobileMenu.classList.remove('is-open');
        menuButton.setAttribute('aria-expanded', 'false');
    };

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            const isOpen = menuButton.classList.toggle('is-open');
            mobileMenu.classList.toggle('is-open', isOpen);
            menuButton.setAttribute('aria-expanded', String(isOpen));
        });
    }

    navLinks.forEach((link) => {
        link.addEventListener('click', () => closeMobileMenu());
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMobileMenu();
        }
    });

    setHeaderState();
    window.addEventListener('scroll', setHeaderState, { passive: true });

    const revealElements = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.14 });

        revealElements.forEach((element) => revealObserver.observe(element));
    } else {
        revealElements.forEach((element) => element.classList.add('is-visible'));
    }

    const desktopLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    if ('IntersectionObserver' in window && sections.length) {
        const sectionObserver = new IntersectionObserver((entries) => {
            const visible = entries
                .filter((entry) => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

            if (!visible) return;
            const id = visible.target.getAttribute('id');
            desktopLinks.forEach((link) => {
                link.classList.toggle('is-active', link.getAttribute('href') === `#${id}`);
            });
        }, {
            rootMargin: '-35% 0px -55% 0px',
            threshold: [0.08, 0.2, 0.4]
        });

        sections.forEach((section) => sectionObserver.observe(section));
    }
});
