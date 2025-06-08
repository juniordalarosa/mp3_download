# Use uma imagem base oficial do Python como base.
# 'slim-buster' é uma versão mais leve do Debian, ideal para imagens Docker menores.
FROM python:3.11-slim-buster

# Defina o diretório de trabalho dentro do contêiner.
# Todos os comandos subsequentes serão executados a partir deste diretório.
WORKDIR /app

# Instale as dependências do sistema operacional necessárias:
#   - apt-get update: Atualiza a lista de pacotes.
#   - ffmpeg: ESSENCIAL para o yt-dlp extrair e converter áudio para MP3.
#   - python3-pip: Garante que o pip esteja disponível para instalar pacotes Python.
#   - --no-install-recommends: Evita a instalação de pacotes recomendados desnecessários,
#     mantendo o tamanho da imagem menor.
#   - rm -rf /var/lib/apt/lists/*: Limpa o cache do apt para reduzir o tamanho final da imagem.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copie o arquivo de dependências Python (requirements.txt) para o contêiner.
# Fazer isso cedo aproveita o cache de build do Docker: se requirements.txt não mudar,
# esta e as próximas camadas (pip install) não serão reconstruídas.
COPY requirements.txt .

# Instale os pacotes Python listados em requirements.txt.
# --no-cache-dir: Impede que o pip armazene dados em cache, reduzindo o tamanho da imagem.
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código-fonte da sua aplicação para o diretório de trabalho no contêiner.
# Isso inclui app.py e index.html.
COPY . .

# Exponha a porta na qual sua aplicação Flask vai escutar.
# Isso informa ao Docker que o contêiner ouvirá na porta 5001.
EXPOSE 5001

# Defina variáveis de ambiente para a aplicação Flask.
# FLASK_APP: Especifica o ponto de entrada da aplicação Flask.
# FLASK_RUN_HOST: Torna a aplicação Flask acessível de fora do contêiner (0.0.0.0 significa todas as interfaces).
# FLASK_RUN_PORT: Define a porta na qual o Flask vai escutar dentro do contêiner.
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Comando para executar a aplicação Flask quando o contêiner iniciar.
# Usamos 'flask run' para simplicidade. Para produção, é recomendado usar um servidor WSGI
# mais robusto como Gunicorn (ex: CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app"]).
CMD ["flask", "run"]
