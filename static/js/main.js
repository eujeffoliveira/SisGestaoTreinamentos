// static/js/main.js

/**
 * Função para atualizar o ano atual no footer
 * Esta função é executada quando o DOM é completamente carregado
 */
document.addEventListener('DOMContentLoaded', function () {
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
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarToggle && sidebar && content) {
        sidebarToggle.addEventListener('click', function () {
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
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function () {
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
document.addEventListener('DOMContentLoaded', function () {
    // Inicializa todos os tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Inicialização do List.js para tabelas dinâmicas
 * @param {string} containerId - ID do container da tabela
 * @param {Array} valueNames - Nomes das colunas para ordenação
 */
function initializeDataTable(containerId, valueNames) {
    if (document.getElementById(containerId)) {
        var options = {
            valueNames: valueNames,
            searchColumns: valueNames,
            page: 10,
            pagination: {
                paginationClass: 'pagination',
                outerWindow: 1, // Número de páginas exibidas antes e depois da página atual
                innerWindow: 2, // Número de páginas exibidas antes e depois dos pontos suspensivos
            }
        };
        return new List(containerId, options);
    }
    return null;
}

/**
 * Função genérica para editar um registro
 * @param {string} route - Rota base para edição
 * @param {number} id - ID do registro
 */
function editarRegistro(route, id) {
    window.location.href = `/${route}/editar/${id}`;
}

/**
 * Função genérica para excluir um registro
 * @param {string} route - Rota base para exclusão
 * @param {number} id - ID do registro
 * @param {string} mensagem - Mensagem de confirmação
 */
function excluirRegistro(route, id, mensagem = 'Tem certeza que deseja excluir este registro?') {
    if (confirm(mensagem)) {
        fetch(`/${route}/excluir/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Erro ao excluir o registro');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao excluir o registro');
            });
    }
}

// Inicialização das tabelas específicas
document.addEventListener('DOMContentLoaded', function () {
    // Tabela de Cargos
    if (document.getElementById('cargos')) {
        initializeDataTable('cargos', ['id', 'nome', 'descricao']);
    }

    // Tabela de Colaboradores
    if (document.getElementById('colaboradores')) {
        initializeDataTable('colaboradores', ['id', 'nome', 'cargo', 'departamento']);
    }

    // Tabela de Treinamentos
    if (document.getElementById('treinamentos')) {
        initializeDataTable('treinamentos', ['id', 'titulo', 'descricao', 'data']);
    }
});
