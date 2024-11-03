import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class VagasSpider(scrapy.Spider):
    name = 'vagas'
    allowed_domains = ['vagas.com.br', 'trabalhaes.com.br']
    start_urls = [
        'https://www.vagas.com.br/vagas-de-vitoria-es',
        'https://www.trabalhaes.com.br/vagas-em-vitoria-es/'
    ]

    palavras_chave_ti = [
        'ciência da computação',
        'sistemas de informação',
        'engenharia de software',
        'desenvolvimento de software',
        'análise e desenvolvimento de sistemas',
        'tecnologia da informação',
        'gestão da tecnologia da informação',
        'segurança da informação',
        'redes de computadores',
        'inteligência artificial',
        'machine learning',
        'data science',
        'big data',
        'programação',
        'análise de dados',
        'administração de banco de dados',
        'web design',
        'desenvolvimento web',
        'mobile development',
        'cloud computing',
        'devops',
        'testes de software',
        'metodologias ágeis',
        'ciência de dados'
    ]


    def __init__(self, *args, **kwargs):
        super(VagasSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.set_window_size(1920, 1080)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(VagasSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        self.driver.quit()

    def parse(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            )

            sel_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

            # Parseando vagas dependendo do domínio
            if "vagas.com.br" in sel_response.url:
                yield from self.parse_vagas(sel_response)
            elif "trabalhaes.com.br" in sel_response.url:
                yield from self.parse_trabalhaes(sel_response)

            # Extraindo link da próxima página
            proxima_pagina = sel_response.css('a.proxima::attr(href)').get() or sel_response.css('a[aria-label="Próxima"]::attr(href)').get()
            if proxima_pagina:
                yield response.follow(proxima_pagina, self.parse)

        except Exception as e:
            self.log(f"Erro ao carregar a página: {e}")

    def parse_vagas(self, response):
        vagas = response.css('li.vaga')
        for vaga in vagas:
            titulo = vaga.css('a.link-detalhes-vaga::text').get(default='').strip()
            empresa = vaga.css('span.emprVaga::text').get(default='').strip()
            localizacao_mark = vaga.css('span.vaga-local mark::text').get(default='').strip()
            localizacao_rest = vaga.css('span.vaga-local::text').get(default='').strip()
            localizacao = f"{localizacao_mark} {localizacao_rest}".replace('  ', ' ').strip()
            data_publicacao = vaga.css('span.data-publicacao::text').get(default='').strip()
            url_vaga = vaga.css('a.link-detalhes-vaga::attr(href)').get()

            self.log(f'Título: {titulo}, Empresa: {empresa}, Localização: {localizacao}, Data de Publicação: {data_publicacao}, URL: {url_vaga}')

            if url_vaga:
                url_vaga = response.urljoin(url_vaga)
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

        # Extraindo a descrição da vaga
        descricao = response.css('div.job-description__text ::text').getall()  # Para Vagas.com
        descricao_texto = ' '.join(descricao).replace('\n', ' ').replace('\t', ' ').strip()  # Removendo quebras de linha e tabulações

        self.log(f'Descrição (Vagas.com): {descricao_texto}')

        if any(palavra.lower() in descricao_texto.lower() for palavra in self.palavras_chave_ti):
            yield {
                'Título': titulo,
                'Empresa': empresa,
                'Localização': localizacao,
                'Data de Publicação': data_publicacao,
                'Descrição': descricao_texto,
                'URL da Vaga': response.url
            }

    def parse_trabalhaes(self, response):
        # Extrair todas as vagas na página atual
        for vaga in response.css('div.list-item'):
            titulo = vaga.css('.list-item-title a::text').get()
            empresa = vaga.css('.list-item-company div[itemprop="name"]::text').get().strip() if vaga.css('.list-item-company div[itemprop="name"]::text').get() else None
            localizacao = vaga.css('.list-item-location span[itemprop="addressLocality"]::text').get() + ' - ' + \
                        vaga.css('.list-item-location span[itemprop="addressRegion"]::text').get()
            data_publicacao = vaga.css('time[itemprop="datePosted"]::attr(datetime)').get()
            url_vaga = vaga.css('.list-item-title a::attr(href)').get()

            self.log(f'Título: {titulo}, Empresa: {empresa}, Localização: {localizacao}, Data de Publicação: {data_publicacao}')

            if url_vaga:
                url_vaga = response.urljoin(url_vaga)
                yield response.follow(url_vaga, self.parse_detalhes_vaga_trabalhaes, meta={
                    'Título': titulo,
                    'Empresa': empresa,
                    'Localização': localizacao,
                    'Data de Publicação': data_publicacao
                })

        # Verificar se há um botão "Carregar mais vagas" e seguir o link se existir
        carregar_mais = response.css('a.btn.btn-round.btn-white.btn-transparent::attr(href)').get()
        if carregar_mais:
            next_page_url = response.urljoin(carregar_mais)
            self.log(f'Carregando mais vagas de: {next_page_url}')
            yield response.follow(next_page_url, self.parse_trabalhaes)


    def parse_detalhes_vaga_trabalhaes(self, response):
        titulo = response.meta['Título']
        empresa = response.meta['Empresa']
        localizacao = response.meta['Localização']
        data_publicacao = response.meta['Data de Publicação']

        descricao = response.css('div.sc-add46fb1-3.cOkxvQ p::text').getall()
        descricao_texto = ' '.join(descricao).replace('\n', ' ').replace('\t', ' ').strip()  # Removendo quebras de linha e tabulações

        self.log(f'Descrição (Trabalhaes): {descricao_texto}')

        if any(palavra.lower() in descricao_texto.lower() for palavra in self.palavras_chave_ti):
            yield {
                'Título': titulo,
                'Empresa': empresa,
                'Localização': localizacao,
                'Data de Publicação': data_publicacao,
                'Descrição': descricao_texto,
                'URL da Vaga': response.url
            }
