class BaseCalculator:
    base : int
    value : str
    traduce : str
    def __init__(self) -> None:
        self.base = 16
        self.value = 0
        self.traduce = 0
    
    def toBase(self,value:str,base:int) -> str:
        if(value[0] == "#"):
            value = value.removeprefix("#")
        #A Hexa
        if(base == 16): #A Hexa
            return(self.toHexa(value))
        elif(base == 10):  #A decimal
            return(self.toDecimal(value))
        elif(base == 8): #A Octal
            pass
        elif(base == 2): #A binario
            pass
        else:
            return 0
    
    #A Hexadecimal
    def toHexa(self, number:str) -> str:
        if(number[0] == "$"): #Ya es hexa
            number = number.removeprefix("$")
            number = "0x"+number
            return number
        if(number[0] == "@"): #Octal
            number = number.removeprefix("@")
            aux = int(number,8) #Octal a decimal
            return hex(aux)
        if(number[0] == "%"): #Es Binario
            number = number.removeprefix("%")
            aux = int(number,2) #Binario a Decimal
            return hex(aux)
        return hex(int(number))#Decimal
    
    #Numero negatio a Binario con C1
    #-2 sale 1110
    #-2 sale 10
    #10 a 0010
    #0010 a 1110
    def binComplement(self,number:str) ->str:
        result = bin(-2).removeprefix("-0b")
        if(number == "-16"):
            return "0000"
        if(-15 <= int(number) ):
            result = result.rjust(4,'0')
        else:
            result = result.rjust(8,'0')
        flag1 = False
        complement = ""
        for i in result[::-1]:
            if(flag1):
                if(i == "1"):
                    complement += "0"
                else:
                    complement += "1"
            else:
                complement += i
                if(i == "1"):
                    flag1 = True
        return complement[::-1]
    
    # 400a -> BFF6
    def hexaComplement(self, number:str) ->str:
        number = number.removeprefix("-0x")
        last = number[-1]
        result = ""
        for i in number:
            if(i != last):
                result += str(hex(int(i,16) -15)).removeprefix("-0x")
            else:
                result += str(hex(int(i,16) -16)).removeprefix("-0x")
        return "0x" + result
    #Resta 2 numeros en hexa
    def hexaSubstraction(self,minuend:str,subtracting:str) -> str:
        if(minuend.find("0x") == -1):
            minuend = "0x" + minuend
        if(subtracting.find("0x") == -1):
            subtracting = "0x" + subtracting
        result = int(minuend,16) - int(subtracting,16)
        return hex(result)
    
    #Suma 2 numeros en hexa
    def hexaSum(self,a :str, b:str) -> sum:
        if(a.find("0x") == -1):
            a = "0x" + a
        if(b.find("0x") == -1):
            b = "0x" + b
        result = int(a,16) + int(b,16)
        return hex(result)
    
    #A decimal
    def toDecimal(self,number:str) -> str:
        if(number[0] == "$"): #Es hexa
            number = number.removeprefix("$")
            return int(number,16)
        if(number.find("0x") != -1): #Es Hexa
            number = number.removeprefix("0x")
            return int(number,16)
        if(number[0] == "@"): #Octal
            number = number.removeprefix("@")
            return int(number,8)
        if(number[0] == "%"): #Es Binario
            number = number.removeprefix("%")
            return int(number,2)
        return number#Decimal
    