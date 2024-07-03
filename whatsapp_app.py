import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from langchain_community.llms import Ollama

# Configuração do modelo Ollama
model = Ollama(model="crewai-llama3-8b:latest")

# Configuração do ChromeDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--user-data-dir=C:/Users/Arthur/AppData/Local/Google/Chrome/User Data')  # Caminho para o perfil do usuário do Chrome
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

driver.get('https://web.whatsapp.com')

# Aguardar até que o WhatsApp Web carregue completamente
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
print("WhatsApp Web carregado.")

def gerar_prompt(nova_mensagem):
    prompt = (
        "Responda sempre em Português do Brasil.\n\n"
        "Você é Jusilei, um especialista em direito brasileiro, encarregado de fornecer respostas claras, precisas e éticas em até 3 linhas. "
        "Sua missão é analisar as perguntas dos usuários e fornecer respostas fundamentadas nas leis brasileiras vigentes e nos princípios éticos da profissão jurídica.\n\n"
        "Siga este processo meticulosamente para garantir que suas respostas sejam úteis e informativas:\n\n"
        "1. Analisar a questão legal apresentada, garantindo que você compreenda o contexto e os detalhes específicos.\n"
        "2. Identificar as leis, regulamentos ou princípios legais relevantes que se aplicam à questão.\n"
        "3. Compor uma resposta concisa e informativa que aborde diretamente a consulta.\n"
        "4. Se informações adicionais forem necessárias para fornecer uma resposta precisa, formular perguntas direcionadas que eliciem os detalhes necessários do consultante.\n"
        "5. Seus parágrafos devem se manter curtos sempre que possível, no máximo 1 a 3 linhas.\n\n"
        "Exemplos de Interação:\n"
        "Usuário: 'Quais são os direitos trabalhistas de uma empregada doméstica?'\n"
        "Jusilei: 'Empregada doméstica tem direito a carteira assinada, férias, 13º, FGTS, entre outros (Lei Complementar nº 150/2015).'\n\n"
        "Usuário: 'Como posso contestar uma multa de trânsito?'\n"
        "Jusilei: 'Apresente recurso à JARI com provas e base legal do CTB dentro do prazo da notificação.'\n\n"
        "Lembre-se:\n"
        "- Mantenha suas respostas claras, precisas e baseadas nas leis brasileiras vigentes.\n"
        "- Evite jargões complexos e explique termos legais quando necessário.\n"
        "- Demonstre sensibilidade e empatia em todas as interações.\n\n"
        "Agora, prepare-se para fornecer respostas jurídicas de alta qualidade, ajudando os usuários a entender melhor seus direitos e obrigações legais.\n\n"
        f"Usuário: {nova_mensagem}\n"
        "Resposta do bot:"
    )
    return prompt

def send_and_receive_messages():
    print("Iniciando monitoramento de mensagens...")
    mensagens_respondidas = set()

    while True:
        try:
            conversations = driver.find_elements(By.XPATH, "//*[@id='pane-side']//div[@role='gridcell']")
            for conversation in conversations:
                try:
                    print("Tentando clicar na conversa...")
                    action = ActionChains(driver)
                    action.move_to_element_with_offset(conversation, -50, 0).click().perform()
                    time.sleep(1)
                    print("Conversa clicada, tentando encontrar mensagens...")

                    messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')]//div[@class='copyable-text']")
                    if messages:
                        last_message_element = messages[-1]
                        last_message_text = last_message_element.text
                        print(f"Última mensagem recebida: {last_message_text}")

                        # Verifica se a mensagem é de um grupo e contém a menção necessária
                        if "@Defensoria Bot IA (beta)" in last_message_text or "grupo" not in last_message_element.get_attribute('data-pre-plain-text'):
                            if last_message_text not in mensagens_respondidas:
                                mensagens_respondidas.add(last_message_text)

                                try:
                                    prompt = gerar_prompt(last_message_text)
                                    result = model.generate(prompts=[prompt])
                                    if result.generations and len(result.generations) > 0:
                                        response = result.generations[0][0].text.strip()
                                    else:
                                        response = "Desculpe, houve um erro ao processar sua solicitação."

                                    print(f"Resposta gerada: {response}")

                                    message_box = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, "//*[@id='main']/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p"))
                                    )
                                    message_box.send_keys(response + Keys.ENTER)
                                    print(f"Resposta enviada para a mensagem: {last_message_text}")
                                except Exception as e:
                                    print(f"Erro ao gerar resposta: {e}")

                except TimeoutException:
                    print("Erro: Timeout ao tentar clicar na conversa ou encontrar mensagens.")
                except Exception as e:
                    print(f"Erro ao processar a conversa: {e}")

            time.sleep(1)
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(1)

if __name__ == '__main__':
    send_and_receive_messages()
