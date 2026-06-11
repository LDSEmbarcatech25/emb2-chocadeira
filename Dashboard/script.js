let intervaloAtualizacao = null;
let ipESP = "";
let meuGrafico = null;
let graficoSD = null; 

function inicializarGraficoRealTime() {
    const ctx = document.getElementById('graficoHistorico').getContext('2d');
    
    Chart.defaults.color = '#90a4ae';
    Chart.defaults.borderColor = 'rgba(18, 48, 63, 0.5)';

    meuGrafico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], 
            datasets: [
                {
                    label: 'Temp Caixa',
                    borderColor: '#f07d22',   
                    backgroundColor: 'transparent',
                    data: [],
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#f07d22',
                    yAxisID: 'y'
                },
                {
                    label: 'Temp Ambiente',
                    borderColor: '#3ca0f0',   
                    backgroundColor: 'transparent',
                    data: [],
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#3ca0f0',
                    yAxisID: 'y'
                },
                {
                    label: 'Umidade',
                    borderColor: '#46b46e',   
                    backgroundColor: 'transparent',
                    data: [],
                    borderWidth: 3,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#46b46e',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { boxWidth: 40, padding: 20 }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 15,
                    max: 35,
                    title: { display: true, text: 'Temperatura (°C)' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    title: { display: true, text: 'Umidade (%)' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

function iniciarMonitoramento() {
    const inputIp = document.getElementById('esp-ip').value.trim();
    if (!inputIp) {
        alert("Por favor, insira o IP do ESP32.");
        return;
    }
    
    ipESP = inputIp;
    const sdStatus = document.getElementById('status-sd');
    sdStatus.innerText = "SD Status: Conectando...";

    if (intervaloAtualizacao) clearInterval(intervaloAtualizacao);
    if (!meuGrafico) inicializarGraficoRealTime();

    buscarDados();
    intervaloAtualizacao = setInterval(buscarDados, 2000); 
}

async function buscarDados() {
    try {
        const response = await fetch(`http://${ipESP}/api/status`, {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache'
        });

        if (!response.ok) throw new Error("Erro na rede");

        const dados = await response.json();
        atualizarInterface(dados);
        atualizarGrafico(dados);
    } catch (error) {
        console.error("Erro:", error);
        document.getElementById('status-sd').innerText = "SD Status: Desconectado / Erro de Comunicação";
    }
}

function atualizarInterface(dados) {
    document.getElementById('temp-caixa').innerText = dados.temp_caixa_c !== null ? `${dados.temp_caixa_c.toFixed(1)} °C` : "Erro";
    document.getElementById('temp-amb').innerText = dados.temp_amb_c !== null ? `${dados.temp_amb_c.toFixed(1)} °C` : "Erro";
    document.getElementById('umidade').innerText = dados.umidade !== null ? `${dados.umidade.toFixed(1)} %` : "Erro";

    // Rastrear globalmente o nome do arquivo enviado pela rota de status do ESP32
    window.ultimoNomeFoto = dados.ultima_foto || "Nenhuma";

    const portaEl = document.getElementById('status-porta');
    const portaIcon = document.getElementById('icon-porta');
    if (dados.ir_detectado) {
        portaEl.innerText = "Fechada";
        portaEl.style.color = "#46b46e"; 
        portaIcon.className = "fa-solid fa-lock icon-orange";
    } else {
        portaEl.innerText = "Aberta";
        portaEl.style.color = "#ef4444"; 
        portaIcon.className = "fa-solid fa-lock-open icon-orange";
    }

    const lampEl = document.getElementById('status-lamp');
    const lampIcon = document.getElementById('icon-lamp');
    if (dados.lampada) {
        lampEl.innerText = "Ligada";
        lampEl.style.color = "#f59e0b"; 
        lampIcon.className = "fa-solid fa-lightbulb icon-red"; 
    } else {
        lampEl.innerText = "Desligada";
        lampEl.style.color = "#90a4ae";
        lampIcon.className = "fa-solid fa-power-off icon-red";
    }

    const fanEl = document.getElementById('status-fan');
    const fanIcon = document.getElementById('icon-fan');
    if (dados.ventoinha) {
        fanEl.innerText = "Ligada";
        fanEl.style.color = "#46b46e";
        fanIcon.classList.add('fa-spin'); 
        fanIcon.style.color = "#46b46e";
    } else {
        fanEl.innerText = "Desligada";
        fanEl.style.color = "#90a4ae";
        fanIcon.classList.remove('fa-spin');
        fanIcon.style.color = "#90a4ae";
    }

    const btnLamp = document.getElementById('btn-force-lamp');
    const btnFan = document.getElementById('btn-force-fan');
    
    if (dados.forcar_lampada) {
        btnLamp.style.backgroundColor = "#f07d22";
        btnLamp.style.borderColor = "#f07d22";
        btnLamp.innerHTML = '<i class="fa-solid fa-lightbulb"></i> Lâmpada (FORÇADA)';
    } else {
        btnLamp.style.backgroundColor = "#0f3547";
        btnLamp.style.borderColor = "var(--cyan)";
        btnLamp.innerHTML = '<i class="fa-solid fa-lightbulb"></i> Forçar Lâmpada (AUTO)';
    }

    if (dados.forcar_ventoinha) {
        btnFan.style.backgroundColor = "#46b46e";
        btnFan.style.borderColor = "#46b46e";
        btnFan.innerHTML = '<i class="fa-solid fa-wind"></i> Ventoinha (FORÇADA)';
    } else {
        btnFan.style.backgroundColor = "#0f3547";
        btnFan.style.borderColor = "var(--cyan)";
        btnFan.innerHTML = '<i class="fa-solid fa-wind"></i> Forçar Ventoinha (AUTO)';
    }

    document.getElementById('status-sd').innerText = dados.sd_ok ? "SD Status: Atualizado e Operacional" : "SD Status: Falha / Cartão ausente";
    document.getElementById('ultima-att').innerText = `Atualizado: ${dados.data} ${dados.hora}`;
}

function atualizarGrafico(dados) {
    if (!meuGrafico) return;

    const horaAgora = dados.hora || new Date().toLocaleTimeString('pt-BR', {hour12: false});

    if (meuGrafico.data.labels.length > 15) {
        meuGrafico.data.labels.shift();
        meuGrafico.data.datasets.forEach(dataset => dataset.data.shift());
    }

    meuGrafico.data.labels.push(horaAgora);
    meuGrafico.data.datasets[0].data.push(dados.temp_caixa_c);
    meuGrafico.data.datasets[1].data.push(dados.temp_amb_c);
    meuGrafico.data.datasets[2].data.push(dados.umidade);

    meuGrafico.update();
}

// -------------------------------------------------------------------
// FUNÇÕES DO HISTÓRICO CSV
// -------------------------------------------------------------------
async function carregarHistoricoCSV() {
    if (!ipESP) {
        alert("Por favor, conecte-se ao IP primeiro.");
        return;
    }

    const btn = document.getElementById('btn-load-sd');
    const loadArea = document.getElementById('area-loading-sd');
    const graphArea = document.getElementById('area-grafico-sd');

    btn.innerText = "Processando...";
    btn.disabled = true;

    try {
        const response = await fetch(`http://${ipESP}/api/csv`);
        if (!response.ok) throw new Error("Erro ao baixar arquivo CSV.");
        
        const csvText = await response.text();
        processarDadosCSV(csvText);

        loadArea.style.display = "none";
        graphArea.style.display = "block";

    } catch (error) {
        console.error("Erro CSV:", error);
        alert("Não foi possível carregar o histórico. Verifique se o cartão SD está inserido e se há dados gravados.");
    } finally {
        btn.innerHTML = `<i class="fa-solid fa-cloud-arrow-down"></i> Atualizar Dados`;
        btn.disabled = false;
    }
}

function processarDadosCSV(csvText) {
    const linhas = csvText.split('\n');
    const rotulos = [];
    const tCaixa = [];
    const tAmb = [];
    const umid = [];

    for (let i = 1; i < linhas.length; i++) {
        const linha = linhas[i].trim();
        if (!linha) continue; 

        const colunas = linha.split(',');
        if (colunas.length >= 5) {
            rotulos.push(`${colunas[0]} ${colunas[1]}`); 
            tAmb.push(parseFloat(colunas[2]));
            umid.push(parseFloat(colunas[3]));
            tCaixa.push(parseFloat(colunas[4]));
        }
    }
    renderizarGraficoSD(rotulos, tCaixa, tAmb, umid);
}

function renderizarGraficoSD(rotulos, tCaixa, tAmb, umid) {
    const ctx = document.getElementById('graficoSD').getContext('2d');
    if (graficoSD) graficoSD.destroy();

    graficoSD = new Chart(ctx, {
        type: 'line',
        data: {
            labels: rotulos, 
            datasets: [
                { label: 'Temp Caixa Histórico', borderColor: '#f07d22', backgroundColor: 'transparent', data: tCaixa, borderWidth: 2, tension: 0.1, pointRadius: 0, yAxisID: 'y' },
                { label: 'Temp Ambiente Histórico', borderColor: '#3ca0f0', backgroundColor: 'transparent', data: tAmb, borderWidth: 2, tension: 0.1, pointRadius: 0, yAxisID: 'y' },
                { label: 'Umidade Histórico', borderColor: '#46b46e', backgroundColor: 'transparent', data: umid, borderWidth: 2, tension: 0.1, pointRadius: 0, yAxisID: 'y1' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top', labels: { boxWidth: 40, padding: 20 } } },
            scales: { x: { ticks: { maxTicksLimit: 10 } }, y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Temperatura (°C)' } }, y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'Umidade (%)' }, grid: { drawOnChartArea: false } } }
        }
    });
}

// -------------------------------------------------------------------
// INTERVENÇÃO MANUAL E RESET
// -------------------------------------------------------------------
async function enviarComandoESP(rota) {
    if (!ipESP) {
        alert("Conecte-se ao IP da Chocadeira primeiro.");
        return;
    }
    try {
        const response = await fetch(`http://${ipESP}${rota}`, { method: 'GET', mode: 'cors', cache: 'no-cache' });
        if (response.ok) { buscarDados(); } else { alert("A placa rejeitou o comando."); }
    } catch (error) { alert("Falha de comunicação."); }
}

function alternarAtuador(atuador) {
    if (atuador === 'lampada') enviarComandoESP('/api/force/lampada');
    if (atuador === 'ventoinha') enviarComandoESP('/api/force/ventoinha');
}

function resetarPlaca() {
    if (confirm("Deseja realmente reiniciar fisicamente o ESP32?")) {
        enviarComandoESP('/api/reset');
        document.getElementById('status-sd').innerText = "SD Status: Reiniciando placa...";
    }
}

// -------------------------------------------------------------------
// NOVO: REQUISIÇÃO E DOWNLOAD DE IMAGEM
// -------------------------------------------------------------------
async function carregarUltimaFoto() {
    if (!ipESP) {
        alert("Por favor, conecte-se ao IP primeiro.");
        return;
    }

    const btn = document.getElementById('btn-load-photo');
    const placeholder = document.getElementById('area-placeholder-camera');
    const preview = document.getElementById('area-preview-camera');
    const img = document.getElementById('camera-frame');
    const downloadBtn = document.getElementById('btn-download-photo');
    const timestampEl = document.getElementById('photo-timestamp');

    btn.innerText = "Buscando Imagem...";
    btn.disabled = true;

    // Rota com token temporal para evitar cache no navegador do arquivo antigo
    const urlFoto = `http://${ipESP}/api/foto/recente?t=${new Date().getTime()}`;

    const imagemTeste = new Image();
    imagemTeste.onload = function() {
        img.src = urlFoto;
        downloadBtn.href = urlFoto;
        downloadBtn.style.display = "inline-flex";
        
        if (window.ultimoNomeFoto && window.ultimoNomeFoto !== "Nenhuma") {
            timestampEl.innerText = `Arquivo identificado no SD: ${window.ultimoNomeFoto}`;
            downloadBtn.download = window.ultimoNomeFoto;
        } else {
            timestampEl.innerText = "Foto gerada recuperada com sucesso.";
            downloadBtn.download = "ultima_abertura.jpeg";
        }

        placeholder.style.display = "none";
        preview.style.display = "block";
        
        btn.innerHTML = `<i class="fa-solid fa-camera"></i> Atualizar Foto`;
        btn.disabled = false;
    };

    imagemTeste.onerror = function() {
        alert("Nenhuma imagem disponível. A tampa pode não ter sido aberta ainda ou o cartão SD está inacessível.");
        btn.innerHTML = `<i class="fa-solid fa-camera"></i> Visualizar Foto`;
        btn.disabled = false;
    };

    imagemTeste.src = urlFoto;
}