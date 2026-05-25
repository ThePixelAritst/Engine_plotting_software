class outer():
    formatting = 2
    file = "dont mind me, just passing through"

    class inner_1():
        def write_as_1(custom):
            print("not stinky")
            print(outer.file)
            print(custom)

    class inner_2():
        def write_as_2(custom=None):
            print("stinky")
            print(outer.file)
            print(custom)

    def write(self,custom_text):
        available_calls = {1: self.inner_1.write_as_1,
                     2: self.inner_2.write_as_2}
        
        available_calls[self.formatting](custom_text)

bleh = outer()

test = (1)
print(type(test))
if type(test) == int:
    test = (test,)
    
for x in test:
    print(x)