from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

class SeleniumMiddleware:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executa em modo headless
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        
        # Inicia o WebDriver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def process_request(self, request, spider):
        # Usa o Selenium para carregar a página
        self.driver.get(request.url)
        time.sleep(2)  # Aguarda carregar o conteúdo, ajuste conforme necessário
        
        # Retorna o HTML carregado como uma resposta para o Scrapy
        return HtmlResponse(
            url=request.url,
            body=self.driver.page_source,
            encoding='utf-8',
            request=request
        )

    def __del__(self):
        # Finaliza o driver ao encerrar o middleware
        self.driver.quit()
