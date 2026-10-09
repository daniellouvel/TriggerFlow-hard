from place import *
import render as Rd, re
newv={"U121":"LM2596S-ADJ","U122":"SN74AHCT1G125","RELAY121":"HF32F/012-ZS3","J121":"KF128-5.08-3P (servo)","J122":"KF128-5.08-3P (relais)",
 "Q121":"AO3400A","D121":"SS54","D122":"SS14","D123":"PESD5V0S1BB","D101":"SS14"}
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
