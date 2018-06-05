import os, sys
import os.path

mrForense = ""
idForense = ""
correo = ""
sha2original = ""
sha2copia = ""
sha2imagenDD = ""
discoOrigen = ""
discoDestino = ""
rutaOrigen = ""
rutaDestino = ""


def perito():
    global mrForense
    global idForense
    global correo
    mrForense = input("Ingrese datos del Investigador\nNombre: ")
    idForense = input("Documento de Identidad: ")
    correo = input("Correo: ")
    print("Datos Guardados")
    menu()

def rutaMontada(origen):
    comando = "df -Th /dev/" + origen + " | grep -v Filesystem"
    mon = os.popen(comando).read()
    mon1 = mon.split(" ")
    mon1[-1].rstrip("\n")
    return mon1[-1][:-1]

def esterilizar(disco):
    #este proceso fue sacado del material visto en clase analisis forence
    #consiste en llenar de 0 el disco y luego llenarlo de valores aleatoreos y repetir el proceso 3 veces
    #para al final dar formato al disco
    paso1="dd if=/dev/zero of=/dev/" + disco + " bs=1024" 
    paso2="dd if=/dev/urandom of=/dev/" + disco + " bs=1024"
    formato="mkfs.vfat -c /dev/" + disco + " -n imagenDD"
    for i in range(3):
        os.system(paso1)
        os.system(paso2)
        
    os.system(paso1)
    ru = rutaMontada(disco)
    os.system("umount /dev/" + disco)
    os.system(formato)
    os.system("mkdir " + ru)
    os.system("mount /dev/" + disco + " " + ru)
    print("La esterilización se realizó con éxito")

def imagen():
    global sha2original
    global sha2copia
    global sha2imagenDD
    global discoOrigen
    global discoDestino
    global rutaOrigen
    global rutaDestino
    #se listan los discos menos el host ya que es de la raspberry no de los dispositivos conectados 
    os.system("lsblk | grep -v sda | grep -v sr0") 
    discoOrigen = input("\nDigite el nombre del disco a copiar:")	
    rutaOrigen = rutaMontada(discoOrigen)
    sha2original = os.popen("shasum -a 256 " + rutaOrigen).read()
    #se muestran los discos de destino menos el host y el disco de origen al que se le desea hacer la imagen
    os.system("lsblk | grep -v sda | grep -v sr0 | grep -v "+ discoOrigen) 
    discoDestino = input("\nDigite el nombre del disco donde desea guardar la imagen:")
    rutaDestino = rutaMontada(discoDestino)
    #comando para la creacion de la imagen forence con comando dd
    comando="dd if=/dev/"+discoOrigen+" of="+rutaDestino+"/"+discoOrigen+".dd conv=noerror,sync"
    os.system(comando)
    print("shasum Origen:\n(Esto puede tardar algunos minutos...)\n")
    print(sha2original)
    print("shasum imagen dd:\n(Esto puede tardar algunos minutos...)\n")
    sha2imagenDD = os.popen("shasum -a 256 " + rutaDestino + "/" + discoOrigen + ".dd").read()
    print(sha2imagenDD)
    montarImagen(rutaDestino,discoOrigen)
    sha2copia = os.popen("shasum -a 256 /media/root/imagen" ).read()
    print(sha2copia)
    #print("sha2Origianl len:" + len(sha2original.split(" ")[0]))
    if sha2original.split(" ")[0] == sha2copia.split(" ")[0]:
        print("Exito: imagen creada correctamente")
    else:
         print("Error: la imagen no es igual a la original")
        
    print("Proceso finalizado")

def recoverFiles():
    os.system("mkdir " + rutaDestino + "/archivosRecuperados")
    os.system("photorec /log /debug /d " + rutaDestino + "/archivosRecuperados /cmd " + rutaDestino +"/" + discoOrigen +  ".dd options,mode_ext2,5,search")
    #os.system("photorec /log /debug /d " + rutaDestino + "/archivosRecuperados /cmd /dev/loop0 options,mode_ext2,5,search")
    #os.system("scalpel /root/media/imagen/ -o /dev/" + discoDestino + "/recoveredFiles")
    print("proceso finalizado")

def scanFiles():
    os.system("python vt/vt.py -fr " + rutaDestino + "/archivosRecuperados.1 -jv")
    menu()
   # mensajes = os.popen("python vt/vt.py -fr " + rutaDestino + "/archivosRecuperados.1 -jv").read()
   # print(mensajes)


def montarImagen(montado, imagen):
    os.system("mkdir /media/root/imagen");
    os.system("mount -t vfat -o loop,ro " + montado + "/" + imagen + ".dd" + " /media/root/imagen/")



def banner():
    print( "('-. .-.   ('-.     _ .-') _     ('-.    .-')     ")
    print( "( OO )  /  ( OO ).-.( (  OO) )  _(  OO)  ( OO ).  ")
    print( ",--. ,--.  / . --. / \     .'_ (,------.(_)---\_) ")
    print( "|  | |  |  | \-.  \  ,`'--..._) |  .---'/    _ |  ")
    print( "|   .|  |.-'-'  |  | |  |  \  ' |  |    \  :` `.  ")
    print( "|       | \| |_.'  | |  |   ' |(|  '--.  '..`''.) ")
    print( "|  .-.  |  |  .-.  | |  |   / : |  .--' .-._)   \ ")
    print( "|  | |  |  |  | |  | |  '--'  / |  `---.\       / ")
    print( "`--' `--'  `--' `--' `-------'  `------' `-----'  ")
    return


def menu():
    opcion = 0
    while(opcion != 5):
        banner()
        print ("===== " + mrForense + " ===== " + idForense + " ===== " + correo + " =====")
        print("1. Perfil Perito Forense")
        print("2. Crear imagen forense")
        print("3. Esterilizar un medio")
        print("4. Recuperar Archivos")
        print("5. escanear archivos con virus total")
        print("6. Salir")
        opcion=int(input("Digite una opcion:"))
        if opcion == 1:
            perito()
        elif opcion == 2:
            imagen()
        elif opcion == 3:
            os.system("lsblk | grep -v sda | grep -v sr0") 
            disco=input("\nDigite el nombre del disco a esterilizar:")
            esterilizar(disco)
        elif opcion == 4:
            if rutaDestino != "":
                recoverFiles()
            else:
                print("debe ejecutar primero la creacion de la imagen")
        elif opcion == 5:
            scanFiles()
        elif opcion == 6:
            return

menu()

