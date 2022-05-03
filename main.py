#LISTA pasarle lista de lineas al traductor para su dos fases?
#3 Implementar 2 vueltas

#DUDA: Mnemonico con >1 byte de longitud, sale bien???

#para despues: Saber que tipo de IDX (IDX1 o IDX2)
from mnemonico import Mnemonico
from traductor import Traductor
import os

def main():
    lines = []
    if(os.path.exists("P13.asm")):
        fileAsm = open("P13.asm","r")
        traduce = Traductor("tabcop.txt")
        
    #Leemos Archivo
        while True:
            codeLine = fileAsm.readline()
            if(codeLine == ""):
                print("\t---FIN del Archivo---")
                break
            #Traducemos Linea
            lines.append(traduce.toCode(codeLine))
            #Sale Linea
            
        fileAsm.close()
        
        
    #Creamos Archivo .lst
        try:
            fileList = open("P13.LST","w")
            for i in lines:
                fileList.write(i.toString())
                print(i.toString())
            fileList.close()
            
            filetabSim =open("P13.TABSIM","w")
            for i in traduce.tags:
                filetabSim.write(i + " -> $" + traduce.tags[i] + "\n")
                print(i + " -> $" + traduce.tags[i] + "\n")
            filetabSim.close()
            
            input()
        except:
            print("[ERROR] No se pudo crear el archivo")
            input()
    else:
        print("[ERROR] No se pudo encontrar el archivo .asm")
        input()

main()


