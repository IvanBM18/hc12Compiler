# 2ndo ASL impresión del valor
# Impresion EXT con valor sin $
# BCC es FDR
import copy
from os import remove
from mnemonico import Mnemonico
from baseCalculator import BaseCalculator 
class Traductor:
#Atributos
    line = ""
    fileName = ""
    mTable = []
    fLines = []
    tags = dict()
    idxModes = {"X":"00","Y":"01","SP":"10","PC":"11"}
    acumulators = {"A":"00","B":"01","D":"10"}
    contloc = 0
    contlocHex = 0
    calculator = BaseCalculator()
    calculator.base = 16
#Constructor
    def __init__(self,name) -> None:
        self.fileName = name
        try:
            fTable = open("tabcop.txt","r") 
            self.fLines = fTable.readlines()
            fTable.close()
            self.buildList()
            
        except FileNotFoundError:
            print("[ERROR] No se pudo encontrar el archivo con la tabla de codigos de operación")
            input()
            exit()

#Metodos
    #Crea una lista de Mnemonicos con sus respectivos metodos de direccionamiento
    def buildList(self):
        if(len(self.fLines) > 0):
            mnenmon = Mnemonico("")
            for i in self.fLines:
                row = i.split(" ")
                if(self.search(row[0]) == None): #Cambio de Mnemonico
                    mnenmon = Mnemonico("")
                    mnenmon.name = row[0]
                    self.mTable.append(mnenmon)
                mnenmon.modes[row[1]] = int(row[2]) #Añadimos metodo direcc al diccionario
                mnenmon.codes[row[1]] = row[3][:len(row[3])-1] #Añadimos COP al modo de direccionamiento
                
                
        else:
            print("[ERROR] Tabla de mnemonicos vacia")
    
    #Traduce el mnemonico dado(Momentaneo)
    def toCode(self,line:str):
        aux = line.split()
        # No existe etiqueta
        if(line.find(":") == -1):
            mn = copy.copy(self.search(aux[0])) #Comprobar si se necesita un copy
            if(mn != None): #Es Mnemonico
                mn.line = line
                mn.value = aux[len(aux)-1]
                mn = self.findMode(mn)
                mn.value = str(mn.value).removeprefix("0x")
                mn.value = str(mn.value).removeprefix("$")
                mn.value = mn.value.rjust(2,'0')
                if(mn.value == mn.name) : #caso inherente sin vaor
                    mn.value = -1
                
            else: #Es directiva
                mn = Mnemonico(line)
                mn = self.processDirective(mn,False)
                
        else: #Existe etiqueta
            self.tags[aux[0]] = str(self.contlocHex).removeprefix("0x")
            mn = copy.copy(self.search(aux[1])) #Comprobar si se necesita un copy
            if(mn != None): #Es Mnemonico
                mn.line = line
                mn.value = aux[len(aux)-1]
                mn = self.findMode(mn)
                mn.value = str(mn.value).removeprefix("0x")
                mn.value = mn.value.rjust(2,'0')
            else: #Es directiva
                mn = Mnemonico(line)
                mn = self.processDirective(mn,True)
                mn.tag = aux[0]

        self.updateContloc(mn)
        return mn
    
#PROCESAMIENTO 
    #Procesa directivas
    def processDirective(self, directive : Mnemonico, hasTag : bool):
        directive.isDirective = True
        if(hasTag): #Existe eitqueta en la linea directiva
            line = directive.line.split()
            tag = line[0]
            line = line[1]
        else : #No hay Etiqueta
            line = directive.line.split()
            line = line[0]
            
        if(line == "ORG"):
            aux = int(directive.line.find("$")) + 1
            self.contloc = int(directive.line[aux:aux+4]) #Inicio contador de localidades
            self.contlocHex = hex(int(str(self.contloc),16)) #Inicio contador de localidades en hexa
            directive.direction = 0
            directive.name = line
            directive.value = "--"
            directive.length = 0
            directive.direction = self.contloc
        elif(line == "END"):
            directive.name = line
            directive.value = "--"
            directive.length = 0
            directive.direction = self.contlocHex
        elif(line == "START"):
            self.contloc = 0 #Inicio contador de localidades
            self.contlocHex = 0 #Inicio contador de localidades en hexa
            directive.name = line
            directive.value = "--"
            directive.length = 0
            directive.direction = self.contlocHex
        elif(line == "EQU"):
            directive.name = line
            line = directive.line.split()
            directive.tag = line[0]
            self.tags[tag] = self.calculator.toHexa(line[2]).removeprefix("0x")
            directive.value = self.calculator.toHexa(line[2]).removeprefix("0x").rjust(2,'0')
            directive.length = 0
            directive.direction = self.contlocHex
        elif(line == "DC.B"): #DC.B
            directive.name = line
            directive.direction = self.contlocHex
            directive.value = "--"
            if(len(directive.line.split()) == 1): #Solo reserva memoria
                directive.length = 1
                directive.auxContloc = "00"
            else: #Reserva numeros
                cont = 0
                directive.value = ""
                for i in directive.line.split(","):
                    if(str(i).endswith("\n")):
                        i = str(i).removesuffix("\n")
                    if(str(i).find("DC.B")):
                        i = str(i).removeprefix("\tDC.B ")
                    directive.auxContloc += self.calculator.toHexa(str(i)).removeprefix("0x").rjust(2,'0') + " "
                    cont += 1
                    directive.value +=  str(i).rjust(2,"0") +","
                directive.auxContloc = str(directive.auxContloc).removesuffix(" ")
                directive.length = cont
                directive.value = directive.value.removesuffix(",")
        elif(line == "BSZ"):
            cont = directive.line.split()
            cont = cont[len(cont)-1]
            directive.value = self.calculator.toHexa(str(cont)).removeprefix("0x").rjust(2,'0')
            for i in range(int(cont)):
                directive.auxContloc +=  "00" + " "
            directive.auxContloc = str(directive.auxContloc).removesuffix(" ")
            directive.length = int(cont)
            directive.name = line
            directive.direction = self.contlocHex
        elif(line == "FILL"):
            aux = directive.line.split()
            aux = aux[1]
            coma = aux.find(",")
            a = aux[:coma]
            b = aux[(coma+1):]
            a = self.calculator.toHexa(str(a))
            a = a.removeprefix("0x")
            directive.value = str(a) + "," + str(b)
            a = a.rjust(2,'0') #Añadimos 0s a la izquierda si hace falta
            for i in range(int(b)):
                directive.auxContloc += str(a) + " "
            directive.auxContloc = str(directive.auxContloc).removesuffix(" ")
            directive.length = int(b)
            directive.name = line
            directive.direction = self.contlocHex
        elif(line == "DC.W"): 
            if(len(directive.line.split()) == 1): #Solo reserva memoria
                directive.length = 2
                directive.auxContloc = "00 00"
                directive.value = "--"
            else: #Reserva numeros
                cont = 0
                directive.value = ""
                for i in directive.line.split(","):
                    if(str(i).endswith("\n")):
                        i = str(i).removesuffix("\n")
                    if(str(i).find("DC.W") != -1):
                        i = str(i).removeprefix("\tDC.W ")
                    directive.auxContloc += str(i).rjust(4,'0') + " "
                    cont += 2
                    directive.value +=  str(i) +","
                directive.auxContloc = str(directive.auxContloc).removesuffix(" ")
                directive.length = cont
            directive.name = line
            directive.direction = self.contlocHex
            directive.value = directive.value.removesuffix(",")
            
        elif(line == "FCC"):
            aux = directive.line.split("/")
            aux = aux[1]
            cont = 0
            directive.value = aux
            for i in aux:
                num = self.calculator.toHexa(str(ord(i)))
                num = str(num).removeprefix("0x")
                directive.auxContloc += num.rjust(2,'0') + " "
                cont +=1
            directive.auxContloc = str(directive.auxContloc).removesuffix(" ")
            directive.length = cont
            directive.name = line
            directive.direction = self.contlocHex
        elif(line == "FCB"):
            aux = directive.line.split()
            aux = aux[1]
            directive.value = aux
            aux = self.calculator.toHexa(aux)
            directive.length = 1
            directive.name = line
            directive.direction = self.contlocHex
            directive.value = str(aux).removeprefix("0x").rjust(2,'0')
            directive.auxContloc = str(aux).removeprefix("0x").rjust(2,'0')
        else:
            print("[ERROR]:No se pudo procesar la linea")
            exit()
        return directive
    
    #Procesa Modo de Direccionamiento Indexado
    def processIDX(self,mn :Mnemonico):
        #Aqui obtendremos el valor de rr
        aux = mn.line.split()
        aux = aux[len(aux)-1]
        rr = aux[aux.find(",")+1:]
        operator = mn.value
        if(operator.find("[") != -1): #Función 3 y 6
            #Limpiamos corchetes 
            operator = operator[1:]
            rr = rr[:-1]
            if(operator == "D"): #Función 6 111rr111
                formula = "111" + self.idxModes[rr][0]
                mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
                formula = self.idxModes[rr][1] + "111"
                mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
                mn.opCode = mn.codes[mn.direcMode]
                mn.length = 2
            elif(not operator.isalpha() and int(operator) > 0): #Formula 3 111rr011
                formula = "111" + self.idxModes[rr][0]
                mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
                formula = self.idxModes[rr][1] + "011"
                mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
                mn.value += " " + self.calculator.toHexa(operator).removeprefix("0x").rjust(4,"0")
                mn.opCode = mn.codes[mn.direcMode]
                mn.length = 4
            else: #FDR
                mn.direcMode = ""
                mn.value = "FDR"
                mn.opCode = ""
                mn.length = 0
        elif(self.acumulators.get(operator) != None): #Función 5 111rr1aa
            formula = "111" + self.idxModes[rr][0]
            mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
            formula = self.idxModes[rr][1] + "1" + self.acumulators[operator]
            mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
            mn.opCode = mn.codes[mn.direcMode]
            mn.length = 2
        elif(15 >= int(operator) >= -16): #Formula 1 rr0nnnnn -16 a 15
            operator = int(mn.value)
            mn.length = 2
            formula = self.idxModes[rr] + "0"
            if(operator > 0) : #Positivo
                formula += "0"
                mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
                operator = bin(operator).removeprefix("0b")
                formula = str(operator).rjust(4,'0')
                mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
            else: #Negatiivo
                formula += "1"
                mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
                operator = self.calculator.binComplement(str(operator))
                formula = operator.rjust(4,'0')
                mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
            mn.opCode = mn.codes[mn.direcMode]
        else : #Formula 2 111rr0zs FF FF (+ y -)
            operator = int(mn.value)
            mn.length = 2 + self.getBytes(self.calculator.toHexa(mn.value))
            formula = "111" +  self.idxModes[rr][0]
            mn.value = self.calculator.toHexa("%" + formula).removeprefix("0x")
            formula = self.idxModes[rr][1] + "0"
            formula += str(mn.length - 3)
            if(operator > 0) : #Positivo
                formula += "0"
                operator = self.calculator.toHexa(str(operator)).removeprefix("0x")
            else: #Negativo
                formula += "1"
                operator = self.calculator.toHexa(str(operator))
                operator = self.calculator.hexaComplement(operator).removeprefix("0x")
            mn.value += self.calculator.toHexa("%" + formula).removeprefix("0x")
            mn.value += " " + operator
            mn.opCode = mn.codes[mn.direcMode]
        return mn
    
#BUSQUEDAS
    #Obtiene el metodo de direccionamiento del Mnemonico dado
    def findMode(self,mn :Mnemonico)->Mnemonico:
        posibleModes = mn.modes
        if(len(posibleModes) > 0):
            operator = str(mn.value) #Valor
            for i in posibleModes: #I es la llave
                if(i == "INH"):
                    if(operator == "-1" or operator == mn.name):
                        mn.direcMode = "INH"
                        mn.length = mn.modes[mn.direcMode]
                        mn.opCode = mn.codes[mn.direcMode]
                        mn.direction = self.contlocHex
                        return mn
                elif(i == "IMM"):
                    if(operator.find("#") != -1 ):
                        mn.value = mn.value.removeprefix("#")
                        if(mn.value.find("-") != -1): break
                        if(not self.isFDR(mn.value,mn.codes[i], mn.modes[i])):
                            mn.direcMode = "IMM"
                            mn.value = self.calculator.toHexa(mn.value)
                            mn.length = mn.modes[mn.direcMode]
                            mn.opCode = mn.codes[mn.direcMode]
                            mn.direction = self.contlocHex
                            if(mn.value.find("-0x") != -1):
                                mn.value = self.calculator.hexaComplement(mn.value)
                            return mn
                        else:
                            break
                elif(i == "DIR"):
                    if(operator.find(",") == -1):#Comprobación es un valor
                        if(not self.isFDR(operator,mn.codes[i], mn.modes[i])):
                            mn.direcMode = "DIR"
                            mn.length = mn.modes[mn.direcMode]
                            mn.value = self.calculator.toHexa(mn.value)
                            mn.opCode = mn.codes[mn.direcMode]
                            mn.direction = self.contlocHex
                            return mn
                        
                elif(i=="EXT"):
                    if(operator.find(",") == -1 and operator.find("#") == -1):#Comprobación es un valor
                        if(not self.isFDR(operator,mn.codes[i], mn.modes[i])):
                            mn.direcMode = "EXT"
                            mn.length = mn.modes[mn.direcMode]
                            mn.opCode = mn.codes[mn.direcMode]
                            mn.value = self.calculator.toHexa(mn.value)
                            mn.value = str(mn.value).removeprefix("0x")
                            mn.direction = self.contlocHex
                            return mn
                        else:
                            break
                elif(i == "REL"): 
                    if(self.isValue(operator)): #Es numero
                        size = str(self.getBytes(operator)+1)
                        endDirection = self.calculator.hexaSum(size,self.contlocHex) 
                        result = self.calculator.hexaSubstraction(str(operator),endDirection)
                        if(result.find("-0x") != -1):
                            result = self.calculator.hexaComplement(result)
                        size = self.getBytes(result) - len(mn.codes["REL"])/2
                        positiveSub = int(operator,16) > int(endDirection,16)
                        if(not self.isFDR(result,mn.codes[i], mn.modes[i])):
                            mn.direcMode = "REL"
                            mn.value = result
                            mn.length = mn.modes[mn.direcMode]
                            mn.opCode = mn.codes[mn.direcMode]
                            mn.direction = self.contlocHex
                            return mn
                        else:
                            break
                    else: #Es Tag
                        tagvalue = self.tags[operator + ":"]
                        size = str(self.getBytes(tagvalue))
                        endDirection = self.calculator.hexaSum(size,self.contlocHex) 
                        result = self.calculator.hexaSubstraction(tagvalue,endDirection)
                        if(result.find("-0x") != -1):
                            result = self.calculator.hexaComplement(result)
                        size = self.getBytes(result) - len(mn.codes["REL"])/2
                        positiveSub = int("0x" + tagvalue,16) > int(endDirection,16)
                        if(not self.isFDRREL(result,size, positiveSub)):
                            mn.direcMode = "REL"
                            mn.value = result
                            mn.length = mn.modes[mn.direcMode]
                            mn.opCode = mn.codes[mn.direcMode]
                            mn.direction = self.contlocHex
                            return mn
                        else:
                            break
                elif(i.find("IDX") != -1 and operator.find(",") != -1): 
                    aux = mn.line.split()
                    aux = aux[len(aux)-1]
                    mn.value = aux[:aux.find(",")]
                    mn.direcMode = "IDX"
                    mn = self.processIDX(mn)
                    mn.direction = self.contlocHex
                    return mn
            #FueraDeRango
            mn.direcMode = ""
            mn.length = 0
            mn.opCode = ""
            mn.value = "FDR"
            mn.direction = self.contlocHex
            return mn

    #Busca un Mnemonico en la tabla de mnemonicos
    def search(self, s : str):
        s = s.upper()
        for i in self.mTable:
            if(i.name == s):
                return i
        return None 
    
#VALIDACIONES
    #Me indica si es Fuera de Rango en base al tamaño
    def isFDR(self,value:str,opCode:str, maxLength:int):
        value = self.calculator.toHexa(value)
        value = self.getBytes(value)
        opCode = len(opCode) // 2 #Obtenemos la longitud en bytes de un codigo de operación
        if(value + opCode <= maxLength):
            return False
        return True
    
    #Me indica si es fuera de Rango pero en Restas relativas 
    def isFDRREL(self,number:str,length : int,positive : bool) -> bool:
        if(positive): #Negativa
            if(length == 1): #2 bytes
                if(int(number,16) >= int("0x7F",16)):
                    return True
            else: # 2 bytes
                if(int(number,16) >= int("0x7FFF",16)):
                    return True
        else: #Negativa
            if(length == 1):
                if(int(number,16) >= int("0xFF",16)):
                    return True
            else: #Longitud 2 bytes
                if(int(number,16) >= int("0xFFFF",16)):
                    return True
        return False
    
    #Me indica si el valor es un numero, sino es tag
    def isValue(self,value:str) ->bool:
        if(value.find("#") != -1):
            return True
        elif(value.find("$") != -1):
            return True
        elif(value.find("%") != -1):
            return True
        elif(value.find("@") != -1):
            return True
        elif(value.isdecimal()):
            return True
        return False
#CALCULOS
    #Retorna bytes utilizados por un numero
    def getBytes(self,number:str): #Verificar si recibe solos strings?
        if(int(number,16) <= int("0xFF",16)):
            return 1
        elif(int(number,16) <= int("0xFFFF",16)):
            return 2
        else:
            return 3
    
    #Calcula nuevo contloc
    def updateContloc(self, newMnemon : Mnemonico):
        #Traduce arroja el mnemonico a eso le sumamos la direccion(pasar el contloc al traductor)
        self.contloc += newMnemon.length #ContLoc Decimal actualizado
        if(newMnemon.length < 10):
            aux = int(("0x" + str(newMnemon.length)),16) #Obtenemos el valor en hexadecimal de lo que será añadido
        elif(newMnemon.length >= 10):
            aux = int(hex(newMnemon.length),16)
        b = str(self.contlocHex)
        self.contlocHex = int(b,16) + aux
        self.contlocHex = hex(self.contlocHex)
        