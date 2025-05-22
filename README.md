# Google Maps Scraper com Playwright + SQLite

Este projeto utiliza **Python** e **Playwright** para realizar a extração de dados do Google Maps com base em uma lista de pesquisas (ex: `Salão de beleza - São Paulo`, etc.). Os resultados são armazenados em um banco de dados SQLite (`negocios.db`), com informações como nome, endereço, telefone, localização geográfica, e dados de avaliação.

---

## 📦 Requisitos

- Python 3.8 ou superior
- Pip

### 📁 Instalar dependências (Terminal):

```bash
pip install -r requirements.txt

playwright install

🛠️ Estrutura
input.txt: arquivo com as pesquisas (ex: Salão de beleza - São Paulo)
main.py: script principal para scraping e salvamento no SQLite
negocios.db: banco de dados gerado contendo os dados extraídos

▶️ Como usar
Adicione as pesquisas no arquivo input.txt no formato:

Salão de beleza - São Paulo - SP
Salão de beleza - Guarulhos - SP
Salão de beleza - Campinas - SP
Execute o script:

python main.py
O navegador abrirá e fará as buscas automaticamente.

💾 Banco de dados
Os dados são armazenados na tabela negocios com os seguintes campos:

id (inteiro, auto-incremento)

name
address
website
phone_number
reviews_count
reviews_average
latitude
longitude
cidade
pesquisa

O campo cidade é extraído do texto após o hífen na pesquisa (ex: São Paulo), e o campo pesquisa é o texto antes do hífen (ex: Salão de beleza).

♻️ Modo incremental
A cada nova execução do script, os dados são adicionados à tabela existente (append) sem apagar os anteriores.

🧹 Para reiniciar do zero
Se quiser limpar os dados antigos:

rm negocios.db
⚠️ Aviso
Use com responsabilidade. O scraping do Google Maps pode violar os termos de serviço da plataforma.

Este projeto é apenas para fins educacionais.

---

Se quiser, posso gerar o `requirements.txt` e até mesmo o comando para empacotar tudo com um `setup.py` ou `