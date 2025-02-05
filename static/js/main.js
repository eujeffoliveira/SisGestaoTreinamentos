/***************************************************************
 *                     UTILIDADES GLOBAIS
 ***************************************************************/

/**
 * Cache para armazenar dados temporários, como os retornos de perfis
 */
const dataCache = new Map();

/**
 * Mensagens padrão para feedback visual e erros
 */
const MENSAGENS = {
    ERRO_CARREGAR: 'Não foi possível carregar os dados. Tente novamente.',
    ERRO_ATUALIZAR: 'Erro ao atualizar. Tente novamente.',
    SUCESSO_ATUALIZAR: 'Atualizado com sucesso!',
    CONFIRMA_TOGGLE: 'Tem certeza que deseja {acao} este usuário?'
};

/**
 * Exibe uma mensagem de erro ao usuário (atualmente com alert, mas pode ser substituído por um sistema de notificações)
 * @param {string} message - Mensagem de erro
 */
function showErrorMessage(message) {
    console.error('Erro:', message);
    alert(message); // Futuramente, substitua por um sistema de notificações
}

/**
 * Exibe uma mensagem de sucesso ao usuário (atualmente com alert, mas pode ser substituído por um sistema de notificações)
 * @param {string} message - Mensagem de sucesso
 */
function showSuccessMessage(message) {
    alert(message); // Futuramente, substitua por um sistema de notificações
}

/**
 * Abre um modal do Bootstrap, dado o ID do elemento modal
 * @param {string} modalId - ID do elemento modal
 */
function abrirModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
        throw new Error(`Modal não encontrado: ${modalId}`);
    }
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

/** 
 * Função para exportar dados de uma tabela para um arquivo CSV, Excel ou PDF.
 */
function exportar(formato) {
    window.location.href = "/logs/exportar/" + formato;
}


/***************************************************************
 *                           FOOTER
 ***************************************************************/

/**
 * Atualiza o ano atual no footer.
 * Executado quando o DOM estiver completamente carregado.
 */
document.addEventListener('DOMContentLoaded', function () {
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});

/***************************************************************
 *                          SIDEBAR
 ***************************************************************/

/**
 * Controla o comportamento do toggle da sidebar, incluindo suporte para navegação por teclado e
 * armazenamento do estado (colapsada ou expandida) no localStorage para manter a preferência do usuário.
 */
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarToggle && sidebar && content) {
        /**
         * Alterna o estado da sidebar entre colapsada e expandida.
         */
        function toggleSidebar() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            const isCollapsed = sidebar.classList.contains('collapsed');

            // Armazena o estado atual da sidebar
            localStorage.setItem('sidebarCollapsed', isCollapsed);

            // Atualiza o atributo aria-expanded para melhorar a acessibilidade
            sidebarToggle.setAttribute('aria-expanded', !isCollapsed);
        }

        // Evento de clique para alternar a sidebar
        sidebarToggle.addEventListener('click', toggleSidebar);

        // Suporte para a tecla Enter (acessibilidade)
        sidebarToggle.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                toggleSidebar();
            }
        });

        // Recupera o estado salvo da sidebar e o aplica ao carregar a página
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
            sidebarToggle.setAttribute('aria-expanded', 'false');
        }
    }
});

/***************************************************************
 *             PREVENÇÃO DE ENVIO DUPLICADO DE FORMULÁRIOS
 ***************************************************************/

/**
 * Impede que formulários sejam submetidos múltiplas vezes.
 * Ao enviar, desabilita o botão de submit e exibe um feedback textual.
 * Caso o envio demore (possível falha), o botão é reabilitado após 5 segundos.
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

                    // Restaura o botão após 5 segundos, caso o envio falhe
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

/***************************************************************
 *                INICIALIZAÇÃO DOS TOOLTIP DO BOOTSTRAP
 ***************************************************************/

/**
 * Inicializa os tooltips do Bootstrap para todos os elementos que possuírem o atributo data-bs-toggle="tooltip".
 */
document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/***************************************************************
 *                     TABELAS DINÂMICAS (List.js)
 ***************************************************************/

/**
 * Cache para armazenar instâncias das tabelas inicializadas
 */
const tableCache = new Map();

/**
 * Inicializa uma tabela dinâmica utilizando o List.js.
 * Se a tabela já foi inicializada (cache), retorna a instância armazenada.
 * @param {string} containerId - ID do container da tabela
 * @param {Array} valueNames - Array com os nomes das colunas (para ordenação e pesquisa)
 * @returns {List|null} - Instância da tabela ou null se o container não existir
 */
function initializeDataTable(containerId, valueNames) {
    const container = document.getElementById(containerId);
    if (!container) return null;

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

/**
 * Inicializa as tabelas dinâmicas disponíveis na aplicação.
 * Cada objeto no array "tables" representa a configuração de uma tabela.
 */
document.addEventListener('DOMContentLoaded', function () {
    const tables = [
        {
            id: 'cargos',
            columns: ['id', 'nome', 'descricao'],
            options: { page: 10 }
        },
        {
            id: 'colaboradores',
            columns: ['id', 'nome', 'cargo', 'departamento'],
            options: { page: 15 }
        },
        {
            id: 'treinamentos',
            columns: ['id', 'titulo', 'descricao', 'data'],
            options: { page: 10 }
        }
    ];

    tables.forEach(table => {
        const container = document.getElementById(table.id);
        if (container) {
            const tableInstance = initializeDataTable(
                table.id,
                table.columns,
                table.options
            );
        }
    });
});

/***************************************************************
 *           FUNÇÕES DE MANIPULAÇÃO DE REGISTROS (CRUD)
 ***************************************************************/

/**
 * Função genérica para editar um registro com tratamento de erros aprimorado.
 * Realiza uma requisição para obter os dados do registro e, de acordo com a rota,
 * chama a função responsável por preencher o formulário correspondente.
 * @param {string} route - Rota base para edição (ex: 'usuarios', 'cargos', 'colaboradores', 'treinamentos')
 * @param {number} id - ID do registro a ser editado
 */
async function editarRegistro(route, id) {
    try {
        // Realiza a requisição para buscar os dados do registro
        const response = await fetch(`/${route}/editar/${id}`);

        if (!response.ok) {
            console.error('Status:', response.status);
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();

        // Chama a função específica de preenchimento de formulário com base na rota
        switch (route) {
            case 'cargos':
                preencherFormularioCargo(data);
                break;
            case 'colaboradores':
                preencherFormularioColaborador(data);
                break;
            case 'treinamentos':
                preencherFormularioTreinamento(data);
                break;
            default:
                throw new Error('Tipo de registro não suportado');
        }

    } catch (error) {
        console.error('Erro ao editar registro:', error);
        showErrorMessage('Não foi possível carregar os dados para edição. Por favor, tente novamente.');
    }
}

/**
 * Exclui um registro específico após confirmação do usuário.
 * @param {string} route - Rota base para exclusão
 * @param {number} id - ID do registro a ser excluído
 * @param {string} mensagem - Mensagem de confirmação personalizada (padrão se não informado)
 */
async function excluirRegistro(route, id, mensagem = 'Tem certeza que deseja excluir este registro?') {
    if (!confirm(mensagem)) return; // Se o usuário cancelar, não prossegue

    try {
        const response = await fetch(`/${route}/excluir/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Falha ao excluir o registro');
        }

        showSuccessMessage('Registro excluído com sucesso!');
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        console.error('Erro ao excluir registro:', error);
        showErrorMessage(`Erro ao excluir o registro: ${error.message}`);
    }
}

/***************************************************************
 *           FUNÇÕES DE MANIPULAÇÃO DE USUÁRIOS
 ***************************************************************/

/**
 * Inicia o processo de edição de um usuário.
 * Busca os dados do usuário via fetch, preenche o formulário e abre o modal de edição.
 * @param {number} id - ID do usuário a ser editado
 */
function editarUsuario(id) {

    fetch(`/auth/usuario/${id}`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            preencherFormularioUsuario(data);
            abrirModal('editUsuarioModal');
        })
        .catch(error => {
            console.error('Erro:', error);
            showErrorMessage(MENSAGENS.ERRO_CARREGAR);
        });
}

/**
 * Preenche o formulário de edição de usuário com os dados obtidos.
 * @param {Object} data - Objeto com os dados do usuário
 */
function preencherFormularioUsuario(data) {
    const campos = {
        'edit_nome': data.NOME_USUARIO,
        'edit_login': data.LOGIN,
        'edit_email': data.EMAIL,
        'edit_id_role': data.ID_ROLE,
        'edit_usuario_id': data.ID_USUARIO
    };

    Object.entries(campos).forEach(([id, valor]) => {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = valor;
        } else {
            console.warn(`Campo não encontrado: ${id}`);
        }
    });
}

/**
 * Alterna o status (ativo/inativo) de um usuário.
 * Solicita confirmação do usuário e envia a alteração via fetch.
 * @param {number} id - ID do usuário
 * @param {boolean} ativo - Status atual do usuário
 */
function toggleUsuario(id, ativo) {
    const novoStatus = !ativo;
    const mensagem = novoStatus ? 'ativar' : 'desativar';

    if (confirm(MENSAGENS.CONFIRMA_TOGGLE.replace('{acao}', mensagem))) {
        fetch(`/auth/usuario/${id}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ativo: novoStatus })
        })
            .then(response => {
                if (!response.ok) throw new Error('Erro na requisição');
                showSuccessMessage(`Usuário ${mensagem}do com sucesso!`);
                setTimeout(() => window.location.reload(), 1500);
            })
            .catch(error => {
                console.error('Erro:', error);
                showErrorMessage(MENSAGENS.ERRO_ATUALIZAR);
            });
    }
}

/**
 * Atualiza os dados de um usuário após a edição.
 * Envia os dados atualizados para o servidor via método PUT.
 * @param {number} userId - ID do usuário
 * @param {Object} dados - Dados atualizados do usuário
 */
function atualizarUsuario(userId, dados) {
    fetch(`/auth/usuario/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
        .then(response => {
            if (!response.ok) throw new Error('Falha ao atualizar usuário');
            showSuccessMessage(MENSAGENS.SUCESSO_ATUALIZAR);
            window.location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
            showErrorMessage(MENSAGENS.ERRO_ATUALIZAR);
        });
}

/**
 * Função para excluir um usuário.
 * Exibe uma confirmação para o usuário e, se confirmado, envia uma requisição para a API.
 * Após a exclusão bem-sucedida, recarrega a página para atualizar a lista.
 *
 * @param {number} id - ID do usuário a ser excluído.
 */
async function excluirUsuario(id) {
    // Mensagem de confirmação para o usuário
    if (!confirm("Tem certeza que deseja excluir este usuário?")) {
        return;
    }

    try {
        // Envia a requisição para excluir o usuário.
        // Ajuste a URL conforme sua rota de exclusão.
        const response = await fetch(`/auth/usuario/${id}/excluir`, {
            method: 'POST', // ou 'DELETE', conforme sua implementação no backend
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Verifica se a resposta foi bem-sucedida
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Erro ao excluir usuário");
        }

        // Exibe uma mensagem de sucesso e recarrega a página
        alert("Usuário excluído com sucesso!");
        window.location.reload();
    } catch (error) {
        // Em caso de erro, exibe uma mensagem para o usuário
        alert("Erro: " + error.message);
    }
}


/***************************************************************
 *           FUNÇÕES DE MANIPULAÇÃO DE PERFIS
 ***************************************************************/

/**
 * Inicia o processo de edição de um perfil.
 * Busca os dados do perfil, armazena no cache e preenche o formulário de edição.
 * @param {number} id - ID do perfil
 */
function editarPerfil(id) {
    fetch(`/auth/perfil/${id}`)
        .then(response => {
            if (!response.ok) throw new Error('Falha ao carregar dados do perfil');
            return response.json();
        })
        .then(data => {
            dataCache.set(`perfil_${id}`, data);
            preencherFormularioPerfil(data);
            abrirModal('editPerfilModal');
        })
        .catch(error => {
            console.error('Erro:', error);
            showErrorMessage(MENSAGENS.ERRO_CARREGAR);
        });
}

/**
 * Preenche o formulário de edição de perfil com os dados obtidos.
 * @param {Object} data - Dados do perfil
 */
function preencherFormularioPerfil(data) {
    const editNomeRole = document.getElementById('edit_nome_role');
    const editDescricaoRole = document.getElementById('edit_descricao_role');
    const editRoleId = document.getElementById('edit_role_id');

    if (editNomeRole) editNomeRole.value = data.NOME_ROLE;
    if (editDescricaoRole) editDescricaoRole.value = data.DESCRICAO;
    if (editRoleId) editRoleId.value = data.ID_ROLE;
}

/**
 * Trata o envio do formulário para criação de um novo perfil.
 * Envia os dados via método POST e atualiza a página após sucesso.
 * @param {Event} e - Evento de submit do formulário
 */
function handleNovoPerfilSubmit(e) {
    e.preventDefault();
    const dados = {
        nome: document.getElementById('nome_role').value,
        descricao: document.getElementById('descricao_role').value
    };

    fetch('/auth/perfil', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
        .then(response => response.json())
        .then(data => {
            showSuccessMessage('Perfil criado com sucesso!');
            window.location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
            showErrorMessage('Erro ao criar perfil');
        });
}

/**
 * Atualiza os dados de um perfil.
 * Envia os dados atualizados para o servidor via método PUT.
 * @param {number} perfilId - ID do perfil
 * @param {Object} dados - Dados atualizados do perfil
 */
function atualizarPerfil(perfilId, dados) {
    fetch(`/auth/perfil/${perfilId}`, {
        method: 'PUT', // Certifique-se de que o backend esteja preparado para receber PUT
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
        .then(response => {
            if (!response.ok) throw new Error('Falha ao atualizar perfil');
            return response.json();
        })
        .then(data => {
            showSuccessMessage('Perfil atualizado com sucesso!');
            window.location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
            showErrorMessage('Erro ao atualizar perfil');
        });
}

/**
 * Função para excluir um perfil.
 * Solicita confirmação do usuário e envia uma requisição para a API para exclusão do perfil.
 * Se houver algum erro (por exemplo, se existirem usuários associados), a API retornará uma mensagem de erro,
 * que será exibida ao usuário. Após exclusão bem-sucedida, a página é recarregada para atualizar a lista.
 *
 * @param {number} id - ID do perfil a ser excluído.
 */
function excluirPerfil(id) {
    // Solicita a confirmação do usuário antes de prosseguir
    if (!confirm("Tem certeza que deseja excluir este perfil?")) {
        return;
    }

    // Envia a requisição para a rota de exclusão do perfil
    fetch(`/auth/perfil/${id}/excluir`, {
        method: 'POST', // Pode ser alterado para 'DELETE' se o backend estiver configurado para isso
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            // Se a resposta não for ok, tenta extrair a mensagem de erro do JSON retornado
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || "Erro ao excluir perfil");
                });
            }
            return response.json();
        })
        .then(data => {
            // Exibe mensagem de sucesso e recarrega a página
            showSuccessMessage(data.message || "Perfil excluído com sucesso!");
            window.location.reload();
        })
        .catch(error => {
            console.error("Erro:", error);
            showErrorMessage(error.message);
        });
}


/***************************************************************
 *              INICIALIZAÇÃO DE EVENT LISTENERS
 ***************************************************************/
document.addEventListener('DOMContentLoaded', function () {
    // Event Listener para o formulário de edição de usuário
    const editUsuarioForm = document.getElementById('editUsuarioForm');
    if (editUsuarioForm) {
        editUsuarioForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const userId = document.getElementById('edit_usuario_id').value;

            const dados = {
                nome: document.getElementById('edit_nome').value,
                email: document.getElementById('edit_email').value,
                id_role: document.getElementById('edit_id_role').value,
                senha: document.getElementById('edit_senha').value
            };

            atualizarUsuario(userId, dados);
        });
    }

    // Event Listener para o formulário de criação de um novo perfil
    const novoPerfilForm = document.getElementById('novoPerfilForm');
    if (novoPerfilForm) {
        novoPerfilForm.addEventListener('submit', handleNovoPerfilSubmit);
    }

    /**
 * Trata o envio do formulário para criação de um novo perfil.
 * Envia os dados via método POST e atualiza a página após sucesso.
 * @param {Event} e - Evento de submit do formulário
 */
    function handleNovoPerfilSubmit(e) {
        e.preventDefault();
        // Altere as chaves para corresponder ao que o backend espera
        const dados = {
            nome_role: document.getElementById('nome_role').value,
            descricao_role: document.getElementById('descricao_role').value
        };

        fetch('/auth/perfil', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
            .then(response => {
                // Opcional: Verificar se a resposta está ok antes de converter para JSON
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || "Erro ao criar perfil");
                    });
                }
                return response.json();
            })
            .then(data => {
                showSuccessMessage('Perfil criado com sucesso!');
                window.location.reload();
            })
            .catch(error => {
                console.error('Erro:', error);
                showErrorMessage('Erro ao criar perfil');
            });
    }

    // Event Listener para o formulário de edição de perfil
    const editPerfilForm = document.getElementById('editPerfilForm');
    if (editPerfilForm) {
        editPerfilForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const perfilId = document.getElementById('edit_role_id').value;

            const dados = {
                nome_role: document.getElementById('edit_nome_role').value,
                descricao: document.getElementById('edit_descricao_role').value
            };

            atualizarPerfil(perfilId, dados);
        });
    }
});

/***************************************************************
 *                     DETALHES DE LOGS
 ***************************************************************/

function mostrarDetalhes(id) {
    fetch(`/logs/detalhes/${id}`)
        .then(response => response.json())
        .then(data => {
            let detalhes = `
                <p><strong>ID:</strong> ${data.ID_LOG}</p>
                <p><strong>Usuário:</strong> ${data.USUARIO}</p>
                <p><strong>Ação:</strong> ${data.ACAO}</p>
                <p><strong>Tabela:</strong> ${data.TABELA}</p>
                <p><strong>ID do Registro:</strong> ${data.ID_REGISTRO}</p>
                <p><strong>Data/Hora:</strong> ${data.DATA_HORA}</p>
                <p><strong>Dados Anteriores:</strong> <pre>${data.DADOS_ANTERIORES || 'N/A'}</pre></p>
                <p><strong>Dados Novos:</strong> <pre>${data.DADOS_NOVOS || 'N/A'}</pre></p>
            `;
            document.getElementById("detalhesLogContent").innerHTML = detalhes;
            new bootstrap.Modal(document.getElementById("detalhesLogModal")).show();
        })
        .catch(error => console.error("Erro ao buscar detalhes do log:", error));
}

function limparFiltros() {
    // Redireciona para a mesma página sem parâmetros na URL
    window.location.href = window.location.pathname;
}


