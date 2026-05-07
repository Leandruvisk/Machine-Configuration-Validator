# Machine Configuration Validator

Validação de configurações de máquinas industriais.

## Descrição

Este projeto valida configurações de máquinas industriais, verificando CPU, memória, disco, rede e serviços do sistema.

## Estrutura do Projeto

```
machine-configuration-validator/
├── app/
│   ├── main.py                    # Ponto de entrada da aplicação
│   ├── validators/               # Validadores específicos
│   │   ├── cpu_validator.py
│   │   ├── memory_validator.py
│   │   ├── disk_validator.py
│   │   ├── network_validator.py
│   │   └── services_validator.py
│   ├── utils/                    # Utilitários
│   │   ├── logger.py
│   │   └── config_loader.py
│   ├── __init__.py
│   ├── validators/__init__.py
│   └── utils/__init__.py
├── configs/
│   └── expected_config.yaml      # Configuração esperada
├── reports/                      # Relatórios de validação
├── pyproject.toml               # Configuração do Poetry
├── poetry.lock                  # Lock file do Poetry
├── Dockerfile                    # Docker image
├── docker-compose.yml           # Orquestração Docker
├── .env                         # Variáveis de ambiente
├── README.md
├── run_poetry.bat
├── run_poetry.sh
└── .gitignore
```

## Pré-requisitos

- Docker e Docker Compose
- Poetry (para desenvolvimento local)
- Python 3.11+

## Instalação do Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
```

## Instalação e Execução

### Com Docker (Recomendado)

```bash
docker-compose up --build
```

Isso inicia o serviço `validator` e o banco PostgreSQL em `db`.

### Com Poetry

```bash
poetry install
poetry run python app/main.py
```

### Migrações com Aerich

```bash
poetry run aerich init
poetry run aerich init-db
poetry run aerich migrate
poetry run aerich upgrade
```

### Scripts úteis

```bash
./run_poetry.sh    # Linux/Mac
run_poetry.bat     # Windows
./run_migrations.sh # Linux/Mac
run_migrations.bat  # Windows
```

## Configuração

### Configuração do PostgreSQL

O banco PostgreSQL é configurado com as seguintes variáveis de ambiente:

- `DATABASE_URL=postgres://validator:validator@db:5432/validator`
- `DB_HOST=db`
- `DB_PORT=5432`
- `DB_NAME=validator`
- `DB_USER=validator`
- `DB_PASSWORD=validator`

Edite `configs/expected_config.yaml` para definir os requisitos mínimos do sistema:

```yaml
cpu:
  min_cores: 4
  min_frequency_ghz: 2.5

memory:
  min_gb: 8

disk:
  min_free_gb: 50

network:
  interfaces:
    - name: eth0
      required: true
      min_speed_mbps: 1000

services:
  required:
    - sshd
    - systemd
```

## Compatibilidade Linux

Sim, o projeto é compatível com Linux. A imagem Docker é baseada em Linux e o comando `./run_poetry.sh` funciona em ambientes Linux. Se você executar localmente no Linux, use `poetry install` e `poetry run python app/main.py`.

## Observações de plataforma

- O validador de rede depende de interfaces como `eth0` e `psutil`.
- O validador de serviços usa `systemctl`, `service` e `pgrep`, que são típicos de Linux.

## Gerenciamento de dependências

```bash
poetry add package-name
poetry add --group dev package-name
poetry update
poetry show
```

## Relatórios

Os relatórios são gerados em `reports/validation_report.txt`.
