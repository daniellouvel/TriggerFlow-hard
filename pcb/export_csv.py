from place import *
import render as Rd, re
newv={"U121":"LM2596S-ADJ","L121":"33uH 4,25A","D121":"SS54","C129":"10uF","C122":"10uF","C123":"100nF","C124":"330uF","C125":"100nF","C126":"470uF","C127":"100nF",
 "R121":"1kΩ 1%","R122":"3.9kΩ 1%","R123":"10kΩ","R124":"10kΩ","R125":"220Ω","U122":"SN74AHCT1G125","D122":"PESD5V0S1BB","J121":"servo 1x3",
 "K131":"HF32F/012-ZS3","Q131":"AO3400A","D131":"SS14","R131":"220Ω","R132":"100kΩ","J131":"bornier 3P 5,08"}
names={"ana":"Entrées capteur","iso":"Sorties isolées","pwr":"Puissance","esp":"ESP32 / 3V3","i2c":"Bus I2C"}
def k(r):
    m=re.match(r"([A-Z]+)(\d+)",r); return (m.group(1),int(m.group(2)))
with open("placement_TriggerFlow.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f,delimiter=";")
    w.writerow(["Ref","Valeur","Empreinte","X_mm","Y_mm","Rotation","Face","Bloc"])
    for r in sorted(P,key=k):
        x,y,rot=P[r]; v=newv.get(r, vals.get(r,"")).replace("{Value}","")
        w.writerow([r,v,comps[r],f"{x:.2f}".replace(".",","),f"{y:.2f}".replace(".",","),rot,"Dessus",names[Rd.block(r)]])
    for h,(hx,hy,kind) in HOLES.items(): w.writerow([h,"M3 "+kind,"MountingHole_3.2mm",str(hx),str(hy),0,"—","Mécanique"])
print("ok")
