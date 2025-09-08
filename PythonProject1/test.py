list=[1,2,3,4];
list_new=list[1:2]
print(id(list_new))
print(id(list))

a=", "
print(id(a))
result=a.join(["1","2","3"])
id(result)
t=(1,[1,2,3],5)
print(id(t))
t[1][2]=6
print(id(t))
