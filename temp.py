class A:
    a = 0
    def __init__(self):
        a = 1
        
    def __str__(self):
        return str(self.a)    

print (A())    