import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Função para clicar na aba "Tudo"
def clicar_aba_tudo(driver):
    try:
        aba_tudo = driver.find_element(By.XPATH, "//*[@id='side']/div[2]/button[1]/div/div")
        action = ActionChains(driver)
        action.move_to_element(aba_tudo).click().perform()
        time.sleep(2)  # Esperar um pouco para garantir que a aba seja selecionada
        return True
    except NoSuchElementException:
        print("Erro ao encontrar a aba 'Tudo'.")
        return False

# Função para clicar na primeira conversa da lista
def clicar_primeira_conversa(driver):
    try:
        primeira_conversa = driver.find_element(By.XPATH, "//*[@id='pane-side']/div[1]/div/div/div/div/div/div/div[2]")
        action = ActionChains(driver)
        action.move_to_element(primeira_conversa).click().perform()
        time.sleep(2)  # Esperar um pouco para garantir que a conversa carregue
        return True
    except NoSuchElementException:
        print("Primeira conversa não encontrada.")
        return False

# Função para obter o nome do contato
def obter_nome_contato(driver):
    try:
        contato_element = driver.find_element(By.XPATH, "//*[@id='main']/header/div[2]/div/div/div/span")
        contato_nome = contato_element.text
        print(f"Nome do contato: {contato_nome}")
        return contato_nome
    except NoSuchElementException:
        print("Erro ao encontrar o nome do contato, usando 'Desconhecido'.")
        return "Desconhecido"

# Função para obter as mensagens da conversa
def obter_mensagens(driver):
    try:
        messages = driver.find_elements(By.XPATH, "//*[@id='main']/div[3]/div/div[2]//div[contains(@class, 'message-in') or contains(@class, 'message-out')]//div[@class='copyable-text']")
        return messages
    except NoSuchElementException:
        print("Erro ao encontrar mensagens.")
        return []

# Função para verificar se a mensagem foi enviada pelo bot
def is_bot_message(message_element):
    try:
        message_element.find_element(By.XPATH, ".//*[@id='main']/div[3]/div/div[2]/div[2]/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/div/div/span")
        return True
    except NoSuchElementException:
        return False

# Função para verificar se a mensagem foi enviada pelo usuário
def is_user_message(message_element):
    try:
        # Verificar se a mensagem está do lado esquerdo
        message_element.find_element(By.XPATH, ".//div[contains(@class, 'message-in')]")
        return True
    except NoSuchElementException:
        return False

# Função para obter a última mensagem do usuário na lista de conversas
def obter_ultima_mensagem_usuario(driver):
    try:
        ultima_mensagem_element = driver.find_element(By.XPATH, "//*[@id='pane-side']/div[1]/div/div/div/div/div/div/div[2]/div[2]/div[1]/span/span")
        return ultima_mensagem_element.text
    except NoSuchElementException:
        print("Erro ao encontrar a última mensagem do usuário.")
        return ""
