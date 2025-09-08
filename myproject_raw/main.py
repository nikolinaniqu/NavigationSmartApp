from mypackage.stuff import packE
from mypackage import *
from mypackage.stuff import *
from mymoduls import modA,modB

print(__name__)
packE.f_pack_E()
print(packD.f_pack_D())
packC.f_pack_C()
modA.f_mod_A()
modB.f_mod_B()
