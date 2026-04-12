const API_URL = 'http://localhost:5000/solicitacoes';
const API_CONDOMINIOS_URL = 'http://localhost:5000/condominios';
let todasSolicitacoes = [];
let listaCondominios = [];
const itemsPerPage = 10;
let currentPage = 1;
let totalPages = 0;
let sortDirection = 'descending';

function isPdf(url) {
    if (!url) return false;
    if (url.startsWith('data:application/pdf')) return true;
    if (url.toLowerCase().endsWith('.pdf')) return true;
    if (/\.pdf(\?|$)/i.test(url)) return true;
    return false;
}

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

function isSolicitacaoExpirada(solicitacao) {
    if (solicitacao.status === 'confirmado' || !solicitacao.data_expiracao) {
        return false;
    }
    const dataExpiracao = new Date(solicitacao.data_expiracao);
    const dataAtual = new Date();
    return dataAtual > dataExpiracao;
}

function abrirObservacoesModal(id, observacoes, condominio = '') 
{
    document.getElementById('observacoesModalLabel').textContent = `Observações - Solicitação #${id} ${condominio ? `- ${condominio}` : ''}`;
    document.getElementById('observacoesModalBody').innerHTML = `
        <div class="observacoes-content" style="white-space: pre-wrap;">${observacoes.replace(/\n/g, '<br>')}</div>
        <button class="btn btn-sm btn-primary mt-2" onclick="navigator.clipboard.writeText('${observacoes.replace(/'/g, "\\'").replace(/"/g, '\\"')}').then(() => alert('Copiado!'))">Copiar</button>
    `;
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('observacoesModal'));
        modal.show();
    } else {
        alert('Observações: ' + observacoes);
    }
}

function abrirImagemModal(url) {
    if (isPdf(url)) {
        window.open(url, '_blank');
        return;
    }
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
    document.getElementById('imagemInput').addEventListener('change', handlePreviewImagem);
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
    const dataCriacaoHeader = document.getElementById('dataCriacaoHeader');
    if (dataCriacaoHeader) {
        dataCriacaoHeader.addEventListener('click', () => {
            sortDirection = sortDirection === 'ascending' ? 'descending' : 'ascending';
            exibirSolicitacoes();
        });
    }
});

function handlePreviewImagem(e) {
    const previewImg = document.getElementById('previewImagem');
    const previewPdf = document.getElementById('previewPdf');
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const dataUrl = e.target.result;
            if (isPdf(dataUrl)) {
                previewImg.classList.add('d-none');
                previewImg.src = '';
                previewPdf.href = dataUrl;
                previewPdf.classList.remove('d-none');
            } else {
                previewPdf.classList.add('d-none');
                previewPdf.href = '#';
                previewImg.src = dataUrl;
                previewImg.classList.remove('d-none');
            }
        };
        reader.readAsDataURL(file);
    } else {
        previewImg.classList.add('d-none');
        previewImg.src = '';
        previewPdf.classList.add('d-none');
        previewPdf.href = '#';
    }
}

function limparImagem() {
    document.getElementById('imagemInput').value = '';
    document.getElementById('imagemUrlHidden').value = '';
    const previewImg = document.getElementById('previewImagem');
    previewImg.src = '';
    previewImg.classList.add('d-none');
    const previewPdf = document.getElementById('previewPdf');
    previewPdf.classList.add('d-none');
    previewPdf.href = '#';
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
    let solicitacoesFiltradas;
    if (filtroCondominio === '') {
        solicitacoesFiltradas = todasSolicitacoes;
    } else {
        solicitacoesFiltradas = todasSolicitacoes.filter(s => 
            s.condominio === filtroCondominio
        );
    }
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
            if (isPdf(solicitacao.imagem_url)) {
                imagemCell = `<a href="${solicitacao.imagem_url}" target="_blank" rel="noopener noreferrer" class="pdf-thumb" title="Abrir PDF em nova guia">
                    <i class="fas fa-file-pdf"></i>
                </a>`;
            } else {
                imagemCell = `<img src="${solicitacao.imagem_url}" class="img-thumbnail" style="height: 50px; cursor: pointer;" 
                    onclick="abrirImagemModal('${solicitacao.imagem_url}')" title="Clique para ampliar">`;
            }
        } else {
            imagemCell = '<i class="fas fa-image text-muted"></i>';
        }
        const observacoesTruncadas = truncarTexto(solicitacao.observacoes);
        const observacoesCompletas = solicitacao.observacoes || '';
        const observacoesCell = observacoesCompletas ? 
            `<div class="d-flex align-items-center">
                <span class="text-truncate" style="max-width: 150px;" data-bs-toggle="tooltip" title="${observacoesCompletas.replace(/"/g, '&quot;')}">${observacoesTruncadas}</span>
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
            <td class="d-none d-md-table-cell">${formatarDataExibicao(solicitacao.data_expiracao)}</td>
            <td class="d-none d-md-table-cell">${solicitacao.placa_veiculo}</td>
            <td class="d-none d-md-table-cell">${observacoesCell}</td>
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
    const dataCriacaoHeader = document.getElementById('dataCriacaoHeader');
    if (dataCriacaoHeader) {
        dataCriacaoHeader.innerHTML = `Data Criação <i class="fas fa-sort-${sortDirection === 'ascending' ? 'up' : 'down'}"></i>`;
    }
}

function filtrarSolicitacoes() {
    currentPage = 1;
    exibirSolicitacoes();
}

async function carregarCondominios() {
    try {
        const response = await fetch(API_CONDOMINIOS_URL);
        if (!response.ok) {
            throw new Error('Erro ao carregar condominios');
        }
        const condominiosData = await response.json();
        listaCondominios = condominiosData.map(cond => cond.nome);
        preencherSelectCondominios(document.getElementById('condominio'), listaCondominios);
        preencherFiltroCondominios(todasSolicitacoes);
    } catch (error) {
        console.error("Erro ao carregar condomínios:", error);
    }
}

function preencherSelectCondominios(selectElement, condominios) {
    selectElement.innerHTML = '<option value="">Selecione um condomínio</option>';
    condominios.forEach(condominio => {
        const option = document.createElement('option');
        option.value = condominio;
        option.textContent = condominio;
        selectElement.appendChild(option);
    });
}

async function adicionarNovoCondominio() {
    const novoCondominio = window.prompt("Digite o nome do novo condomínio:");
    if (!novoCondominio || novoCondominio.trim() === '') {
        return;
    }
    const condominio = novoCondominio.trim();
    if (listaCondominios.includes(condominio)) {
        alert("Este condomínio já existe!");
        return;
    }
    try {
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
        await carregarCondominios();
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
    try {
        const response = await fetch(`${API_URL}/${id}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Erro ao carregar");
        }
        const data = await response.json();
        function formatarParaInput(dataString) {
            if (!dataString) return '';
            const date = new Date(dataString);
            const offset = date.getTimezoneOffset() * 60000;
            return new Date(date.getTime() - offset).toISOString().slice(0, 16);
        }
        const tabela = document.getElementById('tabelaSolicitacoes');
        if (tabela) {
            tabela.classList.add('d-none');
        }
        document.getElementById('paginationContainer').classList.add('d-none');
        const filtroContainer = document.getElementById('filtroCondominioContainer');
        if (filtroContainer) {
            filtroContainer.classList.add('d-none');
        }
        document.getElementById('solicitacaoId').value = data.id;
        document.getElementById('nome').value = data.nome || '';
        document.getElementById('tipo').value = data.tipo || '';
        document.getElementById('condominio').value = data.condominio || '';
        document.getElementById('dataVisita').value = formatarParaInput(data.data_visita) || '';
        document.getElementById('dataExpiracao').value = formatarParaInput(data.data_expiracao) || '';
        document.getElementById('placa').value = data.placa_veiculo || '';
        document.getElementById('observacoes').value = data.observacoes || '';
        document.getElementById('imagemUrlHidden').value = data.imagem_url || '';
        document.getElementById('status').value = data.status || 'pendente';
        const previewImg = document.getElementById('previewImagem');
        const previewPdf = document.getElementById('previewPdf');
        if (data.imagem_url) {
            if (isPdf(data.imagem_url)) {
                previewImg.classList.add('d-none');
                previewImg.src = '';
                previewPdf.href = data.imagem_url;
                previewPdf.classList.remove('d-none');
            } else {
                previewPdf.classList.add('d-none');
                previewPdf.href = '#';
                previewImg.src = data.imagem_url;
                previewImg.classList.remove('d-none');
            }
        } else {
            previewImg.classList.add('d-none');
            previewImg.src = '';
            previewPdf.classList.add('d-none');
            previewPdf.href = '#';
        }
        document.getElementById('formContainer').classList.remove('d-none');
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
