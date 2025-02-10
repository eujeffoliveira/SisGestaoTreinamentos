/***************************************************************
 *                  FUNÇÕES DA PÁGINA DE LOGS
 ***************************************************************/

/**
 * Exibe os detalhes de um log em um modal.
 * @param {number} id - ID do log a ser exibido.
 */
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

/**
 * Exporta os logs para um dos formatos suportados: CSV, Excel ou PDF.
 * @param {string} formato - Formato do arquivo a ser exportado.
 */
function exportar(formato) {
    window.location.href = `/logs/exportar/${formato}`;
}

/**
 * Limpa os filtros de busca e recarrega a página sem parâmetros na URL.
 */
function limparFiltros() {
    window.location.href = window.location.pathname;
}

/**
 * Inicializa a tabela de logs utilizando List.js para pesquisa e ordenação.
 */
document.addEventListener('DOMContentLoaded', function () {
    const tableId = 'logsTable';  // Substitua pelo ID real da sua tabela de logs
    const tableElement = document.getElementById(tableId);

    if (tableElement) {
        const tableInstance = new List(tableId, {
            valueNames: ['id_log', 'usuario', 'acao', 'tabela', 'data_hora'],
            page: 15,
            pagination: {
                paginationClass: 'pagination',
                outerWindow: 1,
                innerWindow: 2,
            }
        });
    }
});
