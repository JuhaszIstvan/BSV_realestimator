## MI EZ?
Egy egyszerű script, ami:
1. a hirdetésazonosító számokat növelve lekérdezi az ingatlan.com egyes hirdetéseit
1. Parsolja a html stringet.
1. A visszakapott értékek alapján leszűri a keresett hirdetéseket
1. A talált hirdetéseket elküldi a kívánt email címre, Illetve másodpéldányt küld az ellenőrző emailcímre.
1. A találatokat elmenti egy sqlite adtbázisba

## MIT TUD?

1. Megkeresi az adatbázisból a legutóbbi sikeres letöltés számát s onnan folytatja
1. Az előre meghatározott batch méretig, kivéve ha 10-nél több 404 errorba fut, ekkor a scraper megáll.
1. UAT és PROD környezetek ugyanazon a scripten. 


## TELEPÍTÉS WINDOWSRA
1. Szerezz egy git klienst pl innen: https://git-scm.com/downloads 
2. Töltsd le a scriptet egy tetszőleges könyvtárba (itt:C:\src\BSV_realestimator) 

pl git cmd-ben:
```
md C:\src
cd C:\src\
git clone git@github.com:JuhaszIstvan/BSV_realestimator.git
```

### Hozd létre a python virtuális environmentet
1. Töltsd le s telepítsd a legújabb miniconda verziót https://docs.conda.io/en/latest/miniconda.html
1. Futtasd az anaconda prompton belül:
```
cd C:\src\BSV_realestimator
conda env create -f "C:\src\BSV_realestimator\scripts\bsv_realestimator.yml"
conda activate bsv_realestimator_env
```
A virtual environmentet ellenőrizheted a ```conda env list```
## CONFIGURÁCIÓ
Hozd létre a lenti tartalommal a  params.ini filet a scripts könyvtárban. Ebben a példában: C:\src\BSV_realestimator\scripts\params.ini. 
(PROD és a UAT environmentek között az -e PROD vagy -e UAT argumentummal lehet majd váltani.)
```
[DEFAULT]
[PROD]
sender_address = a_jelentes_kuldo_email_cime@gmail.com
sender_pass = a_jelentes_kuldo_gmail_API_kulcsa
receiver_address = a_jelentés_címzettjének@email.címe
bcc_address = bcc_címzett@gmail.com
outputfld = C:\temp\prod_kimenet_konyvtar

[UAT]
sender_address = a_jelentes_kuldo_email_cime@gmail.com
sender_pass = a_jelentes_kuldo_gmail_API_kulcsa
receiver_address = a_jelentés_címzettjének_teszt@email.címe
bcc_address = bcc_címzett@gmail.com
outputfld = C:\temp\dev_kimenet_konyvtar
```

## ELSŐ FUTTATÁS ELŐTT

A configuráció után futtasd le az anaconda prompt-ban a következő parancsokat:

```
conda activate bsv_realestimator_env
python C:\Users\eee\Dropbox\BSV_realestimator\scripts\setup.py
```

## FUTTATÁS
Vagy Anaconda prompton vagy powershellen vagy cmd.exe-n keresztül:
```
conda activate bsv_realestimator_env
python C:\Users\eee\Dropbox\BSV_realestimator\scripts\ingatlan_com.py -b 15 -s 0 -e UAT
```

```

## FUTTATÁSI PARAMÉTEREK
```
USAGE:          ingatlan_com.py 
                    -e, --env <environment UAT|PROD|DEV>
                    -s, --start to set the first posting to check, 0 will check the latest in the db
                    -b, --bsize to set how far should the script count upwards Default is 4000
                    -h for help''
```
