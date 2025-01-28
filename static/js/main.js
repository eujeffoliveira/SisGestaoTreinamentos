// static/js/main.js

/**
 * Função para atualizar o ano atual no footer
 * Esta função é executada quando o DOM é completamente carregado
 */
document.addEventListener('DOMContentLoaded', function() {
    // Atualiza o ano no footer
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});

/**
 * Funcionalidade para controlar o toggle da sidebar
 * Adiciona ou remove classes para expandir/colapsar a sidebar
 */
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarToggle && sidebar && content) {
        sidebarToggle.addEventListener('click', function() {
            // Toggle das classes para colapsar/expandir a sidebar
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            
            // Armazena o estado da sidebar no localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });

        // Recupera o estado da sidebar do localStorage ao carregar a página
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        }
    }
});

/**
 * Função para prevenir envios duplicados de formulários
 * Desabilita o botão de submit após o primeiro clique
 */
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Encontra todos os botões de submit no formulário
            const submitButtons = form.querySelectorAll('button[type="submit"]');
            
            // Desabilita cada botão após o envio
            submitButtons.forEach(button => {
                button.disabled = true;
            });
        });
    });
});

/**
 * Inicialização de tooltips do Bootstrap
 * Ativa tooltips em elementos com o atributo data-bs-toggle="tooltip"
 */
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa todos os tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
