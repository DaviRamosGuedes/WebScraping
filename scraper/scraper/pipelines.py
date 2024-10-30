# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperPipeline:
    def process_item(self, item, spider):
        return item

# import openai

# class ChatGPTPipeline:
#     def open_spider(self, spider):
#         openai.api_key = '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'  # Insira sua chave da API aqui
#         self.jobs_data = []

#     def close_spider(self, spider):
#         # Após o scraping, envie os dados coletados ao ChatGPT
#         self.ask_chatgpt(self.jobs_data)

#     def process_item(self, item, spider):
#         # Armazena os itens (vagas) coletados
#         self.jobs_data.append(item)
#         return item

#     def ask_chatgpt(self, jobs_data):
#         # Cria um prompt com base nas vagas coletadas
#         prompt = "Eu coletei as seguintes vagas de emprego em Vitória, ES:\n"
        
#         for job in jobs_data:
#             prompt += f"- Vaga: {job['title']}, Empresa: {job['company']}, Local: {job['location']}, Link: {job['link']}\n"

#         prompt += "\nPode me dizer qual dessas vagas parece mais interessante e por quê?"

#         # Enviar o prompt ao ChatGPT
#         response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#         {"role": "user", "content": "Seu prompt aqui"}
#         ],
#         max_tokens=50
#         )

#         # Exibir a resposta do ChatGPT
#         print("Resposta do ChatGPT:")
#         print(response.choices[0].text.strip())