#Si desea que el programa actue por comando de voz tambien deberá instalar pyaudio
#pip install pyaudio
import speech_recognition as sr         #pip install speechrecognition
import subprocess as sub
import pyttsx3                          #pip install pyttsx3
import pywhatkit                        #pip install pywhatkit
import wikipedia                        #pip install wikipedia
import datetime                         #pip install datetime
import keyboard                         #pip install keyboard
import cam                              #importamos el archivo cam.py
import os
import pymongo                          #pip install pymongo
from tkinter import *
from PIL import Image, ImageTk
from pygame import mixer                #pip install pygame --pre
import threading as tr
import serial as ser                    #pip install serial
import webbrowser

main_window = Tk()
main_window.title("Emma asistente virtual")

main_window.geometry("800x550")
main_window.resizable(0, 0)
main_window.configure(bg='#00B4DB')

comandos = """
    Comandos que puedes usar:
    - Reproduce..(canción)
    - Busca...(algo)
    - Abre...(página web o app)
    - Alarma..(hora en 24H)
    - Archivo...(nombre)
    - Colores (rojo, azul, amarillo)
    - Termina
"""

label_title = Label(main_window, text="Emma AV", bg="#6DD5FA", fg="#2c3e50",
                    font=('Arial', 30, 'bold'))
label_title.pack(pady=10)

canvas_comandos = Canvas(bg="#6dd5ed", height=170, width=195)
canvas_comandos.place(x=0, y=0)
canvas_comandos.create_text(90, 80, text=comandos,
                            fill="#434343", font='Arial 10')
text_info = Text(main_window, bg="#00B4DB", fg="black")
text_info.place(x=0, y=170, height=280, width=198)

Emma_photo = ImageTk.PhotoImage(Image.open("./img/emma-prototipo.jpeg"))
window_photo = Label(main_window, image=Emma_photo)
window_photo.pack(pady=10)

def mexican_voice():
    change_voice(0)

def spanish_voice():
    change_voice(1)

def change_voice(id):
    engine.setProperty('voice', voices[id].id)
    engine.setProperty('rate', 145)
    talk("Hola, soy el asistente con el nombre menos argentino posible, Emma")

name = "Emma"
listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 145)

def charge_data(name_dict, name_file):
    try:
        with open(name_file) as f:
            for line in f:
                (key, val) = line.split(",")
                val = val.rstrip("\n")
                name_dict[key] = val
    except FileNotFoundError as e:
        pass

sites = dict()
charge_data(sites, "pages.txt")
files = dict()
charge_data(files, "archivos.txt")
programs = dict()
charge_data(programs, "apps.txt")
contacts = dict()
charge_data(contacts, "contacts.txt")

def talk(text):
    engine.say(text)
    engine.runAndWait()

def read_and_talk():
    text = text_info.get("1.0", "end")
    talk(text)

def write_text(text_wiki):
    text_info.insert(INSERT, text_wiki)

def listen(phrase=None):
    listener = sr.Recognizer()    
    with sr.Microphone() as source:            
        listener.adjust_for_ambient_noise(source)
        talk(phrase)
        pc = listener.listen(source)
    try:
        rec = listener.recognize_google(pc, language="es")
        rec = rec.lower()
    except sr.UnknownValueError:
        print("No te entendí. ¿Podrias repetirlo?")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return rec

def reproduce(rec):
    music = rec.replace('reproduce', '')
    print("Reproduciendo " + music)
    talk("Reproduciendo " + music)
    pywhatkit.playonyt(music)

def busca(rec):
    search = rec.replace('busca', '')
    wikipedia.set_lang("es")
    wiki = wikipedia.summary(search, 1)
    talk(wiki)
    write_text(search + ": " + wiki)

def thread_alarma(rec):
    t = tr.Thread(target=clock, args=(rec,))
    t.start()

def colores(rec):
    talk("Enseguida")
    t = tr.Thread(target=cam.capture)
    t.start()
    
def abre(rec):
    task = rec.replace('abre', '').strip()

    if task in sites:
        for task in sites:
            if task in rec:
                sub.call(f'start chrome.exe {sites[task]}', shell=True)
                talk(f'Abriendo {task}')
    elif task in programs:
        for task in programs:
            if task in rec:
                talk(f'Abriendo {task}')
                os.startfile(programs[task])
    else:
        talk("Parece que aún no has agregado nada al respecto, \
            no seas boludo y agrega la app o pagina antes de pedirla!")

def archivo(rec):
    file = rec.replace('archivo', '').strip()
    if file in files:
        for file in files:
            if file in rec:
                sub.Popen([files[file]], shell=True)
                talk(f'Abriendo {file}')
    else:
        talk("Parece que aún no has agregado nada al respecto, \
            ¿No aprendes? usa los botones de agregar!")

def escribe(rec):
    try:
        with open("nota.txt", 'a') as f:
            write(f)

    except FileNotFoundError as e:
        file = open("nota.txt", 'a')
        write(file)

def clock(rec):
    num = rec.replace('alarma', '')
    num = num.strip()
    talk("Alarma activada a las " + num + " horas")
    if num[0] != '0' and len(num) < 5:
        num = '0' + num
    print(num)
    while True:
        if datetime.datetime.now().strftime('%H:%M') == num:
            print("DESPIERTA!!!")
            mixer.init()
            mixer.music.load("./audio/auronplay-alarma.mp3")
            mixer.music.play()
        else:
            continue
        if keyboard.read_key() == "s":
            mixer.music.stop()
            break


def cierra(rec):
    for task in programs:
        kill_task = programs[task].split('\\')
        kill_task = kill_task[-1]
        if task in rec:
            sub.call(f'TASKKILL /IM {kill_task} /F', shell=True)
            talk(f'Cerrando {task}')
        if 'todo' in rec:
            sub.call(f'TASKKILL /IM {kill_task} /F', shell=True)
            talk(f'Cerrando {task}')
    if 'ciérrate' in rec:
        talk('Adiós!')
        sub.call('TASKKILL /IM Emma_guiyt.exe /F', shell=True)

def serial_led(val):        
    data = str(val).encode()
    ser.write(data)

key_words = {
    'reproduce': reproduce,
    'busca': busca,
    'alarma': thread_alarma,
    'colores': colores,
    'abre': abre,
    'archivo': archivo,
    'escribe': escribe,
    'cierra': cierra,
    'ciérrate': cierra,
}

def run_Emma():
    talk("Te escucho...")
    while True:
        try:
            rec = listen("")
        except UnboundLocalError:
            talk("Repetí lo que dijiste degenerado...")
            continue
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        elif rec.split()[0] in key_words:
            key = rec.split()[0]        
            key_words[key](rec)
        else:
            break
    main_window.update()

def write(f):
    talk("¿Qué querés que escriba navo?")
    rec_write = listen("Te escucho gil")
    f.write(rec_write + os.linesep)
    f.close()
    talk("Listo, y ya dejate de joder")
    sub.Popen("nota.txt", shell=True)

def open_w_files():
    global namefile_entry, pathf_entry
    window_files = Toplevel()
    window_files.title("Agrega archivos")
    window_files.configure(bg="#434343")
    window_files.geometry("300x200")
    window_files.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_files)} center')

    title_label = Label(window_files, text="Agrega un archivo",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_files, text="Nombre del archivo",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namefile_entry = Entry(window_files)
    namefile_entry.pack(pady=1)

    path_label = Label(window_files, text="Ruta del archivo",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    pathf_entry = Entry(window_files, width=35)
    pathf_entry.pack(pady=1)

    save_button = Button(window_files, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_files)
    save_button.pack(pady=4)

def open_w_apps():
    global nameapps_entry, patha_entry
    window_apps = Toplevel()
    window_apps.title("Agrega apps")
    window_apps.configure(bg="#434343")
    window_apps.geometry("300x200")
    window_apps.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_apps)} center')

    title_label = Label(window_apps, text="Agrega una app",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_apps, text="Nombre de la app",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    nameapps_entry = Entry(window_apps)
    nameapps_entry.pack(pady=1)

    path_label = Label(window_apps, text="Ruta de la app",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    patha_entry = Entry(window_apps, width=35)
    patha_entry.pack(pady=1)

    save_button = Button(window_apps, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_apps)
    save_button.pack(pady=4)

def open_w_pages():
    global namepages_entry, pathp_entry
    window_pages = Toplevel()
    window_pages.title("Agrega páginas web")
    window_pages.configure(bg="#434343")
    window_pages.geometry("300x200")
    window_pages.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_pages)} center')

    title_label = Label(window_pages, text="Agrega una página web",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_pages, text="Nombre de la página",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namepages_entry = Entry(window_pages)
    namepages_entry.pack(pady=1)

    path_label = Label(window_pages, text="URL de la página",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    path_label.pack(pady=2)

    pathp_entry = Entry(window_pages, width=35)
    pathp_entry.pack(pady=1)

    save_button = Button(window_pages, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_pages)
    save_button.pack(pady=4)

def open_w_contacts():
    global namecontact_entry, phone_entry
    window_contacts = Toplevel()
    window_contacts.title("Agrega un contacto")
    window_contacts.configure(bg="#434343")
    window_contacts.geometry("300x200")
    window_contacts.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(window_contacts)} center')

    title_label = Label(window_contacts, text="Agrega un contacto",
                        fg="white", bg="#434343", font=('Arial', 15, 'bold'))
    title_label.pack(pady=3)
    name_label = Label(window_contacts, text="Nombre del contacto",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    name_label.pack(pady=2)

    namecontact_entry = Entry(window_contacts)
    namecontact_entry.pack(pady=1)

    phone_label = Label(window_contacts, text="Número celular (con código del país).",
                       fg="white", bg="#434343", font=('Arial', 10, 'bold'))
    phone_label.pack(pady=2)

    phone_entry = Entry(window_contacts, width=35)
    phone_entry.pack(pady=1)

    save_button = Button(window_contacts, text="Guardar", bg='#16222A',
                         fg="white", width=8, height=1, command=add_contacts)
    save_button.pack(pady=4)

def add_files():
    name_file = namefile_entry.get().strip()
    path_file = pathf_entry.get().strip()

    files[name_file] = path_file
    save_data(name_file, path_file, "archivos.txt")
    namefile_entry.delete(0, "end")
    pathf_entry.delete(0, "end")

def add_apps():
    name_file = nameapps_entry.get().strip()
    path_file = patha_entry.get().strip()

    programs[name_file] = path_file
    save_data(name_file, path_file, "apps.txt")
    nameapps_entry.delete(0, "end")
    patha_entry.delete(0, "end")

def add_contacts():
    name_contact = namecontact_entry.get().strip()
    phone = phone_entry.get().strip()

    contacts[name_contact] = phone
    save_data(name_contact, phone, "contacts.txt")
    namecontact_entry.delete(0, "end")
    phone_entry.delete(0, "end")

def save_data(key, value, file_name):
    try:
        with open(file_name, 'a') as f:
            f.write(key + "," + value + "\n")
    except FileNotFoundError:
        file = open(file_name, 'a')
        file.write(key + "," + value + "\n")


pages = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.wikipedia.org",
    "https://www.amazon.com",
    "https://www.linkedin.com",
    "https://www.reddit.com",
    "https://www.netflix.com"
]

def add_pages():
    while True:
        page = input("Ingrese un enlace o URL (o escriba 'salir' para detenerse): ")
        if page.lower() == 'salir':
            break
        pages.append(page)

# Función para abrir los enlaces en el navegador
def talk_pages():
    if len(pages) == 0:
        print("No hay enlaces para mostrar.")
    else:
        print("Enlaces disponibles:")
        for idx, page in enumerate(pages, start=1):
            print(f"{idx}. {page}")
        
        choice = input("Seleccione el número de enlace que desea abrir (o escriba 'salir' para detenerse): ")
        if choice.lower() != 'salir':
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pages):
                    webbrowser.open(pages[choice_idx], new=2)
                else:
                    print("Selección inválida.")
            except ValueError:
                print("Entrada inválida. Por favor, ingrese un número válido.")

# Ejecución del programa
if __name__ == "__main__":
    while True:
        action = input("Seleccione una acción: 'agregar' para agregar enlaces, 'abrir' para abrir enlaces, o 'salir' para terminar: ")
        
        if action.lower() == 'agregar':
            add_pages()
        elif action.lower() == 'abrir':
            talk_pages() 
        elif action.lower() == 'salir':
            break
        else:
            print("Acción inválida. Por favor, elija una acción válida.")

def talk_apps():
    if bool(programs) == True:
        talk("Bien loco, agregaste una app")
        for app in programs:
            talk(app)
    else:
        talk("Aún no agregás ninguna app zapallo!")

def talk_files():
    if bool(files) == True:
        talk("Has agregado los siguientes archivos")
        for file in files:
            talk(file)
    else:
        talk("Tenes que agregar archivos si queres abrir archivos... Sentido comun papi")

def talk_contacts():
    if bool(contacts) == True:
        talk("Has agregado los siguientes contactos")
        for cont in contacts:
            talk(cont)
    else:
        talk("Primero tenes que agregar contactos genio!")

def give_me_name():
    talk("Buenas, ¿cómo te llamas maestro?")
    name = listen("Te escucho")
    name = name.strip()
    talk(f"Bienvenido {name}")
    try:
        with open("./txt/name.txt", 'w') as f:
            f.write(name)
    except FileNotFoundError:
        file = open("name.txt", 'w')
        file.write(name)

def say_hello():
    if os.path.exists("name.txt"):
        with open("name.txt") as f:
            for name in f:
                talk(f"Hola, bienvenido {name}")
    else:
        give_me_name()

def thread_hello():
    t = tr.Thread(target=say_hello)
    t.start()

thread_hello()

button_voice_mx = Button(main_window, text="Voz Español", fg="white", bg="#45a247",
                         font=("Arial", 10, "bold"), command=mexican_voice)
button_voice_mx.place(x=625, y=80, width=100, height=30)
button_voice_es = Button(main_window, text="Voz Inglés", fg="white", bg="#f12711",
                         font=("Arial", 10, "bold"), command=spanish_voice)
button_voice_es.place(x=625, y=115, width=100, height=30)

button_listen = Button(main_window, text="Escuchar", fg="white", bg="#1565C0",
                       font=("Arial", 15, "bold"), width=30, height=1, command=run_Emma)
button_listen.pack(side=BOTTOM, pady=10)
button_speak = Button(main_window, text="Hablar", fg="white", bg="#0083B0",
                      font=("Arial", 10, "bold"), command=read_and_talk)
button_speak.place(x=625, y=190, width=100, height=30)

button_add_files = Button(main_window, text="Agregar archivos", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_files)
button_add_files.place(x=615, y=230, width=120, height=30)
button_add_apps = Button(main_window, text="Agregar apps", fg="white", bg="#4286f4",
                         font=("Arial", 10, "bold"), command=open_w_apps)
button_add_apps.place(x=615, y=270, width=120, height=30)
button_add_pages = Button(main_window, text="Agregar páginas", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_pages)
button_add_pages.place(x=615, y=310, width=120, height=30)

button_add_contacts = Button(main_window, text="Agregar contactos", fg="white", bg="#4286f4",
                          font=("Arial", 10, "bold"), command=open_w_contacts)
button_add_contacts.place(x=615, y=350, width=125, height=30)

button_tell_pages = Button(main_window, text="Páginas agregadas", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_pages)
button_tell_pages.place(x=205, y=425, width=125, height=30)
button_tell_apps = Button(main_window, text="Apps agregadas", fg="white", bg="#2c3e50",
                          font=("Arial", 8, "bold"), command=talk_apps)
button_tell_apps.place(x=335, y=425, width=125, height=30)
button_tell_files = Button(main_window, text="Archivos agregados", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_files)
button_tell_files.place(x=465, y=425, width=125, height=30)

button_tell_files = Button(main_window, text="Contactos agregados", fg="white", bg="#2c3e50",
                           font=("Arial", 8, "bold"), command=talk_contacts)
button_tell_files.pack(side=BOTTOM, pady=3)

main_window.mainloop()