from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exc_condts
from selenium.webdriver.common.by import By
import re, requests


#Enviamos notificaciones sobre las ofertas a los bots de telelgram
def reportar_ofertas(ofertas, num_ofertas):
    
    token = '1881568573:AAFztCv85mfCwjoyJFXNnxcGi6ULIJV-Row'#Este es el token que nos da BotFather
    ChatId = '-547825387'#El chatid grupal (integrantes: Jorge Amado y Francisco Bojorque)  

    #Enviamos el texto a la URL de la API de telegram:
    if num_ofertas == 1:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={ChatId}&text= Se tiene 1 oferta nueva:\n')
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={ChatId}&text={ofertas}')
    
    elif num_ofertas > 1:
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={ChatId}&text= Se tienen {num_ofertas} ofertas nuevas:\n')
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={ChatId}&text={ofertas}')

    # elif num_ofertas == 0:
    #     #Avisa en el chat del bot que se llama core bot que no hay ofertas nuevas a reportar    
    #     token = '1042288743:AAHbO-tsc7HuaQaulgXXXer3QKOFRfqJ2WQ'  #Este es el token que nos da BotFather
    #     ChatId = '653960523'#El chatid
    #     requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={ChatId}&text=No hay nuevas ofertas')


def login():

    url_forteza = 'https://www.fortesza.com/'#La url de la pagina donde haremos el scraping
    driver.get(url_forteza)

    btn_login = WebDriverWait(driver, 10).until(exc_condts.presence_of_element_located((By.ID, 'btn-login')))
    btn_login.click()

    user = WebDriverWait(driver, 10).until(exc_condts.presence_of_element_located((By.ID, 'input-txt-emailOrUser')))
    user.send_keys('frako789@gmail.com')

    password = driver.find_element_by_id('input-password')
    password.send_keys('Telregio20.')

    btn_ingresar = driver.find_element_by_id('btn-sign-in')
    btn_ingresar.click()

def get_active_offers():
    
    #Ubicamos el elemento que nos muestra las ofertas activas y damos click en el
    x_path_ofertas = '/html/body/app-root/app-user-layout/app-navbar/mat-sidenav-container/mat-sidenav/div/mat-nav-list/mat-accordion[1]/mat-expansion-panel/mat-expansion-panel-header/span/mat-panel-title/span'
    ver_ofertas = WebDriverWait(driver, 10).until(exc_condts.presence_of_element_located((By.XPATH, x_path_ofertas)))
    ver_ofertas.click()

    #Buscamos las ofertas que se encuentran activas
    x_path_ofertas_activas = '/html/body/app-root/app-user-layout/app-navbar/mat-sidenav-container/mat-sidenav-content/div/app-active-offers/div/div/div/div'
    ofertas_activas = WebDriverWait(driver, 10).until(exc_condts.presence_of_element_located((By.XPATH, x_path_ofertas_activas)))

    #Extraemos el texto que contiene la informacion de las ofertas que se encuentran activas
    ofertas_activas = ofertas_activas.text #Obtenemos el texto de cada cuadro donde se encuentra la oferta
    ofertas_activas = re.sub(r'supervised_user_circle', '', ofertas_activas)#Eliminamos texto que no nos interesa
    ofertas_activas = re.sub(r'signal_cellular_alt', '', ofertas_activas)#Eliminamos texto que no nos interesa
    ofertas_activas = re.sub(r'(\d{2}\s\w+\s\d{2}:\d{2}:\d{2})', '\\1*', ofertas_activas) #agreamos un asterisco al final de cada patron para splitear en la siguiente linea
    ofertas_activas = set(ofertas_activas.split('*'))#hacemos una lista utilizando el asterisco como separador

    return ofertas_activas

def get_sub_cads(ofertas):
    #Obtenemos solo el texto que nos interesa para ambos sets (ofertas_activas y ofertas_previas) de cada oferta, 
    #ya que la información de los dias y el # de participantes es variante lo cual hace que obtengamos 
    #falsos positivos cuando hacemos la comparacion entre los sets:
    sub_cadena_ofertas = set()
    for oferta in ofertas:
        if oferta != '':
            fin_cadena = oferta.find('Retorno') + len('Retorno')
            oferta = oferta[:fin_cadena]+'\n'#Le agregamos un salto de linea por tema de legibilidad en el reporte via telegram
            oferta = re.sub(r'Participantes', '', oferta)#Eliminamos texto que no nos interesa, el # de participantes cambia y nos crea falsos positivos    
            oferta = re.sub(r'\d+\s\n', '', oferta)#Eliminamos texto que no nos interesa, el # de participantes cambia y nos crea falsos positivos   
            sub_cadena_ofertas.add(oferta)

    return sub_cadena_ofertas


def get_new_offers(ofertas_activas):

    ofertas_a_escribir = ofertas_activas

    #Abrimos el archivo donde se encuentran guardadas las ofertas del scrap previo, leemos su contenido y creamos una lista
    with open('ofertas.txt', 'r') as file1:
        ofertas_previas = file1.read()
        ofertas_previas = re.sub(r'(\d{2}\s\w+\s\d{2}:\d{2}:\d{2})', '\\1*', ofertas_previas) #agreamos un asterisco al final de cada patron para splitear en la siguiente linea
        ofertas_previas = set(ofertas_previas.split('*'))#hacemos una lista utilizando el asterisco como separador

    #Obtenemos la informaicón de cada oferta hasta donde aparece la palabra "Retorno" ya que el resto no nos intersa y no conviene compararlo
    ofertas_previas = get_sub_cads(ofertas_previas)
    ofertas_activas = get_sub_cads(ofertas_activas)

    #Comparamos informacion antigua con la nueva en busca de nuevas ofertas
    ofertas_nuevas = ofertas_activas.difference(ofertas_previas)
    
    #Escribimos la informacion completa de las ofertas sin ningun filtro ni reemplazo de cadenas, para utilizar esta información 
    #en la próxima ejecución del script
    with open('ofertas.txt', 'w') as file2:
        file2.write(''.join(ofertas_a_escribir))

    return ofertas_nuevas#Retornamos las ofertas nuevas que hayamos identificado y en caso que no existan entonces se devuelve un set vacio


def logout():
    logout = driver.find_element_by_css_selector('.profile-text > span:nth-child(1)')
    logout.click()

    cerrar_sesion = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/div/button[2]')
    cerrar_sesion.click()


if __name__ == '__main__':
    #Establecemos las siguietnes opciones para evitar la ventana de chrome que indica que nuestra conexión no es privada o no es segura
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument('--ignore-ssl-errors=yes')#ignorar errores de ssl
    options.add_argument('--ignore-certificate-errors')#ignorar errores de certificado
    options.add_argument('--no-sandbox')#Desactivar el ambiente de prueba
    options.add_argument('--disable-dev-shm-usage')#Desactivar el ambiente de prueba
    options.add_argument('window-size=1920x1480')#Indicar el tamaño de la ventana muy importante ya que el webdriver no puede determinarlo por si mismo

    driver = webdriver.Chrome(ChromeDriverManager().install() ,options=options)
    #driver.maximize_window()#Para que se maximize la ventana del explorador

    login()#Hacemos login a la pagina de forteza
    ofertas_activas = get_active_offers()#Obtenemos las ofertas que se encuentran activas
    logout()#Cerramos sesión
    nuevas_ofertas = get_new_offers(ofertas_activas)#Obtenemos las nuevas ofertas
    num_ofertas_nuevas = len(nuevas_ofertas)#Obtenemos la cantidad de ofertas nuevas
    nuevas_ofertas = ''.join(nuevas_ofertas)#Convertimos el set en cadena para reportarla en formato legible en telegram
    nuevas_ofertas = nuevas_ofertas.replace("&", "")#Al enviar texto con & telegram el bot de telegram no lo interpreta bien y no manda el texto
    reportar_ofertas(nuevas_ofertas, num_ofertas_nuevas)#Llamamos a la funcion que envia las notificaciones por telegram

    #Finalmente cerramos nuestro driver y se cierra el navegador
    driver.close()
    driver.quit()


