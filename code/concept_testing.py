import file_manager as fm

file = fm.File(False)
file.write(("mega stinky",0))
print(file.read_row(0))
file.write(())