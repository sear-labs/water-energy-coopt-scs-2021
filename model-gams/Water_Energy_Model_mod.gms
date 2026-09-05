* Erick Jones
* Graduate Program in Operations Research and Industrial Engineering
* The University of Texas at Austin

* Energy and Water Optimization Model



*Multipliers that Can be Modified

Scalar b number of blocks /10/;

Scalar h number of households /32/;

Scalar ElectricityDemandMultiplier /1/;

Scalar WaterDemandMultiplier /1/;

*Set at 80% only 20% of water can be used for greywater needs
Scalar InsideDemand /0.7/;

Scalar GWRecoveryFactor /0.8/;

Scalar Roofsqft /1959/;


set MONTH / 1*12 /;
alias (m,MONTH);



set TECHNOLOGY

$GDXIN indatamod.gdx
$LOAD TECHNOLOGY
$GDXIN

* Water Technologies
*/ H_RW, H_GW, C_GW, C_SW, U_H2O,
*Energy Technologies
* H_PV, C_PV, C_WND, U_ELC,
*Storage Technolgies
*H_BAT, C_BAT, H_RWTANK, C_RWTANK/


WW(TECHNOLOGY) /H_RW, U_H2O1, U_H2O2, U_H2O3, U_H2O4, U_H2O5, C_VRF, H_RWTANK/
GW(TECHNOLOGY) /H_GW, C_SW, C_GW, C_RWTANK/
TANK(TECHNOLOGY) /H_RWTANK, C_RWTANK/
RW(TECHNOLOGY) /H_RW, C_SW/
ELC(TECHNOLOGY) /H_PV, C_PV, C_WND, U_ELC1, U_ELC2, U_ELC3, U_ELC4, U_ELC5, H_BAT, C_BAT, C_HB/
BAT(TECHNOLOGY) /H_BAT, C_BAT/
UTIL(TECHNOLOGY) /U_ELC1, U_ELC2, U_ELC3, U_ELC4, U_ELC5, U_H2O1, U_H2O2, U_H2O3, U_H2O4, U_H2O5/
WUTIL(TECHNOLOGY) /U_H2O1, U_H2O2, U_H2O3, U_H2O4, U_H2O5/
EUTIL(TECHNOLOGY) /U_ELC1, U_ELC2, U_ELC3, U_ELC4, U_ELC5/
ETECH(TECHNOLOGY) /H_PV, C_PV, C_WND, C_HB/
WTECH(TECHNOLOGY) /H_RW, C_GW, C_VRF, H_GW, C_SW/

alias (t,tt,TECHNOLOGY);


set TIMESLICE / WDA1*WDA120, WEA1*WEA48, WDB1*WDB120, WEB1*WEB48, WDC1*WDC120, WEC1*WEC48, WDD1*WDD120,
WED1*WED48, WEE1*WEE48, WDE1*WDE24 /

*Slice = 1 hour
*720 hours in a month

WeekdayNight(TIMESLICE) /WDA1*WDA7, WDA20*WDA31, WDA44*WDA55, WDA68*WDA79, WDA92*WDA103, WDA116*WDA120,
 WDB1*WDB7, WDB20*WDB31, WDB44*WDB55, WDB68*WDB79, WDB92*WDB103, WDB116*WDB120,
WDC1*WDC7, WDC20*WDC31, WDC44*WDC55, WDC68*WDC79, WDC92*WDC103, WDC116*WDC120,
WDD1*WDD7, WDD20*WDD31, WDD44*WDD55, WDD68*WDD79, WDD92*WDD103, WDD116*WDD120, WDE1*WDE7, WDE20*WDE24/

WeekdayDay(TIMESLICE) /WDA8*WDA19, WDA32*WDA43, WDA56*WDA67, WDA80*WDA91, WDA104*WDA115,
WDB8*WDB19, WDB32*WDB43, WDB56*WDB67, WDB80*WDB91, WDB104*WDB115,
WDC8*WDC19, WDC32*WDC43, WDC56*WDC67, WDC80*WDC91, WDC104*WDC115,
WDD8*WDD19, WDD32*WDD43, WDD56*WDD67, WDD80*WDD91, WDD104*WDD115, WDE8*WDE19 /

WeekendNight(TIMESLICE) /WEA1*WEA7, WEA20*WEA31, WEA44*WEA48,
WEB1*WEB7, WEB20*WEB31, WEB44*WEB48,
WEC1*WEC7, WEC20*WEC31, WEC44*WEC48,
WED1*WED7, WED20*WED31, WED44*WED48,
WEE1*WEE7, WEE20*WEE31, WEE44*WEE48/

WeekendDay(TIMESLICE) /WEA8*WEA19, WEA32*WEA43,
WEB8*WEB19, WEB32*WEB43,
WEC8*WEC19, WEC32*WEC43,
WED8*WED19, WED32*WED43,
WEE8*WEE19, WEE32*WEE43/

;

alias (l,ll,TIMESLICE);
* Summary of Set: TIMESLICE

set SEASON / WINTER, SPR_FALL, SUMMER/;
alias(ls,SEASON);

set FUEL / W, kWh, W_H2O, G_H2O, GAL /;
alias (f,FUEL);

set EMISSION / CO2 /;
alias (e,ee,EMISSION);
* Summary of Set: EMISSION
* CO2 = Carbon dioxide

set MODE_OF_OPERATION / 1, 2/;
alias (mo,MODE_OF_OPERATION);
* Summary of Set: MODE_OF_OPERATION
* 1 = Electricity generation
* 2 = Electricity consumption for storage (Charging)


set STORAGE /H_BAT, C_BAT, H_RWTANK, C_RWTANK/

BATT(STORAGE) /H_BAT, C_BAT/
TANKS(STORAGE) /H_RWTANK, C_RWTANK/;

alias (s,STORAGE);

set HOUSE /1*32/

alias(hh,HOUSE);

* ##### Parameters #####

* ##### Global #####



Parameter SpecifiedMonthlyDemand(FUEL,MONTH);
* Total monthly demand for demands that are timeslice-dependent
* Units: PJ (ELC, GAS), Millions Miles (VMT, PM)
* Data Source: See Data spreadsheet



$GDXIN indatamod.gdx
$LOAD SpecifiedMonthlyDemand
$GDXIN




SpecifiedMonthlyDemand('kWh',m) = SpecifiedMonthlyDemand('kWh',m)*b*ElectricityDemandMultiplier;
SpecifiedMonthlyDemand('GAL',m) = SpecifiedMonthlyDemand('GAL',m)*b*WaterDemandMultiplier;
SpecifiedMonthlyDemand('W_H2O',m) = SpecifiedMonthlyDemand('GAL',m)*InsideDemand;
SpecifiedMonthlyDemand('G_H2O',m) = SpecifiedMonthlyDemand('GAL',m)*(1-InsideDemand);

parameter HouseDemand(FUEL,HOUSE,MONTH);
* Fraction of the total monthly demand occurring in each timeslice
* Units: Fraction
* Data Source: See data spreadsheet


$GDXIN indatamod.gdx
$LOAD HouseDemand
$GDXIN



parameter SpecifiedDemandProfile(FUEL,TIMESLICE,MONTH);
* Fraction of the total monthly demand occurring in each timeslice
* Units: Fraction
* Data Source: See data spreadsheet


$GDXIN indatamod.gdx
$LOAD SpecifiedDemandProfile
$GDXIN


*Filling Out the Rest of the Timeslices

*SpecifiedDemandProfile('GAL', WeekdayDay, m) = SpecifiedDemandProfile('GAL','WDA1', m)/(20*12);
*SpecifiedDemandProfile('GAL', WeekdayNight, m) = SpecifiedDemandProfile('GAL','WDA8', m)/(20*12);
*SpecifiedDemandProfile('GAL', WeekendDay, m) = SpecifiedDemandProfile('GAL','WEA1', m)/(10*12);
*SpecifiedDemandProfile('GAL', WeekendNight, m) = SpecifiedDemandProfile('GAL','WEA8', m)/(10*12);
*
*SpecifiedDemandProfile('W_H2O', WeekdayDay, m) = SpecifiedDemandProfile('W_H2O','WDA1', m)/(20*12);
*SpecifiedDemandProfile('W_H2O', WeekdayNight, m) = SpecifiedDemandProfile('W_H2O','WDA8', m)/(20*12);
*SpecifiedDemandProfile('W_H2O', WeekendDay, m) = SpecifiedDemandProfile('W_H2O','WEA1', m)/(10*12);
*SpecifiedDemandProfile('W_H2O', WeekendNight, m) = SpecifiedDemandProfile('W_H2O','WEA8', m)/(10*12);
*
*SpecifiedDemandProfile('G_H2O', WeekdayDay, m) = SpecifiedDemandProfile('G_H2O','WDA1', m)/(20*12);
*SpecifiedDemandProfile('G_H2O', WeekdayNight, m) = SpecifiedDemandProfile('G_H2O','WDA8', m)/(20*12);
*SpecifiedDemandProfile('G_H2O', WeekendDay, m) = SpecifiedDemandProfile('G_H2O','WEA1', m)/(10*12);
*SpecifiedDemandProfile('G_H2O', WeekendNight, m) = SpecifiedDemandProfile('G_H2O','WEA8', m)/(10*12);
*
*
*
*SpecifiedDemandProfile('kWh', WeekdayDay, m) = SpecifiedDemandProfile('kWh','WDA1', m)/(20*12);
*SpecifiedDemandProfile('kWh', WeekdayNight, m) = SpecifiedDemandProfile('kWh','WDA8', m)/(20*12);
*SpecifiedDemandProfile('kWh', WeekendDay, m) = SpecifiedDemandProfile('kWh','WEA1', m)/(10*12);
*SpecifiedDemandProfile('kWh', WeekendNight, m) = SpecifiedDemandProfile('kWh','WEA8', m)/(10*12);






parameter CapacityFactor(TECHNOLOGY,TIMESLICE,MONTH);
* Maximum fraction of time a technology can run in a given timeslice
* Units: Fraction
* Data Source: ATX Hourly Wind Generation 2015 spreadsheet
*              NREL SAM simulations matched to ATX 2013 Solar Generation Report



$GDXIN indatamod.gdx
$LOAD CapacityFactor
$GDXIN

*Commerical Units have slightly better capacity factors I added 5% for this model, but only during the day
CapacityFactor("C_PV",TIMESLICE,MONTH) = CapacityFactor("H_PV",TIMESLICE,MONTH);
CapacityFactor("C_PV",WeekdayDay,MONTH) = CapacityFactor("H_PV",WeekdayDay,MONTH)+0.02;
CapacityFactor("C_PV",WeekendDay,MONTH) = CapacityFactor("H_PV",WeekendDay,MONTH)+0.02;

CapacityFactor(BAT,TIMESLICE,MONTH) = 1;
CapacityFactor(TANK,TIMESLICE,MONTH) = 0.95;
CapacityFactor(GW,TIMESLICE,MONTH) = 1;
CapacityFactor(WW,TIMESLICE,MONTH) = 1;
CapacityFactor(UTIL, TIMESLICE, MONTH) = 1;


*CapacityFactor("C_WND",WeekdayDay,MONTH)=0.25;
*CapacityFactor("C_WND",WeekdayNight,MONTH)=0.65;


*CapacityFactor("C_WND",WeekendDay,MONTH)=0.25;
*CapacityFactor("C_WND",WeekendNight,MONTH)=0.65;

*Because of inverter efficiences solar improves by about 3% using the wind turbine, but I only added that during the day
CapacityFactor("C_HB",TIMESLICE,MONTH) = CapacityFactor("C_WND",TIMESLICE,MONTH)+CapacityFactor("C_PV",TIMESLICE,MONTH);

CapacityFactor("C_HB",WeekdayDay,MONTH) = CapacityFactor("C_WND",WeekdayDay,MONTH)+CapacityFactor("C_PV",WeekdayDay,MONTH)+0.015;
CapacityFactor("C_HB",WeekendDay,MONTH) = CapacityFactor("C_WND",WeekendDay,MONTH)+CapacityFactor("C_PV",WeekendDay,MONTH)+0.015;




Parameter CapitalCost(TECHNOLOGY) Annutized capital cost for Tech t $ per kL;
*Cost per GAL or kWatt
*The integer technolgies will have a capital cost that is the total cost
*Discount Rate 5% , PBP 5 MONTHs

$GDXIN indatamod.gdx
$LOAD CapitalCost
$GDXIN




Parameter VariableCost(TECHNOLOGY);
* Variable costs (variable O&M for power plants; fuel costs for fuel purchasing)
* Data Source: NREL 2016 Annual Technology Baseline
*Units: Million$/PJ, Million$/Millions of Miles
*              SPEER ATX Case Study for Demand Response
* In driving mode (3), VSTORE incurs typical variable cost per mile. Battery is free!

$GDXIN indatamod.gdx
$LOAD VariableCost
$GDXIN






Parameter FixedCost(TECHNOLOGY);
* Fixed costs (fixed O&M for power plants)
* Units: $/kW,?? Million$/Thousand Units (Vehicles)
* Data Source: NREL 2016 Annual Technology Baseline

$GDXIN indatamod.gdx
$LOAD FixedCost
$GDXIN



Parameter EnergyUse(TECHNOLOGY);
*energy use of each tech i kkWh per unit


$GDXIN indatamod.gdx
$LOAD EnergyUse
$GDXIN




*Household demand is assumed to be 185L/d (48 gal/day) kWhich translates to 5.55 kL/Month and 35% is outside
*Can modify each demand (outside and inside) below
*Original indoor demand is 3.6





*gathered from the weather service this is in mm
Parameter  Rainfall(TIMESLICE, MONTH);


$GDXIN indatamod.gdx
$LOAD Rainfall
$GDXIN

*Rainfall available in kL  Assume 1000 sq ft roof that yields 620 gal/in of water
Parameter Rainwater(TIMESLICE,MONTH);
*Roof size is assumed to trap 620 gallons of water per inch of rain

Rainwater(l,m) = Rainfall(l,m)*0.62*Roofsqft;
*Note Max Rainfall is about 400 gallons 0.33*0.62*1959




Positive Variables
     InstalledCapacity(TECHNOLOGY)
     ProducedWhiteWater(TECHNOLOGY,TIMESLICE,MONTH) Produced White Water by Tech
     ProducedGreyWater(TECHNOLOGY,TIMESLICE,MONTH) Produced White Water by Tech
     ProducedElectricity(TECHNOLOGY,TIMESLICE,MONTH) Produced Electricity by Tech
     CurtailmentWater(TECHNOLOGY,TIMESLICE,MONTH) Curtailed Water by Tech
     CurtailmentElectricity(TECHNOLOGY,TIMESLICE,MONTH) Curtailed Electricity by Tech
     ConsumedElectricity(TECHNOLOGY,TIMESLICE,MONTH) Consumed Electricity by Tech
     ConsumedElectricityP(TECHNOLOGY,TIMESLICE,MONTH) Consumed Electricity by Tech
     ConsumedElectricityN(TECHNOLOGY,TIMESLICE,MONTH) Consumed Electricity by Tech
     StorageLevel(STORAGE,TIMESLICE,MONTH) Water bought at time t over the tariff
     StorageAdded(STORAGE,TIMESLICE,MONTH) Water bought at time t over the tariff;


*Makes Sure Each Storage Starts and ?Ends? Empty
StorageLevel.fx(s,'WDA1','1') = 0;
*StorageLevel.fx(s,'WDE24','12') = 0;
ProducedWhiteWater.fx(TANK,'WDA1','1')=0;
ProducedGreyWater.fx(TANK,'WDA1','1')=0;
ProducedElectricity.fx(BAT,'WDA1','1')=0;


*Makes Sure only water water techs can produce white water
ProducedWhiteWater.fx(ELC,TIMESLICE,MONTH) = 0;
ProducedWhiteWater.fx(BAT,TIMESLICE,MONTH) =0;
ProducedWhiteWater.fx(GW,TIMESLICE,MONTH) = 0;


CurtailmentWater.fx(ELC,TIMESLICE,MONTH) = 0;
CurtailmentWater.fx(BAT,TIMESLICE,MONTH) =0;
CurtailmentWater.fx(TANK,TIMESLICE,MONTH) = 0;
CurtailmentWater.fx(WUTIL,TIMESLICE,MONTH) = 0;









*Makes sure only grey water techs can produce grey water
ProducedGreyWater.fx(ELC,TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx(BAT,TIMESLICE,MONTH) = 0;

ProducedGreyWater.fx(WW,TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx('U_H2O1',TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx('U_H2O2',TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx('U_H2O3',TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx('U_H2O4',TIMESLICE,MONTH) = 0;
ProducedGreyWater.fx('U_H2O5',TIMESLICE,MONTH) = 0;




*Makes sure only Electricity techs can produce electricity
ProducedElectricity.fx(WW,TIMESLICE,MONTH) = 0;
ProducedElectricity.fx(GW,TIMESLICE,MONTH) = 0;
ProducedElectricity.fx(TANK,TIMESLICE,MONTH) = 0;

CurtailmentElectricity.fx(WW,TIMESLICE,MONTH) = 0;
CurtailmentElectricity.fx(GW,TIMESLICE,MONTH) = 0;
CurtailmentElectricity.fx(TANK,TIMESLICE,MONTH) = 0;
CurtailmentElectricity.fx(BAT,TIMESLICE,MONTH) = 0;
CurtailmentElectricity.fx(EUTIL,TIMESLICE,MONTH) = 0;






parameter Proportion(FUEL,HOUSE,MONTH);
Proportion(f,hh,m) = HouseDemand(f,hh,m)*b/max(SpecifiedMonthlyDemand(f,m),0.00000001);




*Binary Variable
Integer Variable
Purchase(TECHNOLOGY) how many of a technology to buy for techs with multiple options;



Purchase.up(t) = h*b;
*Purchase.up('C_HB') = max(b/5,1);
*Purchase.up('C_SW') = max(b/5,1);
*Purchase.up('C_VRF') = max(b/5,1);

Parameter PropCheck(f,m);
PropCheck(f,m) = sum(hh,Proportion(f,hh,m));

Parameter DemandCheck(f,m);
DemandCheck(f,m) = SpecifiedMonthlyDemand(f,m)-sum(hh,HouseDemand(f,hh,m));



Display Proportion, PropCheck, SpecifiedMonthlyDemand, DemandCheck;














