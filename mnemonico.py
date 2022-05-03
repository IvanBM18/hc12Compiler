#-1 valor invalido o inexistente(si es diferente a inh significa FDR)
#Valor suele ser un tipo Str
#FDR en valor es fuera de rango


class Mnemonico:
#Atributos
    line :str #EJ. E1: LDCA $450 
    name :str #Ej. ADCA
    opCode = 0 #Ej 1806
    length :int #Ej. 3
    value = "-1" #Ej. 450
    direcMode :str #Ej. INH
    direction = 0 #Ej. 4002
    auxContloc :str = "" #EJ. 00 00 00
    tag:str #Ej. ET1:
    tagValue = 0 #Ej. 4002
    modes = dict() #Ej. "INH:2,EXT:3"
    codes = dict() #Ej. {"INH":86,"DIR",96}
    isDirective = False
    #Crear otro diccionario, "INH:96,DIR:86"

#Constructor
    def __init__(self, line) -> None:
        self.line = line
        self.modes = dict()
        self.codes = dict()
        self.value = "-1"
        self.opCode = 0
        self.length = 0
        self.tag = ""
#toString
    def toString(self): #Le falta codigo de Operación
        result = ""
        if(str(self.direction).find("0x") != -1): #Eliminamos 0x de la dirección
            self.direction = str(self.direction).removeprefix("0x")
        result += str(self.direction).rjust(4,"0") + "\t"
        if(self.tag != ""):
            result += self.tag + "\t"
        if(not self.isDirective):
            result += self.name + " "
            result += self.direcMode + " "
            result += str(self.opCode) + " "
            if(str(self.value) == "FDR"): #Valor esta FDR
                result += str(self.value)
            else:
                if(len(str(self.value)) == 3 and str(self.value) != "-1"): #Redondeo de 0s para valor de 2 bytes
                    result += str(self.value).rjust(4,'0')
                elif(len(str(self.value)) == 1): #Redondeo de 0s para valor de 1 bytes
                    result += str(self.value).rjust(2,'0')
                elif(self.value == -1): #valor invalido?
                    pass
                else:
                    result += str(self.value)
        else: #Es DIrectiva
            if(self.auxContloc != ""):
                result += self.auxContloc + "\t"
            result += self.name + " "
            if(str(self.value) != "--"):
                result += str(self.value)
        result += "\t[LI = " + str(self.length) + "]\n" 
        return result


