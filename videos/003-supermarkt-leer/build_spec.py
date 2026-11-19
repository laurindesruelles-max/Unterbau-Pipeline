import json
def S(img,part,w,move="push",fx=None,atmo=None,off=0.0,**k):
    d={"img":img,"at":[part,w,off] if off else [part,w],"move":move,"fx":fx or []}
    if atmo: d["atmo"]=atmo
    d.update(k); return d
def X(a,b,part,w,rev,move="push",fx=None,wl=0.35,off=0.0):
    return {"xsection":[a,b],"at":[part,w,off] if off else [part,w],"reveal":rev,"reveal_dur":1.6,"waterline":wl,"move":move,"fx":fx or [],"fx_in":["fog"]}
shots=[
 S("01",1,"Dein","push",["wet"],"dust",-0.4),
 S("02",1,"Und heute Nacht","rise",["wet"]),
 S("04",1,"Wie lange","push",[],"dust"),
 S("03",1,"Fünf Uhr","left",["wet","fog"]),
 X("06","06b",1,"Drinnen räumt",[1,"Im Lager dahinter",-0.3],"push",["wet"],0.2),
 S("05",1,"Wir gehen","right",[],"dust"),
 S("07",1,"Das ist ein","push",["fog","wet"],"dust"),
 S("08",2,"Um","push",["fog"],"snow"),
 S("09",3,"Ihr","right",["wet"]),
 S("11",3,"Ziel","orbit",["fog"]),
 S("13",3,"Dort kommt sie","push",[]),
 S("10",3,"Dann geht es","push",["cars"]),
 S("12",3,"Das ist kein","push",[],"dust"),
 S("14",3,"In Deutschland werden","left",["cars"]),
 S("15",3,"Allein die","orbit",[]),
 S("16",3,"Jetzt kommt der","push",["wet"]),
 S("05",3,"Und der Handel","right",[],"dust"),
 S("17",3,"Die Ware steht","push",[],"dust"),
 S("18",3,"Selbst in den","rise",["fog"],"snow"),
 S("11",3,"Das System ist","orbit",["fog"]),
 S("03",3,"Zurück an der","pull",["wet","fog"]),
 S("19",3,"Der Laden öffnet","push",["rays"],"dust"),
 S("20",4,"Klingt","push",["fog"]),
 S("21",4,"Nach wenigen","left",["wet"]),
 S("22",4,"Dann trifft es","push",[]),
 S("23",4,"Andere Ketten","right",[],"dust"),
 S("50",4,"Danach arbeitet","pull",["fog"]),
 S("24",4,"Im Herbst","push",["wet"],"rain"),
 S("21",4,"Tankstellen laufen","right",["wet"]),
 S("24",4,"Rund hundert","pull",["wet"],"rain"),
 S("25",4,"Und Deutschland","push",[],"dust"),
 S("26",4,"Die Regierung hebt","left",["cars","rays"]),
 S("27",4,"Zwei Jahre später","right",[]),
 S("28",4,"Teile der","push",[],"dust"),
 S("29",4,"Vier Fälle","push",[]),
 S("30",5,"Am einen Ende","rise",["screens"]),
 S("22",5,"Von zehn Euro","left",[]),
 S("31",5,"Am anderen Ende","push",["wet"],"rain"),
 S("32",5,"Zwei von fünf","push",["rays"]),
 S("33",5,"Der Branchenverband","left",["wet","fog"]),
 S("26",5,"Schon jetzt fährt","right",["cars"]),
 S("34",5,"Und hier wird","push",[],"dust"),
 S("29",5,"Spedition","push",[]),
 S("57",5,"Wie das im","orbit",[]),
 S("35",5,"Über sechzig","right",[]),
 S("56",5,"Ihr Vorwurf","push",[],"dust"),
 S("35",5,"Sie streiken","pull",[]),
 S("36",5,"Im Sommer","push",[],"dust"),
 S("37",5,"Das ist das","push",["rays"],"dust"),
 S("02",5,"Und genau diese","pull",["wet"]),
 S("38",6,"Tag eins","push",[]),
 S("39",6,"Gleichzeitig","right",[],"dust"),
 S("40",6,"Für Kliniken","push",[]),
 S("41",6,"Tag zwei","left",["wet","fog"]),
 S("42",6,"Dabei ist genug","orbit",["fog"]),
 S("10",6,"Zur Tankstelle","push",["cars"]),
 S("43",6,"Der Müll","push",["wet"],"rain"),
 S("44",6,"So steht es","push",["wet"],"rain"),
 S("45",6,"Tag drei","push",[],"dust"),
 S("18",6,"Eine Studie","pull",["fog"],"snow"),
 S("45",6,"Zwei Szenarien","pull",[],"dust"),
 X("46","47",6,"Aber dafür hat",[6,"Reis",-0.2],"push",["fog"],0.15),
 S("47",6,"Sie liegt in","pull",["fog"]),
 S("48",6,"Bleibt eine","right",["wet"]),
 S("07",6,"Zum zweiten Mal","push",["fog","wet"],"dust"),
 S("49",6,"Und in Woche","left",["fog"]),
 S("50",7,"Hier halten","push",["rays","fog"]),
 S("11",7,"Ein Gesetz","orbit",["fog"]),
 S("21",7,"Aber Großbritannien","right",["wet"]),
 S("51",7,"Und was heißt","push",["rays"],"dust"),
 S("52",7,"Pro Person","push",[]),
 S("14",7,"Kein Grund","left",["cars"]),
 X("54","55",7,"Heute Nacht",[7,"Am Steuer",-0.2],"push",["wet"],0.2),
 S("53",7,"Jetzt weißt","push",["wet","fog"]),
]
ov=[]
def B(part,w,l1,l2,dur=3.6,off=0.0): ov.append({"type":"bauchbinde","lines":[l1,l2],"at":[part,w,off] if off else [part,w],"dur":dur})
def Z(part,w,big,sub,dur=3.4,off=0.0): ov.append({"type":"zahl","big":big,"sub":sub,"at":[part,w,off] if off else [part,w],"dur":dur})
def H(part,w,t,dur=4.0): ov.append({"type":"hinweis","text":t,"at":[part,w],"dur":dur})
H(1,"Das ist ein","Gedankenexperiment",4.6)
ov.append({"type":"videotitel","lines":["Warum dein Supermarkt","nach 3 Tagen leer wäre"],"at":[2,"Um"],"dur":4.0})
Z(3,"vierzig Milliarden","40 Mrd. km","Maut-Lkw pro Jahr")
B(3,"Eine Studie","Studie für den Bundestag (TAB)","kaum Lagerflächen in den Filialen",4.0)
Z(3,"vier Tage","4 Tage","Frischware im Lager (Stand 2005)")
Z(4,"drei von vier","3 von 4","Tankstellen ohne Sprit")
Z(4,"die Hälfte","+50 %","Absatz in zwei Tagen")
B(4,"Im Herbst","Großbritannien, Herbst 2021","Fahrermangel – die Armee fährt Tanklaster",4.0)
Z(4,"Dazu kommen","5.000","Kurzzeit-Visa für Fahrer")
B(4,"Zeitweise","Deutschland, März 2020","Mehl: bis +192 % Absatz",3.8)
Z(5,"fünfundachtzig","> 85 %","Lebensmittelhandel: vier Gruppen")
B(5,"Es sind","Bundeskartellamt","Edeka · Rewe · Schwarz-Gruppe · Aldi",3.8)
Z(5,"siebzigtausend","> 70.000","fehlende Fahrer (Schätzung BGL)")
Z(5,"jeden zweiten","≈ 50 %","der Maut-km: Lkw aus dem Ausland")
H(5,"Gräfenhausen","Szene nachgestellt",34.0)
B(5,"Gräfenhausen","Gräfenhausen (Hessen), Frühjahr 2023","über 60 Fahrer streiken",4.0)
Z(5,"hunderttausend","≈ 100.000 €","Lohnforderung zuletzt")
B(5,"Im Sommer","Sommer 2023","rund 80 Fahrer, ca. 30 im Hungerstreik",4.0)
H(6,"Tag eins","Gedankenexperiment",4.0)
Z(6,"vierzehntausend","> 14.000","Tankstellen in Deutschland")
Z(6,"neunzig Tage","90 Tage","Erdölvorrat (Importe)")
Z(6,"zwei bis fünf","2–5 Tage","bis die Regale leer sind")
Z(6,"rund drei Tagen","≈ 3 Tage","dann wäre dein Supermarkt leer",3.8)
Z(6,"hundertfünfzig","> 150","geheime Lager der Notreserve")
B(7,"Ein Gesetz","Gesetz von 2017 (ESVG)","Transporte anfordern · Höchstmengen",4.0)
Z(7,"zehn Tage","10 Tage","Vorrat (Empfehlung BBK)")
Z(7,"zwanzig Liter","20 Liter","Wasser pro Person für 10 Tage")

DE=[5.6,47.1,15.3,55.1]; EU=[-11.0,35.0,21.0,59.5]
HH=(9.99,53.55); HAN=(9.73,52.37); KS=(9.48,51.31); F=(8.68,50.11); S=(9.18,48.78); MUC=(11.58,48.14); DO=(7.47,51.51); K=(6.96,50.94); B=(13.40,52.52); L=(12.37,51.34); N=(11.08,49.45)
ov.append({"type":"ablauf","at":[3,"Ihr"],"dur":19.5,"steps":[["Molkerei",[3,"Molkerei."]],["Lkw",[3,"Lkw"]],["Zentrallager",[3,"Zentrallager"]],["Lkw",[3,"nächsten"]],["Filiale",[3,"Rampe."]],["Regal",[3,"Regal."]]]})
ov.append({"type":"karte","at":[3,"In Deutschland werden"],"dur":5.2,"view":DE,"hl":["DE"],"title":"Hauptrouten (Schema)","pins":[[9.99,53.55,""],[13.40,52.52,""],[11.58,48.14,""],[8.68,50.11,""],[6.96,50.94,""]],"routes":[[HH,HAN,KS,F,S,MUC],[DO,K,F],[HH,B],[B,L,N,MUC],[DO,HAN,B]]})
ov.append({"type":"balken","at":[3,"Fast vier"],"dur":4.2,"title":"So reisen Güter in Deutschland (2024)","bars":[["Lkw",79,"%"],["alle anderen",21,"%"]],"quelle":"Quelle: Destatis, Anteil an der Gütermenge"})
ov.append({"type":"zaehler","at":[3,"Das sind jeden"],"dur":5.6,"to":9100000,"unit":"t","sub":"Güter pro Tag per Lkw · ≈ 900 Eiffeltürme","quelle":"eigene Rechnung nach Destatis 2024"})
ov.append({"type":"karte","at":[4,"Großbritannien hat"],"dur":4.2,"view":EU,"hl":["GB"],"title":"Großbritannien, September 2000","pins":[[-1.5,53.0,"Raffinerien blockiert"]]})
ov.append({"type":"karte","at":[4,"Und Deutschland?"],"dur":3.2,"view":EU,"hl":["DE"],"title":"Deutschland, März 2020","pins":[[10.4,51.2,"Hamsterkäufe"]]})
ov.append({"type":"karte","at":[4,"Zwei Jahre später"],"dur":4.0,"view":EU,"hl":["ES"],"title":"Spanien, März 2022","pins":[[-3.7,40.4,"Lkw-Streik, rund 3 Wochen"]]})
ov.append({"type":"balken","at":[5,"Zwei von fünf"],"dur":5.5,"title":"Anteil 55 Jahre und älter","bars":[["Lkw-Fahrer",39,"%"],["alle Berufe",25,"%"]],"quelle":"Quelle: Destatis, Mikrozensus 2023"})
ov.append({"type":"ablauf","at":[5,"Denn zwischen"],"dur":16.0,"steps":[["Auftraggeber",[5,"Auftraggeber"]],["Spedition",[5,"Spedition,"]],["Subunternehmer",[5,"Subunternehmer,"]],["dessen Sub",[5,"dessen"]],["Fahrer",[5,"unten"]]]})
ov.append({"type":"karte","at":[5,"Wie das im"],"dur":5.0,"view":DE,"hl":["DE"],"title":"Frühjahr 2023","pins":[[8.66,49.93,"Rastplatz Gräfenhausen"]]})
ov.append({"type":"tage","at":[6,"Tag eins"],"dur":6.0,"n":1,"items":["Frisches fehlt","Apotheken werden knapp"]})
ov.append({"type":"tage","at":[6,"Tag zwei"],"dur":6.5,"n":2,"items":["erste Tankstellen leer","Müll bleibt liegen","Geldautomaten leer"]})
ov.append({"type":"tage","at":[6,"Tag drei"],"dur":5.0,"n":3,"items":["Regale leer – überall"]})
ov.append({"type":"ablauf","at":[6,"Bleibt eine"],"dur":13.0,"steps":[["Notreserve",[6,"Bleibt"]],["über 150 Lager",[6,"Wie"]],["Lkw",[6,"Verteilt"]],["Menschen",[6,"Verteilt",0.6]]],"break":[2,[6,"Zum zweiten"]]})
for o in ov:
    if o["type"]=="bauchbinde" and o["lines"][1]=="": o["lines"]=o["lines"][:1]
spec={"titel":"Warum dein Supermarkt nach 3 Tagen leer wäre","lead":0.4,"tail":2.0,"cut":3.4,
 "parts":[{"id":1,"audio":"audio/1.mp3","words":"words/w1.json","gap_after":5.4},
          {"id":2,"audio":"audio/2.mp3","words":"words/w2.json","gap_after":0.6},
          {"chapter":{"n":1,"title":"Die Kette in der Nacht","pause":4.5}},
          {"id":3,"audio":"audio/3.mp3","words":"words/w3.json","gap_after":0.6},
          {"chapter":{"n":2,"title":"Es ist schon passiert","pause":4.5}},
          {"id":4,"audio":"audio/4.mp3","words":"words/w4.json","gap_after":0.6},
          {"chapter":{"n":3,"title":"Wer die Kette hält","pause":4.5}},
          {"id":5,"audio":"audio/5.mp3","words":"words/w5.json","gap_after":0.6},
          {"chapter":{"n":4,"title":"Tag drei","pause":4.5}},
          {"id":6,"audio":"audio/6.mp3","words":"words/w6.json","gap_after":0.6},
          {"chapter":{"n":5,"title":"Was bleibt","pause":4.5}},
          {"id":7,"audio":"audio/7.mp3","words":"words/w7.json","gap_after":0.4}],
 "shots":shots,
 "title":{"at":[1,"END",0.6],"dur":4.6,"claim":"Verstehen, wie die Welt funktioniert"},
 "overlays":ov,
 "sfx":[[[1,"Im Lager dahinter",-2.0],"ub_riser",0.6],[[1,"Im Lager dahinter",0.0],"ub_whoosh",0.5],
        [[1,"END",0.1],"ub_drop",0.8],[[1,"END",0.6],"ub_hit",0.6],
        [[6,"Reis",-2.0],"ub_riser",0.6],[[6,"Reis",0.0],"ub_whoosh",0.5],
        [[6,"Verteilt wird",-0.1],"ub_drop",0.6],[[3,"In Deutschland werden",0.2],"car_pass",0.35],[[5,"Schon jetzt fährt",0.1],"car_pass_2",0.35],[[7,"Kein Grund",0.1],"car_pass",0.3],
        [[7,"Am Steuer",-1.8],"ub_riser",0.5],[[7,"Am Steuer",0.0],"ub_whoosh",0.45]],
 "amb":[
  [[1,"Dein",-0.4],[1,"Drinnen räumt"],"amb_night",0.35],
  [[1,"Drinnen räumt"],[1,"Das ist ein"],"amb_factory",0.25],
  
  [[4,"Klingt"],[4,"Nach wenigen"],"amb_night",0.3],
  [[4,"Dann trifft es"],[4,"Andere Ketten"],"amb_market",0.3],
  [[4,"Im Herbst"],[4,"Und Deutschland"],"amb_rain",0.3],
  [[5,"Am anderen Ende"],[5,"Zwei von fünf"],"amb_rain",0.3],
  [[5,"Der Branchenverband"],[5,"Und hier wird"],"amb_night",0.3],
  [[6,"Tag eins"],[6,"Gleichzeitig"],"amb_market",0.3],
  [[6,"Der Müll"],[6,"Tag drei"],"amb_rain",0.3],
  [[6,"Tag drei"],[6,"Aber dafür hat"],"amb_factory",0.2],
  [[7,"Heute Nacht"],[7,"END",1.5],"amb_night",0.3]
 ],
 "music":{"file":"music/ub_kaltstart_meer.mp3","mode":"dramaturgie",
          "chapters":["ub_kaltstart_meer","ub_system_puls","ub_ausfall_dunkel","ub_system_puls","ub_spannung_aufbau","ub_aufloesung_weit"]}}
json.dump(spec,open("spec.json","w"),ensure_ascii=False,indent=1)
print(len(shots),"shots",len(ov),"overlays")
