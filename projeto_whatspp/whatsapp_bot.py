import time
from threading import Thread
from langchain_community.llms import Ollama
from config import init_driver
from utils import clicar_aba_tudo, clicar_primeira_conversa, obter_nome_contato, obter_ultima_mensagem_usuario
from salvar_contato import salvar_historico, carregar_historico, salvar_ultima_mensagem, carregar_ultima_mensagem, inicializar_arquivo_excel
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Função para carregar o prompt da IA a partir de um arquivo txt
def carregar_prompt_txt():
    prompt_path = "projeto_whatspp/prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r', encoding='utf-8') as file:
            prompt = file.read()
            return prompt
    else:
        raise FileNotFoundError(f"Arquivo {prompt_path} não encontrado.")

# Carregar o prompt da IA
prompt = carregar_prompt_txt()

# Configuração do modelo Ollama
model = Ollama(model="crewai-llama3-8b:latest")

# Inicialização do WebDriver
driver = init_driver()
driver.get('https://web.whatsapp.com')

# Aguardar até que o WhatsApp Web carregue completamente
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
print("WhatsApp Web carregado.")

def obter_nome_grupo(driver):
    try:
        nome_grupo = driver.find_element(By.XPATH, '//*[@id="main"]/header/div[2]/div[1]/div/span').text
        return nome_grupo
    except NoSuchElementException:
        return None

def is_message_from_user(driver):
    try:
        mensagens = driver.find_elements(By.XPATH, "//*[@id='main']/div[3]/div/div[2]//div[contains(@class, 'message-in')]//div[@class='copyable-text']")
        if mensagens:
            ultima_mensagem = mensagens[-1].text
            return ultima_mensagem
        return ""
    except NoSuchElementException:
        return ""

def responder_mensagem(contato_nome, ultima_mensagem_usuario, historico_conversas, mensagens_processadas):
    if contato_nome not in historico_conversas:
        historico_conversas[contato_nome] = carregar_historico(contato_nome)
        print(f"Histórico carregado para {contato_nome}: {historico_conversas[contato_nome]}")

    historico_conversa = historico_conversas[contato_nome]

    # Verificar se a última mensagem do usuário foi processada
    if ultima_mensagem_usuario and ultima_mensagem_usuario not in mensagens_processadas:
        # Adicionar a última mensagem do usuário ao histórico
        historico_conversa.append(f"{contato_nome}: {ultima_mensagem_usuario}")
        mensagens_processadas.add(ultima_mensagem_usuario)  # Marcar como processada

        try:
            # Usar o histórico de conversa como prompt
            prompt = "\n".join(historico_conversa)
            result = model.generate(prompts=[prompt])
            if result.generations and len(result.generations) > 0:
                response = result.generations[0][0].text.strip()
            else:
                response = "Desculpe, houve um erro ao processar sua solicitação."

            # Salvar a última mensagem do bot
            ultima_mensagem_bot = f"Defensoria IA: {response}"
            historico_conversa.append(ultima_mensagem_bot)
            print(f"Resposta gerada: {response}")

            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='main']/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p"))
            )
            message_box.send_keys(response + Keys.ENTER)
            print(f"Resposta enviada para a mensagem: {ultima_mensagem_usuario}")

            # Salvar o histórico da conversa e a última mensagem do bot
            salvar_historico(contato_nome, historico_conversa)
            salvar_ultima_mensagem(ultima_mensagem_bot)
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")

def verificar_novas_conversas(driver, historico_conversas, mensagens_processadas):
    try:
        conversas = driver.find_elements(By.XPATH, '//*[@id="pane-side"]//div[@role="row"]')
        for conversa in conversas:
            try:
                conversa.click()
                time.sleep(0.5)  # Tempo para a conversa carregar
                contato_nome = obter_nome_contato(driver)
                if not contato_nome:
                    contato_nome = obter_nome_grupo(driver)
                if contato_nome:
                    print(f"Nome do contato ou grupo: {contato_nome}")
                    ultima_mensagem_usuario = is_message_from_user(driver)
                    print(f"Última mensagem do usuário: {ultima_mensagem_usuario}")
                    if "grupo" in contato_nome.lower() and "@Defensoria Bot IA (beta)" not in ultima_mensagem_usuario:
                        print("Mensagem não mencionou o bot diretamente em um grupo. Ignorando.")
                        continue
                    responder_mensagem(contato_nome, ultima_mensagem_usuario, historico_conversas, mensagens_processadas)
            except Exception as e:
                print(f"Erro ao verificar conversa: {e}")
    except Exception as e:
        print(f"Erro ao procurar novas conversas: {e}")

def send_and_receive_messages():
    print("Iniciando monitoramento de mensagens...")
    historico_conversas = {}
    ultima_mensagem_bot = carregar_ultima_mensagem()
    mensagens_processadas = set()  # Conjunto para rastrear mensagens processadas

    while True:
        try:
            if clicar_aba_tudo(driver):  # Clicar na aba "Tudo" antes de selecionar a conversa
                start_time = time.time()  # Iniciar o temporizador

                while True:
                    verificar_novas_conversas(driver, historico_conversas, mensagens_processadas)
                    if time.time() - start_time > 10:  # Verificar se o tempo excede 10 segundos
                        print("Verificação de novas conversas...")
                        start_time = time.time()
                        break

            time.sleep(0.2)  # Intervalo reduzido para verificar novas mensagens
        except (WebDriverException, NoSuchElementException, TimeoutException) as e:
            print(f"Erro no WebDriver fora do loop: {e}")
        except Exception as e:
            print(f"Erro fora do loop: {e}")
        time.sleep(0.5)

if __name__ == '__main__':
    inicializar_arquivo_excel()
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
