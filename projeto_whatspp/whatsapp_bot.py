import time
from langchain_community.llms import Ollama
from config import init_driver
from utils import clicar_primeira_conversa, obter_nome_contato, obter_mensagens, salvar_historico
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do modelo Ollama
model = Ollama(model="crewai-llama3-8b:latest")

# Inicialização do WebDriver
driver = init_driver()
driver.get('https://web.whatsapp.com')

# Aguardar até que o WhatsApp Web carregue completamente
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
print("WhatsApp Web carregado.")

# Ler o arquivo de texto com a base jurídica uma vez
with open('projeto_whatspp/base_juridica.txt', 'r', encoding='utf-8') as file:
    base_juridica = file.read()

# Ler o prompt do arquivo
with open('projeto_whatspp/prompt.txt', 'r', encoding='utf-8') as file:
    prompt_template = file.read()

# Função para gerar o prompt com o histórico de conversas
def gerar_prompt(historico_conversa):
    historico = "\n".join([f"Usuário: {msg}" if i % 2 == 0 else f"Jusilei: {msg}" for i, msg in enumerate(historico_conversa)])
    prompt = f"{prompt_template}\n{historico}\nResposta do bot:"
    return prompt

def send_and_receive_messages():
    print("Iniciando monitoramento de mensagens...")
    historico_conversas = {}

    while True:
        try:
            if clicar_primeira_conversa(driver):
                contato_nome = obter_nome_contato(driver)
                mensagens = obter_mensagens(driver)

                if contato_nome not in historico_conversas:
                    historico_conversas[contato_nome] = []

                historico_conversa = historico_conversas[contato_nome]

                for mensagem in mensagens:
                    if mensagem not in historico_conversa:
                        historico_conversa.append(mensagem)

                if mensagens and historico_conversa[-1] != mensagens[-1]:  # Verifica se a última mensagem não foi respondida
                    try:
                        prompt = gerar_prompt(historico_conversa)
                        result = model.generate(prompts=[prompt])
                        if result.generations and len(result.generations) > 0:
                            response = result.generations[0][0].text.strip()
                        else:
                            response = "Desculpe, houve um erro ao processar sua solicitação."

                        historico_conversa.append(response)
                        print(f"Resposta gerada: {response}")

                        message_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id='main']/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p"))
                        )
                        message_box.send_keys(response + Keys.ENTER)
                        print(f"Resposta enviada para a mensagem: {mensagens[-1]}")

                        # Salvar o histórico da conversa
                        salvar_historico(contato_nome, historico_conversa)
                    except Exception as e:
                        print(f"Erro ao gerar resposta: {e}")

            time.sleep(1)  # Intervalo para verificar novas mensagens
        except WebDriverException as e:
            print(f"Erro no WebDriver fora do loop: {e}")
        except Exception as e:
            print(f"Erro fora do loop: {e}")
        time.sleep(1)

if __name__ == '__main__':
    try:
        send_and_receive_messages()
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
    except WebDriverException as e:
        print(f"Erro crítico no WebDriver: {e}")
    except Exception as e:
        print(f"Erro crítico: {e}")
    finally:
        driver.quit()
