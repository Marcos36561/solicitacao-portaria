const API_URL = 'http://192.168.1.20:5000/solicitacoes';
const API_CONDOMINIOS_URL = 'http://192.168.1.20:5000/condominios';

let todasSolicitacoes = [];
let listaCondominios = [];

// Configuração da paginação
const itemsPerPage = 10; // Quantidade de itens por página
let currentPage = 1;
let totalPages = 0;

// Estado de ordenação
let sortDirection = 'descending'; // Inicialmente ordena por data_criacao decrescente

// Funções de formatação de data
function formatarDataExibicao(dataString) {
    if (!dataString) return 'N/A';
    const [datePart, timePart] = dataString.split(' ');
    const [year, month, day] = datePart.split('-');
    const [hours, minutes] = timePart.split(':');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function truncarTexto(texto, tamanhoMaximo = 30) {
    if (!texto) return '';
    if (texto.length <= tamanhoMaximo) return texto;
    return texto.substring(0, tamanhoMaximo) + '...';
}

// Função para verificar se a solicitação está expirada
function isSolicitacaoExpirada(solicitacao) {
    if (solicitacao.status === 'confirmado' || !solicitacao.data_expiracao) {
        return false;
    }
    const dataExpiracao = new Date(solicitacao.data_expiracao);
    const dataAtual = new Date();
    return dataAtual > dataExpiracao;
}

function abrirObservacoesModal(id, observacoes, condominio = '') {
    if (!document.getElementById('observacoesModal')) {
        const modalDiv = document.createElement('div');
        modalDiv.innerHTML = modalHTML;
        document.body.appendChild(modalDiv.firstChild);
    }

    document.getElementById('observacoesModalLabel').textContent = `Observações - Solicitação #${id} ${condominio ? `- ${condominio}` : ''}`;
    
    document.getElementById('observacoesModalBody').innerHTML = `
        <div class="observacoes-content" style="white-space: pre-wrap;">${observacoes.replace(/\n/g, '<br>')}</div>
        <button class="btn btn-sm btn-primary mt-2" onclick="navigator.clipboard.writeText('${observacoes.replace(/'/g, "\\'").replace(/"/g, '\\"')}').then(() => alert('Copiado!'))">Copiar</button>
    `;
    
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('observacoesModal'));
        modal.show();
    } else {
        console.error('Bootstrap não está disponível. Verifique se o script do Bootstrap foi carregado.');
        alert('Observações: ' + observacoes);
    }
}

function abrirImagemModal(url) {
    const imagemModal = document.getElementById('imagemModalConteudo');
    imagemModal.src = url;
    
    const modal = new bootstrap.Modal(document.getElementById('imagemModal'));
    modal.show();
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap não está disponível. Alguns recursos podem não funcionar.');
    }
    carregarSolicitacoes();
    carregarCondominios();
    document.getElementById('btnNovoCondominio').addEventListener('click', adicionarNovoCondominio);
    document.getElementById('btnNovaSolicitacao').addEventListener('click', mostrarFormulario);
    document.getElementById('btnCancelar').addEventListener('click', esconderFormulario);
    document.getElementById('solicitacaoForm').addEventListener('submit', salvarSolicitacao);
    document.getElementById('imagemInput').addEventListener('change', previewImagem);
    document.getElementById('btnLimparImagem').addEventListener('click', limparImagem);
    document.getElementById('filtroCondominio').addEventListener('change', filtrarSolicitacoes);
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            exibirSolicitacoes();
        }
    });  
    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            exibirSolicitacoes();
        }
    });
    // Adicionar evento de clique no cabeçalho "Data Criação"
    const dataCriacaoHeader = document.getElementById('dataCriacaoHeader');
    if (dataCriacaoHeader) {
        dataCriacaoHeader.addEventListener('click', () => {
            sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
            exibirSolicitacoes();
        });
    }
});

function previewImagem(e) {
    const previewImagem = document.getElementById('previewImagem');
    const file = e.target.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewImagem.src = e.target.result;
            previewImagem.classList.remove('d-none');
        };
        
        reader.readAsDataURL(file);
    } else {
        previewImagem.classList.add('d-none');
    }
}

function limparImagem() {
    document.getElementById('imagemInput').value = '';
    document.getElementById('imagemUrlHidden').value = '';
    document.getElementById('previewImagem').classList.add('d-none');
}

async function carregarSolicitacoes() {
    try {
        const response = await fetch(API_URL);
        const solicitacoes = await response.json();

        todasSolicitacoes = solicitacoes;

        preencherFiltroCondominios(todasSolicitacoes);
        currentPage = 1;
        exibirSolicitacoes();
    } catch (error) {
        console.error("Erro ao carregar solicitações:", error);
        alert("Erro ao carregar solicitações: " + error.message);
    }
}

function exibirSolicitacoes() {
    const filtroCondominio = document.getElementById('filtroCondominio').value;
    console.log("Filtro selecionado:", filtroCondominio);
    
    let solicitacoesFiltradas;
    
    if (filtroCondominio === '') {
        solicitacoesFiltradas = todasSolicitacoes;
    } else {
        solicitacoesFiltradas = todasSolicitacoes.filter(s => 
            s.condominio === filtroCondominio
        );
    }

    // Ordenar por data_criacao
    solicitacoesFiltradas.sort((a, b) => {
        const dateA = new Date(a.data_criacao);
        const dateB = new Date(b.data_criacao);
        return sortDirection === 'ascending' ? dateA - dateB : dateB - dateA;
    });

    totalPages = Math.ceil(solicitacoesFiltradas.length / itemsPerPage);
    
    if (currentPage > totalPages) {
        currentPage = Math.max(1, totalPages);
    }
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, solicitacoesFiltradas.length);
    
    const itensPagina = solicitacoesFiltradas.slice(startIndex, endIndex);

    const tabela = document.getElementById('tabelaSolicitacoes');
    tabela.innerHTML = '';

    itensPagina.forEach(solicitacao => {
        const tr = document.createElement('tr');

        let imagemCell = '';
        if (solicitacao.imagem_url) {
            imagemCell = `<img src="${solicitacao.imagem_url}" class="img-thumbnail" style="height: 50px; cursor: pointer;" 
                        onclick="abrirImagemModal('${solicitacao.imagem_url}')">`;
        } else {
            imagemCell = '<i class="fas fa-image text-muted"></i>';
        }

        const observacoesTruncadas = truncarTexto(solicitacao.observacoes);
        const observacoesCompletas = solicitacao.observacoes || '';
        
        const observacoesCell = observacoesCompletas ? 
            `<div class="d-flex align-items-center">
                <span class="text-truncate" style="max-width: 150px;" data-bs-toggle="tooltip" title="${observacoesCompletas.replace(/"/g, '"')}">${observacoesTruncadas}</span>
                <button class="btn btn-sm btn-info ms-2" onclick="abrirObservacoesModal('${solicitacao.id}', '${observacoesCompletas.replace(/'/g, "\\'").replace(/"/g, '\\"')}', '${solicitacao.condominio || ''}')">
                    <i class="fas fa-eye"></i>
                </button>
             </div>` : '';

        let statusCell = `<span class="badge ${getStatusClass(solicitacao.status)}">${solicitacao.status}</span>`;
        if (isSolicitacaoExpirada(solicitacao)) {
            statusCell += ` <span class="badge bg-danger">Expirado</span>`;
        }

        tr.innerHTML = `
            <td>${solicitacao.condominio}</td>
            <td>${solicitacao.nome}</td>
            <td>${solicitacao.tipo}</td>
            <td>${formatarDataExibicao(solicitacao.data_visita)}</td>
            <td>${formatarDataExibicao(solicitacao.data_expiracao)}</td>
            <td>${solicitacao.placa_veiculo}</td>
            <td>${observacoesCell}</td>
            <td>${imagemCell}</td>
            <td>${statusCell}</td>
            <td>${formatarDataExibicao(solicitacao.data_criacao)}</td>
            <td>
                <button class="btn btn-sm btn-warning me-2" onclick="editarSolicitacao(${solicitacao.id})">Editar</button>
                <button class="btn btn-sm btn-danger" onclick="excluirSolicitacao(${solicitacao.id})">Excluir</button>
            </td>
        `;
        tabela.appendChild(tr);
    });

    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    document.getElementById('currentPage').textContent = currentPage;
    document.getElementById('totalPages').textContent = totalPages;
    document.getElementById('totalItems').textContent = solicitacoesFiltradas.length;
    
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages || totalPages === 0;

    // Atualizar o ícone de ordenação no cabeçalho
    const dataCriacaoHeader = document.getElementById('dataCriacaoHeader');
    if (dataCriacaoHeader) {
        dataCriacaoHeader.innerHTML = `Data Criação <i class="fas fa-sort-${sortDirection === 'ascending' ? 'up' : 'down'}"></i>`;
    }
}

function filtrarSolicitacoes() {
    currentPage = 1;
    exibirSolicitacoes();
}

// Função para carregar a lista de condomínios
async function carregarCondominios() {
    try {
        const response = await fetch(API_CONDOMINIOS_URL);
        if (!response.ok) {
            throw new Error('Erro ao carregar condominios');
        }
        
        const condominiosData = await response.json();

        // Extrair apenas os nomes dos condomínios para manter compatibilidade com o código existente
        listaCondominios = condominiosData.map(cond => cond.nome);
        
        // Preencher o select de condomínios no formulário
        preencherSelectCondominios(document.getElementById('condominio'), listaCondominios);
        
        // Também atualizar o filtro de condomínios
        preencherFiltroCondominios(todasSolicitacoes);
        
    } catch (error) {
        console.error("Erro ao carregar condomínios:", error);
    }
}

// Função para preencher um select com a lista de condomínios
function preencherSelectCondominios(selectElement, condominios) {
    // Manter apenas a primeira opção (placeholder)
    selectElement.innerHTML = '<option value="">Selecione um condomínio</option>';
    
    // Adicionar cada condomínio como uma opção
    condominios.forEach(condominio => {
        const option = document.createElement('option');
        option.value = condominio;
        option.textContent = condominio;
        selectElement.appendChild(option);
    });
}

// Função para adicionar um novo condomínio
async function adicionarNovoCondominio() {
    const novoCondominio = window.prompt("Digite o nome do novo condomínio:");
    
    if (!novoCondominio || novoCondominio.trim() === '') {
        return;
    }
    
    const condominio = novoCondominio.trim();
    
    // Verificar se já existe
    if (listaCondominios.includes(condominio)) {
        alert("Este condomínio já existe!");
        return;
    }

    try {
        // Enviar para o servidor
        const response = await fetch(API_CONDOMINIOS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nome: condominio })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao salvar condomínio');
        }

        const novoCond = await response.json();

        // Recarregar a lista de condomínios do servidor para garantir que temos os dados atualizados
        await carregarCondominios();

        // Selecionar o novo condomínio no select
        document.getElementById('condominio').value = novoCond.nome;
        
        alert('Condomínio adicionado com sucesso!');

    } catch (error) {
        alert(`Erro: ${error.message}`);
        console.error('Erro detalhado:', error);
    }
}

function preencherFiltroCondominios(solicitacoes) {
    const selectFiltro = document.getElementById('filtroCondominio');
    
    if (!selectFiltro) {
        console.error("Elemento 'filtroCondominio' não encontrado no DOM");
        return;
    }

    selectFiltro.innerHTML = '';

    const optionTodos = document.createElement('option');
    optionTodos.value = '';
    optionTodos.textContent = 'Todos os Condomínios';
    selectFiltro.appendChild(optionTodos);
    
    const condominios = [...new Set(solicitacoes.map(s => s.condominio).filter(c => c))];
    
    condominios.sort();

    condominios.forEach(condominio => {
        const option = document.createElement('option');
        option.value = condominio;
        option.textContent = condominio;
        selectFiltro.appendChild(option);
    });    
}

function mostrarFormulario() {
    document.getElementById('tabelaSolicitacoes').classList.add('d-none');
    document.getElementById('paginationContainer').classList.add('d-none');
    const filtroContainer = document.getElementById('filtroCondominio').closest('.row');
    if (filtroContainer) {
        filtroContainer.classList.add('d-none');
    }
    document.getElementById('formContainer').classList.remove('d-none');
    document.getElementById('solicitacaoId').value = '';
    document.getElementById('solicitacaoForm').reset();
}

function esconderFormulario() {
    document.getElementById('formContainer').classList.add('d-none');
    document.getElementById('tabelaSolicitacoes').classList.remove('d-none');
    document.getElementById('paginationContainer').classList.remove('d-none');
    const filtroContainer = document.getElementById('filtroCondominio').closest('.row');
    if (filtroContainer) {
        filtroContainer.classList.remove('d-none');
    }
}

async function uploadImagem(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao fazer upload da imagem');
        }
        
        const data = await response.json();
        return data.filepath;
    } catch (error) {
        console.error('Erro no upload:', error);
        alert(`Erro ao fazer upload: ${error.message}`);
        return null;
    }
}

async function salvarSolicitacao(event) {
    event.preventDefault();

    const formatarDataParaBackend = (dataInput) => {
        if (!dataInput) return null;
        const data = new Date(dataInput + 'Z');
        return data.toISOString().replace('T', ' ').slice(0, 19);
    };

    const imagemInput = document.getElementById('imagemInput');
    let imagemUrl = document.getElementById('imagemUrlHidden').value;

    if (imagemInput.files.length > 0) {
        const btnSubmit = document.querySelector('#solicitacaoForm button[type="submit"]');
        const btnText = btnSubmit.innerHTML;
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
        
        const novaImagemUrl = await uploadImagem(imagemInput.files[0]);
        
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = btnText;
        
        if (novaImagemUrl) {
            imagemUrl = novaImagemUrl;
        } else {
            if (!confirm('Erro ao fazer upload da imagem. Deseja continuar sem a imagem?')) {
                return;
            }
        }
    }

    const formData = {
        nome: document.getElementById('nome').value,
        tipo: document.getElementById('tipo').value,
        condominio: document.getElementById('condominio').value,
        data_visita: formatarDataParaBackend(document.getElementById('dataVisita').value),
        data_expiracao: formatarDataParaBackend(document.getElementById('dataExpiracao').value),
        placa_veiculo: document.getElementById('placa').value,
        observacoes: document.getElementById('observacoes').value,
        imagem_url: imagemUrl,
        status: document.getElementById('status').value
    };

    if (!formData.nome || !formData.tipo || !formData.status) {
        alert('Por favor, preencha todos os campos obrigatórios!');
        return;
    }

    const id = document.getElementById('solicitacaoId').value;
    const url = id ? `${API_URL}/${id}` : API_URL;
    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao salvar');
        }

        esconderFormulario();
        carregarSolicitacoes();

        const condominio = document.getElementById('condominio').value;
    
        // Se for um novo condomínio, adicionar à lista
        if (condominio && !listaCondominios.includes(condominio)) {
            listaCondominios.push(condominio);
            listaCondominios.sort();
        }

        alert('Solicitação salva com sucesso!');
    } catch (error) {
        alert(`Erro: ${error.message}`);
        console.error('Erro detalhado:', error);
    }
}

async function editarSolicitacao(id) {
    console.log("Função editarSolicitacao chamada com id:", id);

    try {
        console.log("Tentando fazer fetch da solicitação");
        const response = await fetch(`${API_URL}/${id}`);
        
        if (!response.ok) {
            console.error("Resposta da API não ok:", response.status, response.statusText);
            const error = await response.json();
            throw new Error(error.message || "Erro ao carregar");
        }
        
        const data = await response.json();
        console.log("Dados da solicitação recebidos:", data);

        function formatarParaInput(dataString) {
            if (!dataString) return '';
            const date = new Date(dataString);
            const offset = date.getTimezoneOffset() * 60000;
            return new Date(date.getTime() - offset).toISOString().slice(0, 16);
        }

        const tabela = document.getElementById('tabelaSolicitacoes');
        if (tabela) {
            console.log("Ocultando a tabela");
            tabela.classList.add('d-none');
        }

        document.getElementById('paginationContainer').classList.add('d-none');

        const filtroContainer = document.getElementById('filtroCondominioContainer');
        if (filtroContainer) {
            console.log("Ocultando filtro de condomínios");
            filtroContainer.classList.add('d-none');
        }

        console.log("Preenchendo formulário com dados da solicitação");
        document.getElementById('tabelaSolicitacoes').classList.add('d-none');
        document.getElementById('solicitacaoId').value = data.id;
        document.getElementById('nome').value = data.nome || '';
        document.getElementById('tipo').value = data.tipo || '';
        document.getElementById('condominio').value = data.condominio || '';
        document.getElementById('dataVisita').value = formatarParaInput(data.data_visita)|| '';
        document.getElementById('dataExpiracao').value = formatarParaInput(data.data_expiracao)|| '';
        document.getElementById('placa').value = data.placa_veiculo || '';
        document.getElementById('observacoes').value = data.observacoes || '';
        document.getElementById('imagemUrlHidden').value = data.imagem_url || '';
        const previewImagem = document.getElementById('previewImagem');
        document.getElementById('status').value = data.status || 'pendente';

        console.log("Mostrando o formulário");
        document.getElementById('formContainer').classList.remove('d-none');

        if (data.imagem_url) {
            previewImagem.src = data.imagem_url;
            previewImagem.classList.remove('d-none');
        } else {
            previewImagem.classList.add('d-none');
        }

    } catch (error) {
        console.error("Erro detalhado:", error);
        alert(`Erro: ${error.message}`);
        document.getElementById('tabelaSolicitacoes').classList.remove('d-none');
        document.getElementById('paginationContainer').classList.remove('d-none');
    }
}

async function excluirSolicitacao(id) {
    if (!confirm('Tem certeza que deseja excluir esta solicitação?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Erro ao excluir');

        carregarSolicitacoes();
        alert('Solicitação excluída com sucesso!');
    } catch (error) {
        alert('Erro: ' + error.message);
    }
}

function getStatusClass(status) {
    const classes = {
        pendente: 'bg-warning text-dark',
        confirmado: 'bg-success',
        cancelado: 'bg-danger'
    };
    return classes[status] || 'bg-secondary';
}

window.abrirObservacoesModal = abrirObservacoesModal;
window.editarSolicitacao = editarSolicitacao;
window.excluirSolicitacao = excluirSolicitacao;
window.abrirImagemModal = abrirImagemModal;