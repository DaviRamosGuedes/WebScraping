import scrapy

class VagasSpider(scrapy.Spider):
    name = 'vagas'
    allowed_domains = ['vagas.com.br']
    start_urls = ['https://www.vagas.com.br/vagas-de-vitoria-es']  # Substitua pela URL real

    def parse(self, response):
        # Encontra todas as vagas
        vagas = response.css('li.vaga')

        # Itera sobre cada vaga encontrada
        for vaga in vagas:
             # Extraí o título da vaga
            titulo = vaga.css('a.link-detalhes-vaga::text').get().strip()  # Obtém o texto do link
            titulo += vaga.css('a.link-detalhes-vaga mark::text').get(default='').strip()  # Adiciona o texto dentro da tag <mark>

            # Extraí a empresa
            empresa = vaga.css('span.emprVaga::text').get().strip()

            # Extraí a localização
            localizacao_mark = vaga.css('span.vaga-local mark::text').get(default='').strip()  # Texto dentro da tag <mark>
            localizacao_rest = vaga.css('span.vaga-local::text').get().strip()  # Texto fora da tag <mark>
            localizacao = f"{localizacao_mark} {localizacao_rest}".replace('  ', ' ').strip()  # Combina os textos e remove espaços extras
            
            # Extraí a data de publicação
            data_publicacao = vaga.css('span.data-publicacao::text').get().strip()

            # Exibe as informações
            yield {
                'Título': titulo,
                'Empresa': empresa,
                'Localização': localizacao,
                'Data de Publicação': data_publicacao
            }

        # Se houver uma próxima página, siga o link
        proxima_pagina = response.css('a.proxima::attr(href)').get()
        if proxima_pagina:
            yield response.follow(proxima_pagina, self.parse)
