* Erick Jones
* Graduate Program in Operations Research and Industrial Engineering
* The University of Texas at Austin

* Water_Energy run file

* Load database

* Default instance: the synthetic one shipped in data/raw/. See README.
* The restricted workbooks are not distributed; override with --nin=<name> to use them.
$if not set nin $set nin ../data/raw/indata-synthetic

$call GDXXRW input=%nin%.xlsx output=indatamod.gdx index=index!A1

*$call GDXXRW input=indata_%inp%.xlsx output=indatamod.gdx index=index!A1


$include Water_Energy_Model_mod.gms
$include Water_Energy_Equations_mod.gms


*Intial Solutions

Purchase.L(WUTIL) = h*b;
Purchase.L(EUTIL) = h*b;


*$ontext
Purchase.fx('U_H2O1')=h*b;
Purchase.fx('U_H2O2')=h*b;
Purchase.fx('U_ELC1')=h*b;



Purchase.up('H_PV') = 0;
Purchase.up('H_BAT') = 0;

*Purchase.lo('H_RW') = 1000;
*Purchase.lo('H_RWTANK') = 1000;
*Purchase.lo('H_GW') = 900;


Purchase.up('C_PV') = 1;
Purchase.up('C_WND') = 1;
Purchase.up('C_BAT') = 1;
Purchase.up('C_HB') = 0;
Purchase.up('C_VRF') = 5;

Purchase.fx('C_RWTANK') = 0;
Purchase.fx('C_GW') = 0;
Purchase.fx('C_SW') = 0;


PurchaseEUTIL.L(EUTIL,HOUSE) = 1;
PurchaseWUTIL.L(WUTIL,HOUSE) = 1;
PurchaseEUTIL.fx('U_ELC1',HOUSE) = 1;

PurchaseWUTIL.fx('U_H2O1',HOUSE) = 1;
PurchaseWUTIL.fx('U_H2O2',HOUSE) = 1;

*$offtext






*For Water Only Solutions
*Purchase.fx(BAT) = 0;
*Purchase.fx(ETECH) = 0;
*ProducedElectricity.fx(ETECH,l,m) = 0;



*For Electricity Only Solutions
Purchase.fx(TANK) = 0;
Purchase.fx(WTECH) = 0;
ProducedWhiteWater.fx(WTECH,l,m) = 0;
ProducedGreyWater.fx(WTECH,l,m) = 0;

*Technology Only Solutions
$ontext

*Purchase.fx('U_H2O5')=0;
Purchase.fx('U_ELC5')=0;

*Purchase.fx('U_H2O4')=0;
Purchase.fx('U_ELC4')=0;

*Purchase.fx('U_H2O3')=0;
Purchase.fx('U_ELC3')=0;

Purchase.fx('U_ELC2')=0;
*Purchase.fx('U_H2O2')=0;

*Purchase.fx('U_ELC1')=0;
*Purchase.fx('U_H2O1')=0;

*Equation UtilLimit1(month);
*UtilLimit1(m).. sum((l,EUTIL),ProducedElectricity(EUTIL,l,m)) =l= 500*h*b;

Equation UtilLimit2(month);
UtilLimit2(m).. sum((l,WUTIL),ProducedWhiteWater(WUTIL,l,m)) =l= 21000*h*b;

$offtext


*For Indivudual Runs
$ontext
Purchase.fx('C_GW') = 0;
Purchase.fx('C_VRF') = 0;
Purchase.fx('C_SW') =0;
Purchase.fx('C_PV') = 0;
Purchase.fx('C_WND') = 0;
Purchase.fx('C_HB') = 0;
Purchase.fx('C_RWTANK')=0;
Purchase.fx('C_BAT')=0;
$offtext















Model program / all /;









option solprint=on, resLim=100000, optcr = 0.05, optca = 1000,  mip = cplex, threads = 6 ;

$onecho > cplex.opt
mipsearch 1
$offecho

program.optfile = 1;







solve program using mip min z;


$include ResultsWE1_mod.gms

*display z1.l, z2.l, z3.l, z.l, h, Purchase.l, InstalledCapacity.l, WWProductionByTechnology, GWProductionByTechnology, ELCProductionByTechnology,
*ELCFraction, WaterFraction, TankStorageLevel, BatteryStorageLevel, WWEnergyConsumption, GWEnergyConsumption, BATEnergyconsumption;

$onEcho > howtowrite.txt

*Objective Values and other 1 value parameters
var = z1.l rng=Results!C3
var = z2.l rng=Results!C4
var = z3.l rng=Results!C5
var = z4.l rng=Results!C6
par = h rng=Results!C8
par = b rng=Results!C9
par = ELCFraction rng=Results!C11
par = WaterFraction rng=Results!C12





*Decision to Purchase and Installed Capacity

squeeze = n var = InstalledCapacity.l rng=Results!F3

squeeze = n par = ELCFractionm rng=Results!F8

squeeze =n par = WaterFractionm rng=Results!F13




squeeze = n var = Purchase.l rng=Results!F18

*squeeze =n var = Purchasem.l rng=Results!F23

squeeze = n par = ELCProductionByTechnology rng=Results!F28

squeeze = n par = WWProductionByTechnology rng=Results!F48

squeeze = n par = GWProductionByTechnology rng=Results!F68


squeeze = n par = CurtailmentELCm rng=Results!F78

squeeze = n par = CurtailmentWaterm rng=Results!F88

squeeze = n par = StorageLoss1 rng=Results!F98

squeeze = n par = StorageLoss2 rng=Results!F102

*get rid of for individual runs



squeeze = n par = ActualDemand rng=Results!F108

*For hourly data runs

squeeze = n par = HourlyELC rng=Results!F120

squeeze = n par = HourlyWW rng=Results!F10120

squeeze = n par = HourlyGW.l rng=Results!F20120

squeeze = n par = HourlyDemand rng=Results!F30120



*squeeze = n par = WWEnergyConsumption rng=Results!F78

*squeeze = n par = GWEnergyConsumption rng=Results!F88

*squeeze = n par = BATEnergyConsumption rng=Results!F98







$offEcho

execute 'gdxxrw ResultsWE_mod.gdx output=%nin%.xlsx @howtowrite.txt';

*execute 'gdxxrw ResultsWE_mod.gdx output=indata_%inp%.xlsx @howtowrite.txt';

*execute 'gdxxrw ResultsWE.gdx output=indata.xlsx squeeze = n var = z1.l rng=Results!C3 var=z2.l rng=Results!C4 var=z3.l rng=Results!C5 var = z.l rng=Results!C6';








