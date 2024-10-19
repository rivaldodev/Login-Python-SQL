
# Projeto: Sistema de Login com Gerador de Dados Pessoais Fictícios

## Tecnologias: Python, Flask, SQLite, API (4devs)
##  Template Frontend: DarkPan (https://themewagon.com/themes/free-bootstrap-5-admin-dashboard-template-darkpan/) - Créditos: HTML Codex

# Resumo:

Este projeto é uma aplicação web simples desenvolvida em Python utilizando o framework Flask. Ele oferece um sistema de login com registro de usuários, armazenamento de créditos e uma página de administração. Uma de suas funcionalidades principais é a integração com a API da 4devs para gerar dados pessoais fictícios.

# Funcionalidades:

<u>**1. Sistema de Login:**</u>

Autenticação de usuários com senha segura (usando Argon2 para hash de senhas)
Registro de novos usuários com armazenamento de credenciais em um banco de dados SQLite

<u>**2. Sistema de Créditos:**</u>

Cada usuário tem um saldo de créditos
Possibilidade de debitar créditos ao utilizar a ferramenta de geração de dados pessoais

<u>**3. Página de Administração (acesso restrito):**</u>

Disponível apenas para o usuário 'rivs'
Gerenciamento de usuários (visualizar, adicionar, remover)
Atualização do saldo de créditos dos usuários

<u>**4. Integração com API da 4devs:**</u>

Requisição para gerar dados pessoais fictícios (nome, CPF, endereço, etc.)
Exibição dos dados gerados na página do usuário

  

# Estrutura do Projeto:

  

 - app.py: Arquivo principal da aplicação, contendo as rotas e lógica do
   Flask
 - templates/: Pasta contendo os templates HTML para as páginas da   
   aplicação
	 - login.html, register.html, gerador.html, admin.html
 - static/: Pasta para arquivos estáticos (CSS, JavaScript, imagens)
 - usuarios.db: Banco de dados SQLite para armazenamento de usuários e  
   créditos

## Requisitos para Execução:

  

 - Python 3.x
 - Flask
 - SQLite
 - Bibliotecas necessárias listadas no requirements.txt

  

# Instalação e Execução:

  

1. Clone o repositório.
2. Instale as dependências necessárias com:
```bash
pip install flask argon2-cffi
```
3. Execute a aplicação com:
````bash
python app.py
````
3. Acesse a aplicação em http://localhost:5000 (ou a porta especificada).

# Créditos e Referências:
## Template Frontend: [DarkPan by HTML Codex](https://themewagon.com/themes/free-bootstrap-5-admin-dashboard-template-darkpan/)
## API de Dados Pessoais Fictícios: [4devs](https://www.4devs.com.br/gerador_de_pessoas)