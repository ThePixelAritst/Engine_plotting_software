import file_manager as fm

file = fm.File(False)
file.write(("mega stinky",0))
file.write(("not stinky",0))

for x in range(20):
    file.write((x,x*2,x**2))

file.write(("stink test",))