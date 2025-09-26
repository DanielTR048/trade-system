# Dockerfile CORRETO E FINAL

# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Instala dependências essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev
# Defina o diretório de trabalho no container
WORKDIR /app

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copie o arquivo de dependências e instale-as
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação para o diretório de trabalho
COPY ./app /app/app