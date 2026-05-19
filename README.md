# PROJETO DE ENCERRAMENTO DE RESIDÊNCIA
### DISPOSITIVO IoT PARA CONTROLE MICROCLIMÁTICO E AUTOMAÇÃO DE CHOCADEIRAS ARTIFICIAIS

## 1. O Problema 

Sou Produtor de Aves em uma granja comercial de médio porte. A incubação artificial de ovos é uma etapa extremamente delicada do nosso negócio; o sucesso da eclosão depende diretamente da manutenção de uma temperatura e umidade rigorosamente estáveis dentro da chocadeira. Se a temperatura subir ou descer apenas 1°C além do limite por algumas horas, todo o lote de ovos pode ser perdido. Outro problema frequente é o esquecimento da porta ou tampa da chocadeira aberta pelos operadores, o que quebra o ciclo térmico e arruína a produção.

Precisamos de uma solução embarcada de controle em malha fechada e alta precisão para automatizar e monitorar nossas chocadeiras. O dispositivo deve medir continuamente a temperatura e a umidade interna do ar. Para a segurança do processo, um sensor de toque (Touch/Fim de curso) deve monitorar a abertura da porta. Todas as informações de telemetria precisam ser transmitidas para uma Dashboard remota e registradas de forma segura em um cartão SD para fins de auditoria e controle de qualidade biológica.

O sistema atuará de forma automatizada e responderá a comandos através dos seguintes eixos:

* **Controle Térmico de Precisão (Malha Fechada):** O dispositivo controlará dois relés. O primeiro acionará uma lâmpada de aquecimento e o segundo acionará um cooler (ventilador de resfriamento). O firmware deve operar de forma inteligente: se a temperatura cair, liga-se a lâmpada; se a temperatura subir demais, desliga-se a lâmpada e aciona-se o cooler para circular o ar e resfriar o ambiente.
* **Acompanhamento Visual da Incubação:** A câmera integrada capturará uma imagem automatizada uma vez por dia e a salvará no cartão SD, permitindo documentar visualmente o estado e a organização das bandejas de ovos ao longo do ciclo de incubação.
* **Supervisão e Controle Remoto:** O painel na internet deve permitir que o supervisor visualize os gráficos de temperatura/umidade, receba um alerta imediato em tempo real se a chocadeira foi aberta (sensor de toque ativado) e consiga enviar comandos para acionar os relés manualmente ou solicitar uma foto em tempo real do interior da chocadeira.

## 2. Recomendações de Firmware e Conectividade

* **Controle de Histerese (Malha Fechada):** O firmware deve implementar uma lógica robusta de histerese para os relés de aquecimento e resfriamento. Evite que oscilações milimétricas na leitura do sensor façam a lâmpada e o cooler ligarem e desligarem em intervalos curtíssimos de tempo, o que causaria desgaste prematuro dos atuadores.
* **Conectividade e Sincronismo Temporal (NTP):** O sistema deve se conectar à rede local para obter a hora exata via servidores NTP. Isso é mandatório para que as strings de texto gravadas no arquivo de log (`chocadeira.csv`) do cartão SD e as fotos diárias sejam marcadas com o registro cronológico perfeito do ciclo de incubação (ex: Dia 1 ao Dia 21).
* **Tratamento do Sensor de Toque:** No momento exato em que a chocadeira for aberta, o firmware deve registrar o evento no cartão SD e enviar um alerta tela para a Dashboard.
* **Comunicação Assíncrona via MQTT:** Utilize o protocolo MQTT para que o envio de telemetria contínua não concorra de forma bloqueante com o recebimento de comandos do operador (acionar foto, forçar cooler ou desligar lâmpada).
* **Gerenciamento do Sistema de Arquivos (SD Card):** Configurar o barramento para escrita contínua. Certifique-se de que o firmware abra, escreva e feche as instâncias de arquivos de imagem e texto de forma atômica para evitar corrupção em caso de queda de energia na granja.

## 3. Requisitos de Modelagem 3D (Gabinete)

O ambiente interno de uma chocadeira possui umidade controlada alta e fluxo de ar induzido, o que exige um design de case focado em isolamento e circulação:

* **Proteção Contra Umidade e Condensação:** O gabinete principal deve isolar a placa de controle (ESP32-S3), o módulo de relés e o leitor de cartão SD do ambiente altamente úmido da chocadeira, evitando que a condensação de água cause curtos-circuitos nas trilhas da placa.
* **Isolamento Dinâmico do Sensor de Clima:** O sensor de temperatura e umidade precisa de fluxo de ar direto para capturar o microclima real da chocadeira, mas não deve sofrer com a irradiação direta de calor da lâmpada de aquecimento. O modelo 3D deve conter uma sonda externa ou um suporte isolado que projete o sensor para a altura correta onde os ovos ficam posicionados.
* **Janelas de Interface Óptica e Cabeamento:**
    * Abertura para a lente da câmera com um ângulo de visão limpo, focado nas bandejas de ovos, sem que o plástico do case gere sombras.
    * Passe de fixação para o sensor de toque se alinhar mecanicamente com a aba de fechamento da porta.
    * Furações na base inferior do case (padrão prensa-cabos) para a saída organizada dos fios de alimentação e dos cabos de alta potência que vão para a lâmpada AC e para o cooler.

## 4. Entregável Inicial: Documento de Arquitetura e Viabilidade Técnica

Antes de iniciar o desenvolvimento prático do firmware ou a modelagem 3D do gabinete, a equipe deverá entregar um relatório técnico de arquitetura contendo obrigatoriamente:

* **4.1. Mapeamento de Hardware e Componentes:** A equipe deve mapear os componentes integrados e os periféricos da placa:
    * **Identificação:** Modelos exatos do sensor de temperatura/umidade do ar, do sensor de toque (Touch/Fim de curso), do leitor de cartão micro SD, dos módulos de relés e da câmera.
    * **Pinout (Tabela de GPIOs):** Tabela detalhada mapeando as conexões de todos os pinos de E/S utilizados no ESP32-S3, destacando os pinos de interrupção (sensor de toque) e as linhas de barramento (cartão SD).
    * **Especificação de Carga dos Relés:** Detalhamento da fiação e suporte de corrente dos relés para garantir o acionamento seguro da lâmpada de aquecimento e do motor do cooler.

* **4.2. Diagrama de Blocos do Sistema:** Apresentar um esquema gráfico modular do hardware. No centro deve figurar o microcontrolador ESP32-S3 e, ao redor, blocos conectados por setas indicando o fluxo de sinal:
    * **Setas de entrada (In):** Sensor de temperatura/umidade do ar, Sensor de toque e Câmera apontando para o ESP32-S3.
    * **Setas bidirecionais ($\leftrightarrow$):** ESP32-S3 conectado ao bloco do Cartão SD (via barramento SPI).
    * **Setas de saída (Out):** ESP32-S3 apontando para os blocos do Relé 1 (Bomba) e Relé 2 (Cooler).
    * **Fluxo de rede:** Seta indicando a transmissão bidirecional Wi-Fi com o Servidor/Dashboard.

* **4.3. Especificação do Algoritmo de Controle e IoT:**
    * **Lógica do Algoritmo Térmico:** Explicação matemática ou em fluxograma de como os relés ligarão/desligarão com base na temperatura lida (definição da janela de histerese).
    * **Estratégia de Arquivo no Cartão SD:** Definição da estrutura de dados textuais das colunas do arquivo CSV para fins de auditoria do lote de ovos.
    * **Protocolo de Aplicação de Rede e Payloads:** Definição e justificativa do protocolo de rede para transmissão de dados leves e mídia (fotos), acompanhado de exemplos de payloads JSON para comandos e alertas de porta aberta.
