10 rem lawn job - mike buhidar jr.
16 goto11000
17 dimp(15):p(1)=-40:p(2)=40:p(4)=-1:p(8)=1
20 rn=0:sc=0:co=54272:hc=0:gosub2000:gosub200:ti$="000000":gosub300
120 bo=128:bc=13:pe=peek(56320):jv=15-(peand15)
125 ifp=5thensc=sc+.050001:sc$=str$(sc):sc$=mid$(sc$,2,4)
127 printtab(10);sc$;tab(32);mid$(ti$,3,2)":";right$(ti$,2)"{up}"
130 pp=op+p(jv):dn=peek(pp):p=peek(pp+co)and15:ifdn<>128then400
137 ifjv=0orjv=5orjv=6orjv=9orjv=10then120
140 pokeop,io:pokeop+co,ic:pokepp+co,1:pokepp,jv+130:op=pp
145 io=bo:ic=bc
150 goto120
200 rem sound init.
203 op=1843:pokeop,131:pokeop+co,1:io=32:ic=1
210 s=54272:fora=stos+24:pokea,0:next:pokes+24,15:pokes+5,63:pokes+6,255
220 pokes+4,65:pokes+3,10:pokes+2,255:return
300 rem start mower
305 print"{wht}"tab(32);mid$(ti$,3,2)":"right$(ti$,2):print"{up}{up}"
310 jv=peek(56320):fr=(jvand16):forit=0to250:next:iffr=16then305
315 yn=int(rnd(1)*6)+1:ifyn=1then340
320 fortt=2to0step-1:pokes+1,tt:forbb=255to0step-5:pokes,bb:pokes,0:next:next
330 pokes+1,0:goto305
340 forcc=1to3:pokes+1,cc:forhh=0to100:next:next:return
400 rem collision
410 ifdn=130then500
420 ifdn=129then520
430 ifdn=133and(peand16)<>16then540
450 goto120
500 rem hit rock
505 forbc=15to0step-1:poke53280,bc:next
510 pokeop,jv+130:forb=4to0step-.05:pokes+1,b:next:rn=rn+1:gosub300:goto120
520 rem walk on sidewalk
530 bo=129:bc=15:goto137
540 rem check for complete job
545 ll=0:print"{up}{up}{up}         looking over your work."
546 forgg=1to0:pokes+1,gg:foryy=255to0step-1:pokes,yy:next:next:pokes+1,0
550 forv=1024to2023:pv=peek(v+co)and15:gosub560:next
552 ifll=mmthen600
555 print"{up}     you have not finished the job!"
556 forg=0to3000:next:print"{up}                                       {down}{down}"
558 gosub300:goto120
560 ifpv=5thenll=ll+1
570 return
600 rem end of game
605 fs=val(sc$)-val(ti$)/100-.50*rn:iffs>hsthenhs=fs
610 pokes+1,0:poke53281,0:print"{clr}{wht}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}"
615 iffs<0then700
620 printtab(6)"great job, you earned $";fs
625 print:printtab(10)"highest earning $";hs
630 print"{down}{down}{down}{down}{down}{down}{down}{down}{cyn}";:printtab(8)"press trigger to play again"
640 aa=peek(56320)and16:ifaa=0then20
650 goto640
700 print"{up} your expenses outweighed your earning!"
710 printtab(5)"find another way to earn money!":goto630
2000 rem initialazation of screen
2003 poke53281,0:poke53280,0:poke53265,peek(53265)and239
2005 print"{clr}{wht}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}{down}":printtab(2)"score:  0"tab(25)"time:  ";
2010 poke53281,5:poke53280,0:poke53281,9
2015 forb5=1464to1783:pokeb5,128:pokeb5+co,5:next
2016 forc2=1247to1447step40:pokec2,128:pokec2+co,5:next
2017 forc3=1248to1448step40:pokec3,128:pokec3+co,5:next
2018 forc4=1249to1449step40:pokec4,128:pokec4+co,5:next
2019 forc5=1250to1450step40:pokec5,128:pokec5+co,5:next
2020 forc6=1310to1326:pokec6,128:pokec6+co,5:next
2021 forc7=1350to1366:pokec7,128:pokec7+co,5:next
2022 forc8=1390to1406:pokec8,128:pokec8+co,5:next
2023 forc9=1430to1446:pokec9,128:pokec9+co,5:next
2029 fora1=1864to1903:pokea1,69:pokea1+co,0:next
2030 fora2=1784to1823:pokea2,129:pokea2+co,15:next
2040 fora3=1323to1801step40:pokea3,129:pokea3+co,15:next
2050 fora4=1324to1328:pokea4,129:pokea4+co,15:next
2060 poke1288,129:poke1288+co,15:forz1=1247to1250:pokez1,133:pokez1+co,12:next
2070 fora5=1028to1148step40:pokea5,116:pokea5+co,hc:next
2080 poke1188,76:poke1188+co,hc
2090 fora6=1189to1210:pokea6,111:pokea6+co,hc:next
3000 fora7=1251to1451step40:pokea7,116:pokea7+co,hc:next
3010 fora8=1211to1055step-39:pokea8,78:pokea8+co,hc:next
3020 fora9=1492to1499:pokea9,111:pokea9+co,hc:next
3030 poke1491,76:poke1491+co,hc:poke1496,76:poke1496+co,hc
3040 forb1=1056to1456step40:pokeb1,116:pokeb1+co,hc:next
3050 poke1500,122:poke1500+co,hc
3060 forb2=1060to1460step40:pokeb2,106:pokeb2+co,hc:next
3070 forb3=1271to1285:pokeb3,67:pokeb3+co,12:next
3080 poke1270,74:poke1270+co,12:poke1286,75:poke1286+co,12
3090 poke1230,93:poke1230+co,12:poke1246,93:poke1246+co,12
3100 forb4=1231to1245step2:pokeb4,135:pokeb4+co,7:next
3110 forb6=1024to1424step40:pokeb6,128:pokeb6+co,5:next
3120 forb7=1025to1425step40:pokeb7,128:pokeb7+co,5:next
3130 forb8=1026to1426step40:pokeb8,128:pokeb8+co,5:next
3140 forb9=1027to1427step40:pokeb9,128:pokeb9+co,5:next
3150 forb9=1228to1428step40:pokeb9,128:pokeb9+co,5:next
3160 forc1=1229to1429step40:pokec1,128:pokec1+co,5:next
3170 ford1=1061to1461step40:poked1,128:poked1+co,5:next
3180 ford2=1062to1462step40:poked2,128:poked2+co,5:next
3190 ford3=1063to1463step40:poked3,128:poked3+co,5:next
3195 fore1=1024to1744step40:pokee1,72:pokee1+co,1:next
3197 fore2=1063to1783step40:pokee2,71:pokee2+co,1:next
3199 mm=int(rnd(1)*10)+10
3200 fortt=1tomm
3210 rp=int(rnd(1)*1000)+1024
3220 ifpeek(rp)<>128then3210
3221 ifpeek(rp-1)=130then3210
3222 ifpeek(rp+1)=130then3210
3223 ifpeek(rp+39)=130then3210
3224 ifpeek(rp+41)=130then3210
3225 ifpeek(rp-41)=130then3210
3226 ifpeek(rp-39)=130then3210
3230 pokerp,130:nexttt
4000 poke53265,peek(53265)or16
9999 return
11000 rem redefine characters
11001 ifpeek(12288)=60then11045
11004 poke53280,0:poke53281,0:print"{clr}"
11005 printtab(16)"{lgrn}{down}{down}{down}{down}{down}{down}{down}{down}lawn job":printtab(19)"{wht}{down}by"
11006 printtab(12)"{down}mike buhidar jr."
11007 print"{cyn}{down}{down}{down}{down}{down}{down}{down}{down}redefining characters, please wait..."
11010 printchr$(142):poke52,48:poke56,48:clr:poke56334,peek(56334)and254
11020 poke1,peek(1)and251
11025 forch=0to1023:pokech+12288,peek(ch+53248):next
11030 forcd=0to87:readd:pokecd+13312,d:next
11040 poke1,peek(1)or4:poke56334,peek(56334)or1
11045 poke53272,(peek(53272)and240)+12
11050 goto17
12000 rem data for characters
12010 data173,255,219,254,183,253,111,255
12020 data255,255,255,255,255,255,255,255
12030 data255,239,231,227,195,193,126,255
12040 data255,231,231,189,36,126,102,60
12050 data60,102,126,36,189,231,231,255
12060 data255,255,255,255,255,255,255,255
12070 data240,230,255,149,149,255,230,240
12080 data0,28,54,28,8,42,28,0
12090 data0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
12110 data15,103,255,169,169,255,103,15
