Baixador de MP3 do YouTube
Esta é uma aplicação web simples e leve que permite baixar o áudio de vídeos do YouTube diretamente para o seu computador, convertendo-o para o formato MP3. A aplicação é conteinerizada com Docker, o que a torna fácil de implantar e usar em qualquer sistema que suporte Docker.

Funcionalidades
Download de áudio MP3 de URLs de vídeos do YouTube.

Interface web intuitiva.

Converte para MP3 com qualidade de 192kbps.

Download direto para o computador do usuário via navegador.

Como Usar (Com Docker)
A maneira mais fácil de usar esta aplicação é através da imagem Docker pré-construída disponível no Docker Hub.

Pré-requisitos

Certifique-se de ter o Docker Desktop (ou um ambiente Docker compatível) instalado e rodando em seu sistema (Windows, macOS, Linux).

1. Puxar a Imagem Docker

Abra seu terminal e puxe a imagem diretamente do Docker Hub. Substitua juniordalarosa pelo seu nome de usuário real do Docker Hub, caso você tenha taggeado a imagem com outro usuário.

docker pull juniordalarosa/youtube-mp3-downloader:latest

2. Rodar o Contêiner

Após o download da imagem, execute o contêiner Docker. A aplicação estará acessível na porta 5001 do seu computador.

docker run -d -p 5001:5001 --name youtube-downloader juniordalarosa/youtube-mp3-downloader:latest

-d: Roda o contêiner em segundo plano (detached mode).

-p 5001:5001: Mapeia a porta 5001 do seu computador (host) para a porta 5001 dentro do contêiner, onde a aplicação Flask está escutando.

--name youtube-downloader: Atribui um nome amigável ao contêiner para facilitar o gerenciamento.

3. Acessar a Aplicação

Abra seu navegador web e acesse a seguinte URL:

http://localhost:5001

Cole a URL de um vídeo do YouTube no campo fornecido e clique no botão "Baixar MP3". O arquivo de áudio MP3 será processado no servidor e o download iniciará diretamente no seu navegador, salvando na pasta de downloads padrão do seu computador.

4. Gerenciar o Contêiner (Comandos Úteis)

Verificar contêineres rodando:

docker ps

Verificar todos os contêineres (rodando e parados):

docker ps -a

Ver logs de um contêiner (útil para depuração):

docker logs youtube-downloader

Parar o contêiner:

docker stop youtube-downloader

Remover o contêiner (depois de parado):

docker rm youtube-downloader

Remover a imagem (opcional, se não for mais usar):

docker rmi juniordalarosa/youtube-mp3-downloader:latest

Desenvolvimento (Construir a Imagem Localmente)
Se você deseja modificar o código ou construir a imagem Docker a partir do código-fonte localmente, siga estes passos.

Pré-requisitos

Git instalado.

Docker Desktop instalado e rodando.

Python 3.x (para executar o código localmente, se desejar).

1. Clonar o Repositório

git clone https://github.com/juniordalarosa/mp3_download.git
cd mp3_download

2. Estrutura do Projeto

Dentro do diretório mp3_download, você encontrará:

mp3_download/
├── app.py          # Backend da aplicação (Flask, yt-dlp)
├── index.html      # Frontend da aplicação (HTML, CSS, JavaScript)
├── requirements.txt # Dependências Python do backend
└── Dockerfile      # Instruções para construir a imagem Docker

3. Construir a Imagem Docker

No diretório mp3_download (onde o Dockerfile está localizado), execute:

docker build -t youtube-mp3-downloader-image .

Este comando construirá uma imagem Docker localmente chamada youtube-mp3-downloader-image.

4. Rodar o Contêiner Localmente

Após construir a imagem, você pode rodar o contêiner:

docker run -d -p 5001:5001 --name youtube-downloader-dev youtube-mp3-downloader-image

A aplicação estará acessível em http://localhost:5001.

Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

Licença
Este projeto é de código aberto e está disponível sob a licença MIT License.
