/**
 * Função para atualizar o ano atual no footer
 * Esta função é executada quando o DOM é completamente carregado
 */
document.addEventListener('DOMContentLoaded', function () {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});

/**
 * Funcionalidade para controlar o toggle da sidebar
 * Adiciona ou remove classes para expandir/colapsar a sidebar
 * Implementa acessibilidade com suporte a navegação por teclado
 */
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarToggle && sidebar && content) {
        function toggleSidebar() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);

            // Atualiza o aria-expanded para acessibilidade
            sidebarToggle.setAttribute('aria-expanded', !isCollapsed);
        }

        sidebarToggle.addEventListener('click', toggleSidebar);

        // Adiciona suporte para tecla Enter
        sidebarToggle.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                toggleSidebar();
            }
        });

        // Recupera o estado da sidebar do localStorage ao carregar a página
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
            sidebarToggle.setAttribute('aria-expanded', 'false');
        }
    }
});

/**
 * Função para prevenir envios duplicados de formulários
 * Desabilita o botão de submit após o primeiro clique e fornece feedback visual
 */
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitButtons = form.querySelectorAll('button[type="submit"]');

            submitButtons.forEach(button => {
                if (!button.disabled) {
                    button.disabled = true;
                    const originalText = button.textContent;
                    button.textContent = 'Enviando...';

                    // Restaura o botão após 5 segundos caso o envio falhe
                    setTimeout(() => {
                        button.disabled = false;
                        button.textContent = originalText;
                    }, 5000);
                } else {
                    e.preventDefault(); // Previne múltiplos envios
                }
            });
        });
    });
});

/**
 * Inicialização de tooltips do Bootstrap
 * Ativa tooltips em elementos com o atributo data-bs-toggle="tooltip"
 */
document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Inicialização do List.js para tabelas dinâmicas com cache de dados
 * @param {string} containerId - ID do container da tabela
 * @param {Array} valueNames - Nomes das colunas para ordenação
 */
const tableCache = new Map();

function initializeDataTable(containerId, valueNames) {
    if (document.getElementById(containerId)) {
        if (tableCache.has(containerId)) {
            return tableCache.get(containerId);
        }

        const options = {
            valueNames: valueNames,
            searchColumns: valueNames,
            page: 15,
            pagination: {
                paginationClass: 'pagination',
                outerWindow: 1,
                innerWindow: 2,
            }
        };
        const table = new List(containerId, options);
        tableCache.set(containerId, table);
        return table;
    }
    return null;
}

/**
 * Função genérica para editar um registro com tratamento de erros aprimorado
 * @param {string} route - Rota base para edição
 * @param {number} id - ID do registro
 */
async function editarRegistro(route, id) {
    try {
        const response = await fetch(`/${route}/editar/${id}`);
        if (!response.ok) {
            throw new Error('Falha ao carregar dados para edição');
        }
        const data = await response.json();
        // Implemente aqui a lógica para preencher o formulário de edição com os dados
    } catch (error) {
        console.error('Erro ao editar registro:', error);
        alert('Não foi possível carregar os dados para edição. Por favor, tente novamente.');
    }
}

/**
 * Função genérica para excluir um registro com feedback visual e tratamento de erros
 * @param {string} route - Rota base para exclusão
 * @param {number} id - ID do registro
 * @param {string} mensagem - Mensagem de confirmação
 */
async function excluirRegistro(route, id, mensagem = 'Tem certeza que deseja excluir este registro?') {
    if (confirm(mensagem)) {
        try {
            const response = await fetch(`/${route}/excluir/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao excluir o registro');
            }

            // Feedback visual de sucesso
            alert('Registro excluído com sucesso!');
            window.location.reload();
        } catch (error) {
            console.error('Erro ao excluir registro:', error);
            alert('Erro ao excluir o registro. Por favor, tente novamente.');
        }
    }
}

// Inicialização das tabelas específicas
document.addEventListener('DOMContentLoaded', function () {
    const tables = [
        { id: 'cargos', columns: ['id', 'nome', 'descricao'] },
        { id: 'colaboradores', columns: ['id', 'nome', 'cargo', 'departamento'] },
        { id: 'treinamentos', columns: ['id', 'titulo', 'descricao', 'data'] }
    ];

    tables.forEach(table => {
        if (document.getElementById(table.id)) {
            initializeDataTable(table.id, table.columns);
        }
    });
});

/**
 * Funções para gerenciamento de usuários e perfis
 */

/**
 * Cache para armazenar dados de usuários e perfis
 */
const dataCache = new Map();

/**
 * Edita um usuário existente
 * @param {number} id - ID do usuário a ser editado
 */
async function editarUsuario(id) {
    try {
        // Verifica se os dados do usuário estão em cache
        if (!dataCache.has(`usuario_${id}`)) {
            const response = await fetch(`/auth/usuario/${id}`);
            if (!response.ok) {
                throw new Error('Falha ao carregar dados do usuário');
            }
            const data = await response.json();
            dataCache.set(`usuario_${id}`, data);
        }

        const data = dataCache.get(`usuario_${id}`);

        // Preenche o modal com os dados do usuário
        document.getElementById('edit_nome').value = data.NOME_USUARIO;
        document.getElementById('edit_login').value = data.LOGIN;
        document.getElementById('edit_email').value = data.EMAIL;
        document.getElementById('edit_id_role').value = data.ID_ROLE;
        document.getElementById('edit_usuario_id').value = data.ID_USUARIO;

        // Abre o modal de edição
        new bootstrap.Modal(document.getElementById('editUsuarioModal')).show();

        // Adiciona listeners para acessibilidade
        setupModalAccessibility('editUsuarioModal');
    } catch (error) {
        console.error('Erro ao editar usuário:', error);
        showErrorMessage('Erro ao carregar dados do usuário. Por favor, tente novamente.');
    }
}

/**
 * Ativa ou desativa um usuário
 * @param {number} id - ID do usuário
 * @param {boolean} ativo - Estado atual do usuário
 */
async function toggleUsuario(id, ativo) {
    const novoStatus = !ativo;
    const mensagem = novoStatus ? 'ativar' : 'desativar';

    if (confirm(`Tem certeza que deseja ${mensagem} este usuário?`)) {
        try {
            const response = await fetch(`/auth/usuario/${id}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ativo: novoStatus })
            });

            if (!response.ok) {
                throw new Error('Erro ao atualizar usuário');
            }

            // Atualiza o cache
            if (dataCache.has(`usuario_${id}`)) {
                const userData = dataCache.get(`usuario_${id}`);
                userData.ATIVO = novoStatus;
                dataCache.set(`usuario_${id}`, userData);
            }

            showSuccessMessage(`Usuário ${mensagem}do com sucesso!`);
            setTimeout(() => window.location.reload(), 1500);
        } catch (error) {
            console.error('Erro ao atualizar status do usuário:', error);
            showErrorMessage('Erro ao atualizar status do usuário. Por favor, tente novamente.');
        }
    }
}

/**
 * Edita um perfil existente
 * @param {number} id - ID do perfil a ser editado
 */
async function editarPerfil(id) {
    try {
        // Verifica se os dados do perfil estão em cache
        if (!dataCache.has(`perfil_${id}`)) {
            const response = await fetch(`/auth/perfil/${id}`);
            if (!response.ok) {
                throw new Error('Falha ao carregar dados do perfil');
            }
            const data = await response.json();
            dataCache.set(`perfil_${id}`, data);
        }

        const data = dataCache.get(`perfil_${id}`);

        // Preenche o modal com os dados do perfil
        document.getElementById('edit_nome_role').value = data.NOME_ROLE;
        document.getElementById('edit_descricao_role').value = data.DESCRICAO;
        document.getElementById('edit_role_id').value = data.ID_ROLE;

        // Abre o modal de edição
        new bootstrap.Modal(document.getElementById('editPerfilModal')).show();

        // Adiciona listeners para acessibilidade
        setupModalAccessibility('editPerfilModal');
    } catch (error) {
        console.error('Erro ao editar perfil:', error);
        showErrorMessage('Erro ao carregar dados do perfil. Por favor, tente novamente.');
    }
}

/**
 * Configura a acessibilidade para modais
 * @param {string} modalId - ID do modal
 */
function setupModalAccessibility(modalId) {
    const modal = document.getElementById(modalId);
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    firstElement.focus();

    modal.addEventListener('keydown', function (e) {
        if (e.key === 'Tab') {
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    });
}

/**
 * Exibe uma mensagem de erro
 * @param {string} message - Mensagem de erro
 */
function showErrorMessage(message) {
    // Implementar lógica para exibir mensagem de erro (ex: toast ou alert)
    alert(message);
}

/**
 * Exibe uma mensagem de sucesso
 * @param {string} message - Mensagem de sucesso
 */
function showSuccessMessage(message) {
    // Implementar lógica para exibir mensagem de sucesso (ex: toast ou alert)
    alert(message);
}

// Inicialização dos tooltips do Bootstrap
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
