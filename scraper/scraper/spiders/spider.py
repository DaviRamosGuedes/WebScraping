import scrapy
import google.generativeai as palm

class VagasSpider(scrapy.Spider):
    name = 'vagas'
    allowed_domains = ['vagas.com.br']
    start_urls = [
        'https://www.vagas.com.br/vagas-de-vitoria-es'
    ]

    palavras_chave_ti = [
        'desenvolvedor', 'programador', 'engenheiro de software', 
        'analista de sistemas', 'ciência de dados', 'cybersegurança', 
        'segurança da informação', 'devops', 'backend', 'frontend',
        'full stack', 'engenharia de dados', 'suporte técnico', 'infraestrutura'
    ]

    def __init__(self, *args, **kwargs):
        super(VagasSpider, self).__init__(*args, **kwargs)
        
        # Configura a chave da API do Google Gemini
        palm.configure(api_key="AIzaSyBG-gtpsLmTHUjpIPMaaSuQU8oitUhxMe8")

    def parse(self, response):
        # Processa as vagas encontradas
        yield from self.parse_vagas(response)

        # Tratamento para navegação entre páginas
        proxima_pagina = response.css('a.proxima::attr(href)').get() or response.css('a[aria-label="Próxima"]::attr(href)').get()
        if proxima_pagina:
            yield response.follow(proxima_pagina, self.parse)

    def parse_vagas(self, response):
        vagas = response.css('li.vaga')
        for vaga in vagas:
            titulo = vaga.css('a.link-detalhes-vaga::text').get(default='').strip()
            empresa = vaga.css('span.emprVaga::text').get(default='').strip()
            localizacao_mark = vaga.css('span.vaga-local mark::text').get(default='').strip()
            localizacao_rest = vaga.css('span.vaga-local::text').get().strip()
            localizacao = f"{localizacao_mark} {localizacao_rest}".replace('  ', ' ').strip()
            data_publicacao = vaga.css('span.data-publicacao::text').get(default='').strip()
            url_vaga = vaga.css('a.link-detalhes-vaga::attr(href)').get()

            # Completa a URL da vaga
            if url_vaga and not url_vaga.startswith('http'):
                url_vaga = response.urljoin(url_vaga)
            
            # Faz um request para a página da vaga para coletar a descrição
            yield response.follow(url_vaga, self.parse_detalhes_vaga, meta={
                'Título': titulo,
                'Empresa': empresa,
                'Localização': localizacao,
                'Data de Publicação': data_publicacao
            })

    def parse_detalhes_vaga(self, response):
        titulo = response.meta['Título']
        empresa = response.meta['Empresa']
        localizacao = response.meta['Localização']
        data_publicacao = response.meta['Data de Publicação']

        # Extrai a descrição da vaga
        descricao = response.css('div.job-tab-content.job-description__text.texto').getall()
        descricao_texto = ' '.join(descricao).strip()
        
        # Debug: Imprimir descrição
        self.log(f'Descrição da vaga: {descricao_texto}')

        # Transformando a descrição para minúsculas para a comparação
        descricao_texto_lower = descricao_texto.lower()
        
        # Verifica se a descrição contém alguma palavra-chave de TI
        if any(palavra.lower() in descricao_texto_lower for palavra in self.palavras_chave_ti):
            yield {
                'Título': titulo,
                'Empresa': empresa,
                'Localização': localizacao,
                'Data de Publicação': data_publicacao,
                'Descrição': descricao_texto,
                'URL da Vaga': response.url
            }
        else:
            self.log(f'Vaga ignorada: {titulo}, pois não contém palavras-chave de TI.')
