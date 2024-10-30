import requests
from bs4 import BeautifulSoup

# URL da página que contém as vagas
url = 'https://www.vagas.com.br/vagas-de-vitoria-es'  # Substitua pela URL real

# Faz a requisição da página
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Cria o objeto BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra todas as vagas
    vagas = soup.find_all('li', class_='vaga')

    # Itera sobre cada vaga encontrada
    for vaga in vagas:
        # Extraí o título da vaga
        titulo = vaga.find('h2', class_='cargo').text.strip()
        
        # Extraí a empresa
        empresa = vaga.find('span', class_='emprVaga').text.strip()
        
        # Extraí a localização
        localizacao = vaga.find('span', class_='vaga-local').text.strip().replace(" \n", "")
        
        # Extraí a data de publicação
        data_publicacao = vaga.find('span', class_='data-publicacao').text.strip()

        # Exibe as informações
        print(f'Título: {titulo}')
        print(f'Empresa: {empresa}')
        print(f'Localização: {localizacao}')
        print(f'Data de Publicação: {data_publicacao}')
        print('---')
else:
    print(f'Erro ao acessar a página: {response.status_code}')
