// =================================
// Funções de manipulação de tabelas
// =================================

// Adiciona uma nova coluna a uma tabela
function adicionarColuna() {
    // Pega o nome da tabela e solicita ao usuário o nome e o tipo da nova coluna
    const tabela = document.getElementById("tabela-editar").value;
    const nomeColuna = prompt("Digite o nome da nova coluna:");
    const tipoColuna = prompt("Digite o tipo da nova coluna (ex: TEXT, INTEGER):");

    // Verifica se todos os campos necessários foram preenchidos
    if (!tabela || !nomeColuna || !tipoColuna) {
        alert("Tabela, nome da coluna e tipo são obrigatórios!");
        return;
    }

    // Envia a requisição para o backend para adicionar a nova coluna
    fetch(`/adicionar_coluna`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tabela, nomeColuna, tipoColuna })
    })
        .then(response => response.json())
        .then(data => {
            // Mostra mensagem de sucesso ou erro
            if (data.erro) {
                alert(`Erro: ${data.erro}`);
            } else {
                alert(data.mensagem);
                carregarColunas(); // Atualiza a lista de colunas
            }
        })
        .catch(error => console.error("Erro ao adicionar coluna:", error));
}

// Exclui uma coluna de uma tabela
function excluirColuna(nomeColuna) {
    // Pega o nome da tabela e verifica se a coluna foi informada
    const tabela = document.getElementById("tabela-editar").value;

    if (!tabela || !nomeColuna) {
        alert("Tabela e nome da coluna são obrigatórios!");
        return;
    }

    // Confirmação antes de excluir a coluna
    if (!confirm(`Tem certeza de que deseja excluir a coluna "${nomeColuna}"?`)) {
        return;
    }

    // Envia a requisição para o backend para excluir a coluna
    fetch(`/excluir_coluna`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tabela, nomeColuna })
    })
        .then(response => response.json())
        .then(data => {
            // Mostra mensagem de sucesso ou erro
            if (data.erro) {
                alert(`Erro: ${data.erro}`);
            } else {
                alert(data.mensagem);
                carregarColunas(); // Atualiza a lista de colunas
            }
        })
        .catch(error => console.error("Erro ao excluir coluna:", error));
}

// Carrega as colunas de uma tabela selecionada
function carregarColunas() {
    // Pega o nome da tabela selecionada
    const tabela = document.getElementById("tabela-editar").value;
    const colunasDiv = document.getElementById("colunas-tabela");

    // Se nenhuma tabela foi selecionada, exibe uma mensagem
    if (!tabela) {
        colunasDiv.innerHTML = "<p>Selecione uma tabela para visualizar as colunas.</p>";
        return;
    }

    // Faz uma requisição para obter as colunas da tabela
    fetch(`/colunas/${tabela}`)
        .then(response => response.json())
        .then(data => {
            colunasDiv.innerHTML = "";
            if (data.colunas && data.colunas.length > 0) {
                // Cria elementos para cada coluna e adiciona botões de editar/excluir
                data.colunas.forEach(coluna => {
                    const colunaDiv = document.createElement("div");
                    colunaDiv.classList.add("coluna-item");
                    colunaDiv.innerHTML = `
                        <span>${coluna}</span>
                        <button onclick="editarColuna('${coluna}')">Editar</button>
                        <button onclick="excluirColuna('${coluna}')">Excluir</button>
                    `;
                    colunasDiv.appendChild(colunaDiv);
                });
            } else {
                colunasDiv.innerHTML = "<p>Essa tabela não possui colunas adicionais.</p>";
            }
        })
        .catch(error => console.error("Erro ao carregar colunas:", error));
}

// ==============================
// Funções de manipulação de dados
// ==============================

// Remove um campo de coluna dinâmico
function removerColuna(botao) {
    // Remove o elemento pai do botão (campo da coluna)
    const campo = botao.parentElement;
    campo.remove();
}

// Redireciona para uma URL especificada no botão
function redirecionar(botao) {
    const url = botao.getAttribute("data-url");
    window.location.href = url;
}

// Apaga uma tabela selecionada
function apagarTabela() {
    // Confirmação antes de apagar a tabela
    if (confirm("Tem certeza de que deseja apagar esta tabela? Essa ação não pode ser desfeita!")) {
        const form = document.getElementById("form-apagar");
        const formData = new FormData(form);

        // Envia a requisição para apagar a tabela
        fetch('/apagar_tabela', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            alert("Tabela apagada com sucesso!");
            window.location.reload(); // Recarrega a página para refletir as mudanças
        })
        .catch(error => {
            console.error("Erro ao apagar a tabela:", error);
            alert("Erro ao apagar a tabela.");
        });
    }
}

// Atualiza as colunas disponíveis para queries
function atualizarColunas() {
    // Pega o nome da tabela selecionada
    const tabela = document.getElementById("tabela").value;
    const colunasSelect = document.getElementById("colunas");

    // Se nenhuma tabela foi selecionada, limpa as colunas
    if (!tabela) {
        colunasSelect.innerHTML = "";
        return;
    }

    // Faz uma requisição para obter as colunas da tabela
    fetch(`/colunas/${tabela}`)
        .then(response => response.json())
        .then(data => {
            colunasSelect.innerHTML = "";
            // Adiciona as colunas como opções no select
            data.colunas.forEach(coluna => {
                const option = document.createElement("option");
                option.value = coluna;
                option.textContent = coluna;
                colunasSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Erro ao carregar colunas:", error));
}

// Executa uma query interativa
function executarQuery() {
    // Pega os valores selecionados para a query
    const tabela = document.getElementById("tabela").value;
    const colunas = Array.from(document.getElementById("colunas").selectedOptions).map(option => option.value);
    const filtros = document.getElementById("filtros").value;
    const ordenacao = document.getElementById("ordenacao").value;

    // Envia a query para o backend
    fetch("/executar_query_interativa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tabela, colunas, filtros, ordenacao })
    })
        .then(response => response.text())
        .then(html => {
            // Exibe o resultado da query no elemento de resultado
            document.getElementById("resultado").innerHTML = html;
        })
        .catch(error => console.error("Erro ao executar query:", error));
}

// ===========================
// Funções de animação
// ===========================

// Aplica animação de fade-in ao conteúdo principal
function aplicarFadeIn() {
    const main = document.querySelector("main");
    if (main) {
        main.style.opacity = 0;
        main.style.transition = "opacity 1s ease-in-out";
        setTimeout(() => {
            main.style.opacity = 1;
        }, 100);
    }
}

// Aplica animação de hover aos botões
function animarBotoes() {
    const botoes = document.querySelectorAll("button");
    botoes.forEach(botao => {
        botao.addEventListener("mouseover", () => {
            botao.style.transform = "scale(1.1)";
            botao.style.transition = "transform 0.3s ease";
        });
        botao.addEventListener("mouseout", () => {
            botao.style.transform = "scale(1)";
        });
    });
}

// Aplica animação de entrada ao cabeçalho
function animarCabecalho() {
    const header = document.querySelector("header");
    if (header) {
        header.style.transform = "translateY(-50px)";
        header.style.opacity = 0;
        header.style.transition = "transform 1s ease, opacity 1s ease";
        setTimeout(() => {
            header.style.transform = "translateY(0)";
            header.style.opacity = 1;
        }, 100);
    }
}

// Aplica animação de fade-in ao rodapé
function animarRodape() {
    const footer = document.querySelector("footer");
    if (footer) {
        footer.style.opacity = 0;
        footer.style.transition = "opacity 1s ease-in-out";
        setTimeout(() => {
            footer.style.opacity = 1;
        }, 500);
    }
}

// ===========================
// Inicialização
// ===========================

// Inicializa todas as animações ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
    console.log("libcore.js carregado com sucesso!");
    aplicarFadeIn();
    animarBotoes();
    animarCabecalho();
    animarRodape();
});