import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

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
        contato_element = driver.find_element(By.XPATH, "//*[@id='main']/header/div[2]/div[1]/div/span")
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
        return [message.text for message in messages]
    except NoSuchElementException:
        print("Erro ao encontrar mensagens.")
        return []

# Função para salvar o histórico da conversa
def salvar_historico(contato, historico_conversa):
    with open(f'{contato}.txt', 'w', encoding='utf-8') as file:
        for linha in historico_conversa:
            file.write(f"{linha}\n")
