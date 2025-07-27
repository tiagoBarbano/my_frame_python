<h3 align="center">My Frame Python</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/tiagoBarbano/my_frame_granian.svg)](https://github.com/tiagoBarbano/my_frame_granian/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/tiagoBarbano/my_frame_granian.svg)](https://github.com/tiagoBarbano/my_frame_granian/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---
## 🧐 About <a name = "about"></a>

Este projeto é uma aplicação Python modular, focada em alta performance e extensibilidade, utilizando o framework Granian para servir APIs REST. Ele foi desenhado para ser facilmente adaptado a diferentes cenários, com módulos separados para lógica de negócio, demonstrações e métricas.

A arquitetura do projeto é composta pelos seguintes módulos principais:

- **app/**: Contém a aplicação principal, incluindo as rotas, controladores e integrações com serviços externos.
- **metrics/**: Responsável pela coleta e exposição de métricas de uso e performance, podendo ser integrado a sistemas de monitoramento como Prometheus.
- **tests/**: Abriga os testes automatizados, incluindo testes unitários, de integração e end-to-end.

A aplicação pode ser executada localmente ou via Docker, e expõe endpoints REST para consumo de dados e operações de negócio. O módulo de métricas permite monitorar a saúde e o desempenho do sistema em tempo real.

Exemplo de fluxo básico:
1. O usuário faz uma requisição HTTP para um endpoint da API.
2. O módulo `app` processa a requisição e executa a lógica de negócio.
3. O módulo `metrics` registra informações relevantes sobre a requisição.

Esta estrutura modular facilita a manutenção, testes e evolução do sistema.


## 🗂️ Estrutura do diretório `app/`

A pasta `app/` é o núcleo da aplicação e está organizada em submódulos para separar responsabilidades e facilitar a manutenção. Veja a seguir um resumo dos principais diretórios e arquivos:

- **config.py**  
  Configurações globais da aplicação (variáveis de ambiente, parâmetros de conexão, etc).

- **core/**  
  Contém funcionalidades centrais e utilitários, como:
  - `application.py`: ponto de entrada da aplicação.
  - `exception.py`: tratamento centralizado de exceções.
  - `logger.py`: configuração e formatação de logs.
  - `metrics.py`: coleta e exposição de métricas.
  - `params.py`: definição de parâmetros para rotas e validação.
  - `routing.py`: sistema de roteamento e decorators para endpoints.
  - `swagger.py`: geração e exposição da documentação OpenAPI.
  - `tracing.py`: integração com OpenTelemetry para tracing.
  - `utils.py`: funções utilitárias diversas.

- **dto/**  
  Objetos de transferência de dados (Data Transfer Objects), usados para padronizar a entrada e saída de dados nas APIs.

- **infra/**  
  Camada de infraestrutura, responsável por integrações externas e recursos compartilhados:
  - `database.py`: gerenciamento de conexões com MongoDB.
  - `redis.py`: gerenciamento de conexões com Redis.
  - `lifespan.py`: controle do ciclo de vida da aplicação.
  - `proxy_handler.py`: integrações HTTP externas via aiohttp.

- **models/**  
  Definições dos modelos de dados utilizados pela aplicação.

- **repository/**  
  Implementação dos repositórios de acesso a dados, abstraindo operações com bancos ou outros serviços persistentes.

- **routers/**  
  Definição das rotas/endpoints da API, agrupadas por domínio ou funcionalidade.

- **services/**  
  Implementação das regras de negócio e serviços reutilizáveis.

Essa estrutura modular permite que cada parte da aplicação seja desenvolvida, testada e mantida de forma independente, promovendo clareza, organização e escalabilidade.



## 🚀 Como montar uma aplicação com este framework

A estrutura do framework foi pensada para facilitar a criação de APIs performáticas, organizadas e escaláveis. Veja um passo a passo para montar sua aplicação:

### 1. Estruture seus módulos dentro de `app/`

- **core/**: Coloque utilitários, configuração de logs, tratamento de exceções, roteamento, geração de documentação e tracing.
- **dto/**: Defina os Data Transfer Objects para padronizar entrada e saída de dados.
- **infra/**: Implemente integrações externas (ex: MongoDB, Redis, APIs HTTP externas).
- **models/**: Modele as entidades de domínio.
- **repository/**: Implemente o acesso a dados, abstraindo a persistência.
- **routers/**: Defina os endpoints da API, agrupando por domínio.
- **services/**: Centralize as regras de negócio e integrações reutilizáveis.
- **config.py**: Centralize configurações globais.

### 2. Crie seus modelos e DTOs

- Em `models/`, crie classes que representam suas entidades.
- Em `dto/`, crie schemas para validação e transporte de dados.

### 3. Implemente repositórios e serviços

- Em `repository/`, crie classes para abstrair operações de banco de dados.
- Em `services/`, implemente a lógica de negócio, utilizando os repositórios.

### 4. Defina suas rotas

- Em `routers/`, crie funções decoradas com os atalhos `@get` e `@post` do módulo de roteamento (`core/routing.py`).
- Especifique modelos de request/response, headers e parâmetros para documentação automática.

Exemplo:
```python
from app.core.routing import post
from app.dto.user_dto import UserRequestDto, UserResponseDto

@post(
    "/usuario",
    summary="Cria um novo usuário",
    request_model=UserRequestDto,
    response_model=UserResponseDto,
    tags=["Usuário"]
)
async def criar_usuario(scope, receive, send):
    # lógica para criar usuário
    ...
```

### 5. Configure integrações externas

- Use `infra/database.py` para MongoDB, `infra/redis.py` para Redis, e `infra/proxy_handler.py` para chamadas HTTP externas.

### 6. Inicialize e rode a aplicação

- Para rodar localmente:
  ```sh
  python main.py
  ```

## ▶️ Como usar o `main.py`

O arquivo `main.py` é o ponto de entrada da aplicação. Ele é responsável por inicializar e executar o servidor Granian, além de configurar middlewares como logging, métricas (Prometheus) e tracing (OpenTelemetry), conforme as opções definidas nas configurações.

### Execução local

O servidor será iniciado na porta 8000, utilizando todos os núcleos de CPU disponíveis (ou conforme definido em `Settings`). Os endpoints da API estarão acessíveis em `http://localhost:8000`.

### Principais funcionalidades do `main.py`:

- **Inicialização do servidor Granian**: Utiliza o ASGI app definido em `app.core.application`.
- **Configuração dinâmica de workers**: O número de workers é ajustado conforme a CPU ou configuração.
- **Middlewares opcionais**:
  - **LoggerMiddleware**: Habilita logs detalhados das requisições.
  - **PrometheusMiddleware**: Expõe métricas em `/metrics` se ativado.
  - **OpenTelemetryMiddleware**: Habilita tracing distribuído se ativado.
- **Configuração automática de variáveis de ambiente para métricas multiprocessadas**.

### Observações

- As configurações são controladas pelo arquivo `app/config.py` (classe `Settings`).
- Para ambientes de produção, recomenda-se utilizar Docker ou um gerenciador de processos.
- A documentação automática estará disponível em `/docs` após inicialização.

---
**Resumo:**  
Basta rodar `python main.py` para iniciar a aplicação com todos os recursos configurados conforme suas necessidades.  


### 7. Documentação automática

- Acesse `/docs` para a interface Swagger UI.
- O OpenAPI JSON está disponível em `/openapi.json`.

---

**Resumo:**  
Monte sua aplicação criando modelos, DTOs, repositórios, serviços e rotas conforme a estrutura sugerida. O framework já provê logging, métricas, tracing, cache, documentação automática e integrações externas prontos para uso.


## 🛠️ Tecnologias Utilizadas

O projeto utiliza um conjunto de tecnologias modernas para garantir alta performance, observabilidade e facilidade de integração:

- **Python 3.10+**  
  Linguagem principal da aplicação.

- **Granian**  
  Servidor ASGI de alta performance para aplicações Python assíncronas.

- **msgspec**  
  Serialização/deserialização e validação de dados eficiente, utilizada nos DTOs e modelos.

- **Pydantic Settings**  
  Gerenciamento de configurações e variáveis de ambiente de forma tipada.

- **orjson**  
  Serializador JSON ultrarrápido para Python.

- **MongoDB**  
  Banco de dados NoSQL, integrado via drivers assíncronos.

- **Redis**  
  Armazenamento em memória para cache e operações rápidas.

- **aiohttp**  
  Cliente HTTP assíncrono para integrações externas.

- **Prometheus Client**  
  Coleta e exposição de métricas para monitoramento.

- **OpenTelemetry**  
  Observabilidade e tracing distribuído, com instrumentação para ASGI, MongoDB, Redis, logging e aiohttp.

- **uvloop**  
  Loop de eventos alternativo para maior desempenho em aplicações assíncronas.

- **pytest & pytest-asyncio**  
  Frameworks para testes automatizados síncronos e assíncronos.

- **jsonschema**  
  Validação de dados baseada em JSON Schema.

Essas tecnologias proporcionam uma base robusta, performática e observável para o desenvolvimento de APIs modernas.
