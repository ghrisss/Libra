# Libra

Repositório para o projeto de visão relacionado ao balanceamento de rotores.

O projeto envolve a integração de cameras OAK-D junto da utilização da biblioteca OpenCV.

## Status do Projeto

Finalizando o desenvolvimento, otimizando o método de detecção de marcação de rebite, alteração de parâmetros para melhorar os resultados. Início de instalação em fábrica de MVP.

## Instalação recomendada

Versão python recomendada: **3.11.x**

* Criar um ambiente virtual com o comando: 
    
        python -m venv {nome_ambiente_virtual}

* Ativar o ambiente virtual:

        {nome_ambiente_virtual}\Scripts\activate

* Baixar as bibliotecas dentro do ambiente virtual: 
        
        pip install -r requirements.txt


Isso instalará todas as bibliotecas necessárias para o funcionamento correto onde for utilizado

A versão 3.12 atualmente (15/12/23) **NÃO** pode ser utilizada pois a atualização retirou várias classes de setup depreciada/não atualizadas como _ImpImporter_ e _distutils_ que são utilizadas para a construição da ''_wheel_'' de algumas bibliotecas utilizadas.

## Funcionalidades 

### Modo de Preparação:
Para realizar o setup do equipamento. Apresenta os modos de:
* Video: para ver a imagem capturada em tempo real. Utilizada para verificar o posicionamento da câmera. Também é possível realizar captura de imagens com a tecla _'C'_
* Configuração: Alterar parâmetros da câmera com o auxilio do teclado. Possível alteração de parâmetros como tempo de exposição, foco, brilho, nitidez, entre outros. Os comandos são mostrados no terminal de comando e para rever os comandos basta apertar a tecla _'H'_
* Captura: Realiza a captura da quantidade de frames escolhida pelo usuário. O tempo para a captura da imagem podem ser configurada no arquivo _configs.py_ e no caso de um tempo maior que 5 segundo ser escolhido, um vídeo é mostrado, para a preparação do frame.

Para rodar esse modo basta escrever a seguinte linha de código no terminal

    python libra.py

### Modo de Operação:
Realizada a captura de imagens junto do processamento de imagens para identificação de anel de curto e análise dos pontos de rebite. é possível chamar o modo com o seguinte comando:

    python libra.py -v True

Ao qual adiciona o argumento _vision_ e aciona o modo de operação

## Tecnologias Utilizadas
* OpenCV 
* Numpy
* DepthAI
* PyAV

#### Desenvolvido por:
Henrique Batista Fragoso (github: ghrisss)