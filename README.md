# Robô EV3 – Busca, Coleta e Depósito de Objeto Vermelho

Este projeto controla um robô LEGO EV3 que navega autonomamente, detecta objetos vermelhos, coleta com uma garra mecânica e deposita em uma caçamba.

## O que o robô faz

O robô executa as seguintes ações de forma autônoma:

1. **Navegação**: Move-se pelo ambiente buscando objetos vermelhos
2. **Detecção de obstáculos**: Identifica paredes brancas e executa manobra evasiva (meia-volta)
3. **Detecção de objeto**: Localiza objetos vermelhos usando sensores de cor e luz
4. **Coleta**: Abre a garra, avança até o objeto, fecha a garra para agarrar
5. **Depósito**: Levanta o braço, abre a garra para soltar o objeto na caçamba
6. **Retorno**: Baixa a garra de volta à posição inicial para continuar a busca

O robô continua buscando até encontrar o objeto ou atingir o tempo limite de busca.

## Como funciona

### Sistema de Detecção

O robô utiliza apenas um **ColorSensor** para duas funções principais:
- **Detecção de paredes**: Identifica superfícies brancas para evitar colisões
- **Detecção de objetos vermelhos**: Combina leitura de cor, reflexão de luz e luz ambiente para detectar objetos vermelhos tanto de perto quanto de longe

A detecção de longo alcance funciona analisando a reflexão de luz e a luz ambiente, permitindo que o robô identifique objetos antes de chegar muito próximo.

### Sistema de Movimento

O robô possui dois motores nas rodas que permitem:
- Movimento para frente e para trás
- Giro no próprio eixo para mudar de direção
- Correção automática de diferenças entre os motores para manter trajetória reta

### Sistema de Garra

A garra é controlada por dois motores independentes:
- **Motor de abertura/fechamento**: Controla a garra para agarrar objetos
- **Motor de elevação**: Levanta e abaixa o braço para depositar objetos

A sequência de coleta foi projetada para garantir que a garra abra antes de avançar, feche com força suficiente para agarrar, e mantenha a posição após levantar para não perder o objeto.

### Prevenção de Travamento

Para evitar que o braço trave ao levantar, o sistema utiliza controle de tempo ao invés de ângulo fixo, permitindo que o movimento pare automaticamente mesmo se encontrar resistência mecânica.

## Tecnologias Utilizadas

- **Pybricks MicroPython**: Framework para programação do LEGO EV3
- **LEGO EV3 Brick**: Controlador principal do robô
- **Motores EV3**: 4 motores para movimento e manipulação
- **ColorSensor**: Sensor de cor e luz para detecção de objetos e obstáculos
- **Python**: Linguagem de programação utilizada

## Estrutura do Código

O código está organizado em funções modulares:

- **Funções de movimento**: Controle das rodas e navegação
- **Funções da garra**: Abertura, fechamento, elevação e descida
- **Funções de detecção**: Identificação de paredes e objetos vermelhos
- **Função principal**: Orquestra todo o processo de busca e coleta

link youtube : https://youtube.com/shorts/JkM2XvW8A1U?si=t5i5qg1zTQmski5k
