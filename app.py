# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_file, make_response
import yt_dlp
import os
import sys
import io
import logging
import tempfile
import shutil
import urllib.parse
import re

# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define o diretório base
DIRETORIO_BASE_APP = os.path.abspath(os.path.dirname(__file__))

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo para evitar problemas com caracteres especiais."""
    # Remove caracteres problemáticos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove espaços extras e limita o tamanho
    filename = re.sub(r'\s+', ' ', filename).strip()
    # Limita o tamanho do nome
    if len(filename) > 200:
        filename = filename[:200]
    return filename

@app.route('/')
def index():
    """Serve o arquivo HTML principal."""
    try:
        index_html_path = os.path.join(DIRETORIO_BASE_APP, 'index.html')
        with open(index_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    except FileNotFoundError:
        logging.error(f"Erro: index.html não encontrado em: {DIRETORIO_BASE_APP}")
        return "Erro: Frontend não encontrado.", 500
    except Exception as e:
        logging.error(f"Erro ao ler index.html: {e}")
        return f"Erro interno ao carregar a página: {e}", 500

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    """Endpoint para baixar o MP3 de uma URL do YouTube e enviá-lo de volta ao usuário."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados JSON não fornecidos."}), 400
    
    url_video = data.get('url')
    if not url_video:
        return jsonify({"error": "URL do vídeo não fornecida."}), 400

    logging.info(f"Requisição de download para: {url_video}")

    temp_dir = None
    downloaded_file_path = None
    
    try:
        temp_dir = tempfile.mkdtemp()
        logging.info(f"Diretório temporário criado: {temp_dir}")
        
        # Configuração do yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'extract_flat': 'discard_webpage',
            'noplaylist': True,
            'quiet': True,  # Mudamos para True para reduzir logs
            'no_warnings': True,
        }

        # Logger personalizado para capturar informações
        class CustomLogger:
            def __init__(self):
                self.messages = []
            
            def debug(self, msg):
                self.messages.append(('DEBUG', msg))
                logging.debug(f"[YTDLP-DEBUG] {msg}")
            
            def warning(self, msg):
                self.messages.append(('WARNING', msg))
                logging.warning(f"[YTDLP-WARNING] {msg}")
            
            def error(self, msg):
                self.messages.append(('ERROR', msg))
                logging.error(f"[YTDLP-ERROR] {msg}")

        custom_logger = CustomLogger()
        ydl_opts['logger'] = custom_logger

        # Executa o download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info("Iniciando processo de download com yt-dlp...")
            info_dict = ydl.extract_info(url_video, download=True)
            titulo_video = info_dict.get('title', 'audio_youtube')
            logging.info(f"yt-dlp concluído. Título: '{titulo_video}'")

            # Procura pelo arquivo MP3 gerado
            mp3_files = []
            for file in os.listdir(temp_dir):
                if file.lower().endswith('.mp3'):
                    mp3_files.append(file)
            
            if not mp3_files:
                logging.error(f"Nenhum arquivo MP3 encontrado em {temp_dir}")
                # Lista todos os arquivos para debug
                all_files = os.listdir(temp_dir)
                logging.error(f"Arquivos encontrados: {all_files}")
                return jsonify({"error": "Erro interno: Arquivo MP3 não foi gerado."}), 500
            
            # Pega o arquivo mais recente se houver múltiplos
            mp3_files.sort(key=lambda f: os.path.getmtime(os.path.join(temp_dir, f)), reverse=True)
            downloaded_file_path = os.path.join(temp_dir, mp3_files[0])
            
            logging.info(f"Arquivo MP3 encontrado: {os.path.basename(downloaded_file_path)}")
            
            # Verifica se o arquivo existe e tem conteúdo
            if not os.path.exists(downloaded_file_path):
                logging.error(f"Arquivo MP3 não encontrado: {downloaded_file_path}")
                return jsonify({"error": "Erro interno: Arquivo MP3 não encontrado."}), 500
            
            file_size = os.path.getsize(downloaded_file_path)
            if file_size == 0:
                logging.error(f"Arquivo MP3 está vazio: {downloaded_file_path}")
                return jsonify({"error": "Erro interno: Arquivo MP3 está vazio."}), 500
            
            logging.info(f"Arquivo MP3 válido - Tamanho: {file_size} bytes")
            
            # Sanitiza o nome do arquivo
            safe_filename = sanitize_filename(titulo_video)
            if not safe_filename.endswith('.mp3'):
                safe_filename += '.mp3'
            
            # Codifica o nome para o cabeçalho
            encoded_filename = urllib.parse.quote(safe_filename)
            
            logging.info(f"Enviando arquivo: {safe_filename}")
            
            # Cria a resposta com o arquivo
            response = make_response(send_file(
                downloaded_file_path,
                as_attachment=True,
                download_name=safe_filename,
                mimetype='audio/mpeg'
            ))
            
            # Define cabeçalhos explicitamente
            response.headers['Content-Type'] = 'audio/mpeg'
            response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Content-Length'] = str(file_size)
            
            logging.info(f"Arquivo '{safe_filename}' enviado com sucesso (Status: 200)")
            return response

    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        logging.error(f"Erro do yt-dlp: {error_message}")
        
        if "This video is unavailable" in error_message:
            return jsonify({"error": "Vídeo indisponível ou URL incorreta."}), 400
        elif "Private video" in error_message:
            return jsonify({"error": "Este vídeo é privado e não pode ser baixado."}), 403
        elif "age confirmation" in error_message:
            return jsonify({"error": "Este vídeo requer confirmação de idade."}), 403
        else:
            return jsonify({"error": f"Erro ao processar vídeo: {error_message}"}), 500
    
    except Exception as e:
        logging.error(f"Erro inesperado: {e}", exc_info=True)
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500
    
    finally:
        # Limpa o diretório temporário
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logging.info(f"Diretório temporário {temp_dir} removido")
            except Exception as e:
                logging.error(f"Erro ao remover diretório temporário: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check."""
    return jsonify({"status": "ok", "message": "Servidor funcionando"}), 200

if __name__ == '__main__':
    logging.info("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5001, debug=False)