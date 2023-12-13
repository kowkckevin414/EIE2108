class Quaternion:
    def __init__(self, value):
        if type(value)!=list or len(value)!=4:
            print('Err: It must be in a list of 4 values')
        else:
            self.value = value
    
    def Add(self, other):
        return Quaternion([self.value[0]+other.value[0],self.value[1]+other.value[1],self.value[2]+other.value[2],self.value[3]+other.value[3]])
    
    def Mul(self, other):
        real = (self.value[0]*other.value[0])-(self.value[1]*other.value[1])-(self.value[2]*other.value[2])-(self.value[3]*other.value[3])
        i = (self.value[0]*other.value[1])+(self.value[1]*other.value[0])+(self.value[2]*other.value[3])-(self.value[3]*other.value[2])
        j = (self.value[0]*other.value[2])-(self.value[1]*other.value[3])+(self.value[2]*other.value[0])+(self.value[3]*other.value[1])
        k = (self.value[0]*other.value[3])+(self.value[1]*other.value[2])-(self.value[2]*other.value[1])+(self.value[3]*other.value[0])
        return Quaternion([real,i,j,k])
    
    def Conj(self):
        return Quaternion([self.value[0],-self.value[1],-self.value[2],-self.value[3]])
    
    def Inv(self):
        real = (self.value[0])/((self.value[0])**2+(self.value[1])**2+(self.value[2])**2+(self.value[3])**2)
        i = (self.value[1])/((self.value[0])**2+(self.value[1])**2+(self.value[2])**2+(self.value[3])**2)
        j = (self.value[2])/((self.value[0])**2+(self.value[1])**2+(self.value[2])**2+(self.value[3])**2)              
        k = (self.value[3])/((self.value[0])**2+(self.value[1])**2+(self.value[2])**2+(self.value[3])**2)
        return Quaternion([real,-i,-j,-k])
    
    def Norm(self):
        temp=0
        for item in self.value:
            temp+=item**2
        return (temp)**0.5
    

z1 = Quaternion([1,-2,3,-4])
z2 = Quaternion([5,-6,7,-8])
z3 = Quaternion([-9,11,-16,9])
print(z1.value,z2.value,z3.value)

#z3z2
print(z3.Mul(z2).value)

#z1-z3
negative_z3= [0,0,0,0]
for i in range(4):
    negative_z3[i] = z3.value[i]*-1
print(z1.Add(Quaternion(negative_z3)).value)

#(z1*)z3
print(z1.Conj().Mul(z3).value)

#(z3)^-3
print(z3.Inv().Mul(z3.Inv().Mul(z3.Inv())).value)

#||z2||
print(z2.Norm())

#((z1^3)(z2*)(z3^-4)((z1+z3)^2))/((||z2||)(z1+z2))
_3_z1 = Quaternion(z1.Mul(z1.Mul(z1)).value)
conj_z2 = Quaternion(z2.Conj().value)
_4_of_z3 = Quaternion(z3.Inv().Mul(z3.Inv().Mul(z3.Inv().Mul(z3.Inv()))).value)
z1_plus_z2 = Quaternion(z1.Add(z2).value)
z1_plus_z3 = Quaternion(z1.Add(z3).value)
suare_of_z1_plus_z3 = Quaternion(z1_plus_z3.Mul(z1_plus_z3).value)

Dividend = Quaternion(_3_z1.Mul(conj_z2.Mul(_4_of_z3).Mul(suare_of_z1_plus_z3)).value)
Divisor = z1_plus_z2
for i in range(len(Divisor.value)):
    Divisor.value[i] *= z2.Norm()
    print(Divisor.value)

print(Dividend.Mul(Divisor.Inv()).value)