# Serverless GenAI: Criando Agentes com Cloud Run e Gemini

Este projeto serve como uma demonstração prática para a palestra "Serverless GenAI: Criando Agentes com Cloud Run e Gemini". Ele apresenta a construção de um agente de IA utilizando o Google Agent Developer Kit (ADK) e o modelo Gemini, empacotado em um contêiner Docker e implantado de forma serverless no Google Cloud Run.

O agente desenvolvido aqui, chamado `creator_agent`, é um agente multi-agente que orquestra outros sub-agentes para interagir com a API do YouTube e o modelo Gemini, com o objetivo de gerar roteiros para vídeos curtos baseados no conteúdo de um canal do YouTube.


## Demo Implantada
A demonstração deste projeto está implantada no Google Cloud Run e pode ser acessada na interface de desenvolvimento do ADK através do seguinte link:

https://gc-agente-service-773267354023.us-central1.run.app/dev-ui?app=creator_agent

Explore a interface para interagir com o creator_agent e ver os sub-agentes em ação!

## Variavéis de Ambiente
Arquivo de exemplo para as variáveis de ambiente necessárias. Copie para .env e preencha com suas credenciais e IDs.

```
GOOGLE_API_KEY=SUA_CHAVE_API_GOOGLE
YOUTUBE_API_KEY=SUA_CHAVE_API_YOUTUBE
YOUTUBE_PLAYLIST_UPLOAD_ID=ID_DA_PLAYLIST_DO_CANAL
GOOGLE_CLOUD_PROJECT=SEU_PROJETO_GCP
GOOGLE_CLOUD_LOCATION=SUA_LOCALIZACAO_GCP
```

## Estrutura do Projeto

A estrutura de pastas do projeto é a seguinte:

```
├── creator_agent/
│   ├── pycache/
│   ├── init.py
│   ├── .env.example
│   └── agent.py
├── .gitignore
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt

```

`creator_agent/`: Contém a lógica específica do agente.

`agent.py`: Define os sub-agentes e o agente principal (`creator_agent`) usando o ADK. Inclui as funções de ferramenta (Tools) para interagir com o YouTube e o modelo Gemini.

`.env` e `.env.example`: Arquivos para gerenciar variáveis de ambiente sensíveis (chaves de API, IDs).

`venv/`: Ambiente virtual Python.

`.gitignore`: Define arquivos e pastas a serem ignorados pelo Git.

`Dockerfile`: Instruções para construir a imagem do contêiner Docker da aplicação.

`main.py`: Ponto de entrada da aplicação, configura a API FastAPI e integra o agente ADK. Responsável por iniciar o servidor web.

`README.md`: Este arquivo.

`requirements.txt`: Lista as dependências Python do projeto.

## Tecnologias Utilizadas

* **Python 3.13**: Linguagem de programação principal.
* **Google Agent Developer Kit (ADK)**: Framework para construir agentes baseados em LLMs.
* **Google Gemini (gemini-2.0-flash-001, gemini-2.5-flash-preview-04-17)**: Modelos de linguagem grandes utilizados pelo agente.
* **FastAPI**: Framework web para criar a interface HTTP da aplicação.
* **Docker**: Para empacotar a aplicação em um contêiner.
* **Google Cloud Run**: Plataforma serverless para executar contêineres escaláveis.
* **Google Cloud SDK (gcloud CLI)**: Ferramenta de linha de comando para interagir com o Google Cloud.
* **YouTube Data API**: Para buscar informações sobre vídeos em um canal do YouTube.


### `main.py`

Configura e inicia o servidor FastAPI integrando o agente ADK.

```python
import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

SESSION_DB_URL = "sqlite:///./sessions.db"
ALLOWED_ORIGINS = ["*"]
SERVE_WEB_INTERFACE = True


app: FastAPI = get_fast_api_app(
    agent_dir=os.path.join(AGENT_DIR, 'creator_agent'),
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

```

Explicação de main.py:

from google.adk.cli.fast_api import get_fast_api_app: Importa a função utilitária do ADK para configurar uma aplicação FastAPI que serve o agente.

AGENT_DIR = os.path.dirname(os.path.abspath(__file__)): Define o diretório base onde o arquivo main.py está localizado.

SESSION_DB_URL = "sqlite:///./sessions.db": Configura a URL para um banco de dados SQLite local (sessions.db) que será usado pelo ADK para gerenciar o estado da sessão.

ALLOWED_ORIGINS = ["*"]: Define quais origens (domínios) são permitidas a acessar a API. "*" permite qualquer origem (útil para desenvolvimento/demonstração, mas restrinja em produção).

SERVE_WEB_INTERFACE = True: Uma variável booleana para controlar se a interface web de desenvolvimento do ADK deve ser servida. Quando True, o ADK fornece automaticamente uma UI interativa em /dev-ui para testar e depurar o agente. Quando implantado no Cloud Run, definir isso como True torna a UI pública.

app: FastAPI = get_fast_api_app(...): Inicializa a aplicação FastAPI, passando o diretório do agente, a URL do banco de dados de sessão, as origens permitidas e a configuração da interface web. O ADK configura automaticamente os endpoints da API para interagir com o agente.

if __name__ == "__main__":: Bloco padrão Python que executa o código dentro dele apenas quando o script é executado diretamente.

port = int(os.environ.get("PORT", 8080)): Configura a porta na qual o servidor web irá escutar. Ele tenta obter o número da porta da variável de ambiente PORT. Se PORT não estiver definida (como geralmente acontece em ambientes locais), ele assume a porta 8080 por padrão. No Google Cloud Run, a variável de ambiente PORT é definida automaticamente pela plataforma para indicar a porta na qual seu contêiner deve escutar.

uvicorn.run(app, host="0.0.0.0", port=port): Inicia o servidor Uvicorn (um servidor ASGI rápido) para servir a aplicação FastAPI (app). host="0.0.0.0" faz com que o servidor escute em todos os endereços IP disponíveis, tornando-o acessível externamente (necessário para o Cloud Run). A porta utilizada é a definida na linha anterior.

## Como Rodar Localmente
Para executar este projeto na sua máquina local, siga os passos abaixo:

Configure as Variáveis de Ambiente:

Copie o arquivo .env.example para .env:
```
cp creator_agent/.env.example creator_agent/.env
```

Edite o arquivo creator_agent/.env e preencha com suas chaves de API do Google e YouTube, e o ID da playlist de uploads do canal.
Crie e Ative um Ambiente Virtual:

Crie um ambiente virtual (recomendado para isolar as dependências):

```
python3 -m venv venv
```

* Ative o ambiente virtual: 

* No Linux/macOS

```
source venv/bin/activate
```

* No Windows:


````
venv\Scripts\activate
````


Instale as Dependências:

Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:


```
pip install -r requirements.txt
```
Inicie a Aplicação Localmente (com UI do ADK):

Inicie a aplicação usando o comando adk web, que fornece uma interface web para interagir com o agente:


```
adk web
```
A UI do ADK estará disponível em http://localhost:8080/dev-ui?app=creator_agent


## Deploy no Cloud Run

### Preparação para Nuvem (Containerização):

Criação do Dockerfile para definir o ambiente de execução da aplicação dentro de um contêiner Docker.
Definição das dependências no arquivo requirements.txt.

```
FROM python:3.13-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

COPY . .

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH"
EXPOSE 8080
CMD ["python", "main.py"]
```

Explicação do Dockerfile:

O Dockerfile contém as instruções para montar o ambiente da sua aplicação dentro de um contêiner Docker, tornando-a portátil e consistente.


FROM python:3.13-slim: Define a imagem base para o seu contêiner. Usamos a imagem oficial do Python na versão 3.13, na variante slim, que é menor e mais adequada para implantação.

WORKDIR /app: Define o diretório de trabalho dentro do contêiner como /app. Todos os comandos subsequentes serão executados a partir deste diretório.

COPY requirements.txt .: Copia o arquivo requirements.txt do diretório local para o diretório de trabalho (/app) dentro do contêiner. Copiar apenas este arquivo antes de instalar as dependências permite que o Docker utilize o cache se o arquivo não mudar.

RUN pip install --no-cache-dir -r requirements.txt: Executa o comando para instalar as dependências Python listadas no requirements.txt. O --no-cache-dir evita o armazenamento em cache dos pacotes instalados, reduzindo o tamanho da imagem final.

RUN adduser --disabled-password --gecos "" appuser && \ chown -R appuser:appuser /app: Cria um usuário não-root chamado appuser dentro do contêiner e define a propriedade do diretório /app para este usuário.
Rodar a aplicação com um usuário não-root é uma boa prática de segurança.

COPY . .: Copia todo o conteúdo do diretório local atual (excluindo o que está no .gitignore) para o diretório de trabalho (/app) dentro do contêiner. Isso inclui todos os arquivos do projeto, como main.py e a pasta creator_agent.

USER appuser: Define que os comandos subsequentes e o comando de execução padrão (CMD) serão executados como o usuário appuser.

ENV PATH="/home/appuser/.local/bin:$PATH": Adiciona o diretório de binários locais do usuário (/home/appuser/.local/bin) à variável de ambiente PATH. Isso garante que scripts instalados pelo pip para o usuário appuser possam ser encontrados e executados.

EXPOSE 8080: Informa que o contêiner irá "escutar" na porta 8080 em tempo de execução. Isso não publica a porta automaticamente, mas serve como documentação e pode ser usado por ferramentas de orquestração (como o Cloud Run) para configurar o mapeamento de portas.

CMD ["python", "main.py"]: Define o comando padrão a ser executado quando o contêiner for iniciado. Neste caso, ele executa o arquivo main.py usando o interpretador Python.


### Deploy no Google Cloud Run:

Utilização da ferramenta de linha de comando gcloud CLI para autenticação e configuração do projeto e localização no Google Cloud (gcloud init)

```
gcloud init
```

Exporte as Variáveis de Ambiente no Terminal:

Antes de executar o comando de deploy, defina as variáveis de ambiente necessárias na sua sessão do terminal. Certifique-se de substituí-las pelos seus valores reais.

```
export GOOGLE_CLOUD_PROJECT=SEU_PROJETO_GCP
export GOOGLE_CLOUD_LOCATION=SUA_LOCALIZACAO_GCP
export GOOGLE_API_KEY=SUA_CHAVE_API_GOOGLE
export YOUTUBE_API_KEY=SUA_CHAVE_API_YOUTUBE
export YOUTUBE_PLAYLIST_UPLOAD_ID=ID_DA_PLAYLIST_DO_CANAL
```

Execução do comando de deploy:


```
gcloud run deploy nome-do-seu-servico \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_API_KEY=$GOOGLE_API_KEY,YOUTUBE_API_KEY=$YOUTUBE_API_KEY,YOUTUBE_PLAYLIST_UPLOAD_ID=$YOUTUBE_PLAYLIST_UPLOAD_ID" \
    --timeout=3600
```

Explicação do comando:
gcloud run deploy nome-do-seu-servico: Inicia o processo de deploy para um serviço no Cloud Run chamado nome-do-seu-servico. Se o serviço não existir, ele será criado.

--source .: Indica que a fonte do código está no diretório atual. O Cloud Build será acionado automaticamente para construir a imagem do contêiner a partir do Dockerfile.

--region $GOOGLE_CLOUD_LOCATION: Especifica a região do Google Cloud onde o serviço será implantado. A variável $GOOGLE_CLOUD_LOCATION deve estar configurada no seu ambiente ou substituída pela região desejada (ex: us-central1).

--project $GOOGLE_CLOUD_PROJECT: Especifica o ID do projeto Google Cloud. A variável $GOOGLE_CLOUD_PROJECT deve estar configurada no seu ambiente.

--allow-unauthenticated: Permite que o serviço seja acessado sem autenticação. Use com cautela; para aplicações de produção, configure autenticação adequada.

--set-env-vars="...": Define as variáveis de ambiente que serão injetadas no contêiner em execução. É crucial passar as chaves de API e IDs aqui.

--timeout=3600: Define o tempo máximo de processamento para uma requisição em segundos (3600 segundos = 1 hora). Ajuste conforme a necessidade das suas operações.

## Recursos Adicionais
Para mais informações sobre o Google Agent Developer Kit, consulte a documentação oficial e os exemplos:

Documentação Oficial do ADK: https://google.github.io/adk-docs
Exemplos do ADK: https://github.com/google/adk-samples
