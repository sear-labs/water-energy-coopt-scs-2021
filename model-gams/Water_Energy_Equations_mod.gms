*  Erick Jones
*Graduate Program in Operations Research and Industrial Engineering
* The University of Texas at Austin

* Water Energy model equations

* ##### Objective Function #####

Variable
     z      total cost
     z1     cost of buying and operating equipment
     z2     Cost of Water
     z3     Cost of Energy
     z4     Printable Version of Objective
    ;








Equations
     cost1     cost of buying the equipment
     cost2     cost of the water
     cost3     energy cost of using the equipment
     cost4      printable version of objective value
     cost        define objective function

;


*z1  =e=  sum(t,CapitalCost(t)*InstalledCapacity(t))+sum(NEXCL,FixedCost(NEXCL)*Purchase(NEXCL))+sum(EXCL,FixedCost(EXCL)*Purchasem(EXCL)) ;
cost1..         z1  =e=  sum(t,CapitalCost(t)*InstalledCapacity(t))+sum(t,FixedCost(t)*Purchase(t)) ;
cost2..         z2 =e= sum((t,l,m),VariableCost(t)*(ProducedWhiteWater(t,l,m)+ProducedGreyWater(t,l,m)));
cost3..         z3 =e= sum((t,l,m),VariableCost(t)*ProducedElectricity(t,l,m));
cost4..         z4 =e= z1+z2+z3;
cost..          z  =e= z4;

*Greater than because White Water can be used for GreyWater Demand
equation WhiteWaterBalance1(TIMESLICE,MONTH);
WhiteWaterBalance1(l,m)..   sum(WW,ProducedWhiteWater(WW,l,m)) =g= sum(WW,CurtailmentWater(WW,l,m))+
SpecifiedDemandProfile('GAL',l,m)*SpecifiedMonthlyDemand('W_H2O',m)+StorageAdded('H_RWTANK',l,m);

*equation WhiteWaterBalance2(TIMESLICE,MONTH);
*WhiteWaterBalance2(l,m+1)..   StorageLevel('H_RWTank','WEE48',m) + sum((t),ProducedWhiteWater(t,'WEE48',m)) =g=
*SpecifiedDemandProfile('W_H2O','WEE48',m)*SpecifiedMonthlyDemand('W_H2O',m)+StorageLevel('H_RWTank','WDA1',m+1);

*Has to be equal because all produced water has to equal all storage + demand + curtailment
equation WaterBalance1(TIMESLICE,MONTH);
WaterBalance1(l,m)..   sum(WW,ProducedWhiteWater(WW,l,m))+sum(GW,ProducedGreyWater(GW,l,m))
 =e= sum(t,CurtailmentWater(t,l,m))+ SpecifiedDemandProfile('GAL',l,m)*SpecifiedMonthlyDemand('GAL',m)+
StorageAdded('H_RWTANK',l,m)+StorageAdded('C_RWTANK',l,m);

*equation WaterBalance2(TIMESLICE,MONTH);
*WaterBalance2(l,m+1)..   sum((t),ProducedWhiteWater(t,'WEE48',m)+ProducedGreyWater(t,'WEE48',m))+StorageLevel('H_RWTank','WEE48',m)
*+StorageLevel('C_RWTank','WEE48',m) =g=
*SpecifiedDemandProfile('W_H2O','WEE48',m)*SpecifiedMonthlyDemand('W_H2O',m)
*+SpecifiedDemandProfile('G_H2O','WEE48',m)*SpecifiedMonthlyDemand('G_H2O',m)+StorageLevel('H_RWTank','WDA1',m+1)
*+StorageLevel('C_RWTank','WDA1',m+1);

*All produced ELC equals all produced Demand+Curtailment+Storage+Consumed Electricity
equation ElectricityBalance(TIMESLICE,MONTH);
ElectricityBalance(l,m)..   sum(ELC,ProducedElectricity(ELC,l,m)) =e= sum(ELC,CurtailmentElectricity(ELC,l,m))
+ SpecifiedDemandProfile('kWh',l,m)*SpecifiedMonthlyDemand('kWh',m)+StorageAdded('H_BAT',l,m)+
StorageAdded('C_BAT',l,m)+sum(WW,ConsumedElectricity(WW,l,m))+sum(GW,ConsumedElectricity(GW,l,m));



equation WaterEnergyBalance1(TECHNOLOGY,TIMESLICE,MONTH);
WaterEnergyBalance1(WW,l,m).. EnergyUse(WW)*ProducedWhiteWater(WW,l,m) =e= ConsumedElectricity(WW,l,m)  ;

equation WaterEnergyBalance2(TECHNOLOGY,TIMESLICE,MONTH);
WaterEnergyBalance2(GW,l,m).. EnergyUse(GW)*ProducedGreyWater(GW,l,m) =e= ConsumedElectricity(GW,l,m)  ;

equation Curtailment1(ELC,TIMESLICE,MONTH);
Curtailment1(ELC,l,m).. CurtailmentElectricity(ELC,l,m) =l= ProducedElectricity(ELC,l,m);

equation Curtailment2(WW,TIMESLICE,MONTH);
Curtailment2(WW,l,m).. CurtailmentWater(WW,l,m) =l= ProducedWhiteWater(WW,l,m);

equation Curtailment3(GW,TIMESLICE,MONTH);
Curtailment3(GW,l,m).. CurtailmentWater(GW,l,m) =l= ProducedGreyWater(GW,l,m);





*Upper and Lower Bounds for Water Tiers
* 0 to 2000 gallons (2000 gallons)
equation Water1(MONTH);
Water1(m).. sum(l,ProducedWhiteWater('U_H2O1',l,m)) =l= 2000*Purchase('U_H2O1');

* 2000 to 6000 gallons (4000 gallons)
equation Water2(MONTH);
Water2(m).. sum(l,ProducedWhiteWater('U_H2O2',l,m)) =l= 4000*Purchase('U_H2O2');

* 6000 to 11000 gallons (5000 gallons)
equation Water3(MONTH);
Water3(m).. sum(l,ProducedWhiteWater('U_H2O3',l,m)) =l= 5000*Purchase('U_H2O3');

* 11000 to 20000 gallons (9000 gallons)
equation Water4(MONTH);
Water4(m).. sum(l,ProducedWhiteWater('U_H2O4',l,m)) =l= 9000*Purchase('U_H2O4');



*RO unit does 9 kgal / h when solved optimally so thats the upper limit of the VRF
equation Water5(TIMESLICE,MONTH);
Water5(l,m).. ProducedWhiteWater('C_VRF',l,m) =l= 9000*Purchase('C_VRF');

*Making Sure H2O5 is less than half of the Monthly Demand Reasonable since the monthly demand is never over 40,000 gals
*Max demand is 27000 using 7000 as max for U_H2O5
equation Water6(MONTH);
Water6(m).. sum(l,ProducedWhiteWater('U_H2O5',l,m)) =l= 7000*Purchase('U_H2O5');

*equation Water7;
*Water7.. sum(WUTIL, Purchase(WUTIL)) + Purchase('H_RW') + Purchase('H_GW') + h*Purchase('C_GW') + h*Purchase('C_VRF') =g= h*b;

*Ensures you can't skip a tier
equation Water8;
Water8.. Purchase('U_H2O5') =l= Purchase('U_H2O4');

equation Water9;
Water9.. Purchase('U_H2O4') =l= Purchase('U_H2O3');

equation Water10;
Water10.. Purchase('U_H2O3') =l= Purchase('U_H2O2');

equation Water11;
Water11.. Purchase('U_H2O2') =l= Purchase('U_H2O1');

*Capacity Limits for GreyWater and StormWater
equation Water12(TIMESLICE,MONTH);
Water12(l,m).. ProducedGreyWater('C_GW',l,m) =l= 180*Purchase('C_GW');

equation Water13;
Water13.. InstalledCapacity('C_SW') =l= 100000*Purchase('C_SW');


equation Water14(MONTH);
Water14(m).. sum(l,ProducedGreyWater('H_GW',l,m)) =l= SpecifiedMonthlyDemand('W_H2O',m)/(h*b)*GWRecoveryFactor*Purchase('H_GW');




*Bounds for the Technologies

*Note Max Rainfall is about 400 gallons 0.33inches of rain *0.62 gal / sq ft*1959 sq ft
equation RainWaterLimits1(TIMESLICE,MONTH);
RainWaterLimits1(l,m).. ProducedWhiteWater('H_RW',l,m)  =l= Rainwater(l,m)*Purchase('H_RW');

equation RainWaterLimits2(TIMESLICE,MONTH);
RainWaterLimits2(l,m).. ProducedGreyWater('C_SW',l,m)  =l= 10000*Rainwater(l,m)*Purchase('C_SW');

equation RainWaterLimits3;
RainWaterLimits3.. Purchase('H_RWTANK')*sum((l,m),Rainwater(l,m))  =g= InstalledCapacity('H_RWTANK');

equation RainWaterLimits4;
RainWaterLimits4.. Purchase('C_RWTANK')*sum((l,m),Rainwater(l,m))*10000 =g= InstalledCapacity('C_RWTANK');

equation RainWaterLimits5(TIMESLICE,MONTH);
RainWaterLimits5(l,m).. StorageAdded('H_RWTANK',l,m)  =l= ProducedWhiteWater('H_RW',l,m);

equation RainWaterLimits6(TIMESLICE,MONTH);
RainWaterLimits6(l,m).. StorageAdded('C_RWTANK',l,m)  =l= ProducedGreyWater('C_SW',l,m);







equation GreyWaterLimits(TIMESLICE,MONTH);
GreyWaterLimits(l+1,m).. ProducedWhiteWater('C_VRF',l+1,m)+ProducedGreyWater('H_GW',l+1,m)+ProducedGreyWater('C_GW',l+1,m) =l=
SpecifiedDemandProfile('GAL',l,m)*SpecifiedMonthlyDemand('W_H2O',m)*GWRecoveryFactor;







*Upper  Bounds for Electricity Tiers

* 0 - 500 kwh
equation ELC1(MONTH);
ELC1(m).. sum(l,ProducedElectricity('U_ELC1',l,m)) =l= 500*Purchase('U_ELC1');

* 500 to 1000 kwh (500 kwh in this tier)
equation ELC2(MONTH);
ELC2(m).. sum(l,ProducedElectricity('U_ELC2',l,m)) =l= 500*Purchase('U_ELC2');

* 1000 to 1500 kwh (500 kwh in this tier)
equation ELC3(MONTH);
ELC3(m).. sum(l,ProducedElectricity('U_ELC3',l,m)) =l= 500*Purchase('U_ELC3');

* 1500 to 2500 kwh (1000 kwh in this tier)
equation ELC4(MONTH);
ELC4(m).. sum(l,ProducedElectricity('U_ELC4',l,m)) =l= 500*Purchase('U_ELC4');




*This is a 2.5 MW project so giving it a 4 MW for the maximum installed size
equation ELC5(TIMESLICE,MONTH);
ELC5(l,m).. ProducedElectricity('C_HB',l,m) =l= 2500*CapacityFactor('C_HB',l,m)*Purchase('C_HB');

*Most large wind farms in the Us are around 4 MW, using 250-1000 kW

equation ELC6(TIMESLICE,MONTH);
ELC6(l,m).. ProducedElectricity('C_WND',l,m) =l= 1000*CapacityFactor('C_WND',l,m)*Purchase('C_WND');

*Assume electric farm is 100-250kW
equation ELC7(TIMESLICE,MONTH);
ELC7(l,m).. ProducedElectricity('C_PV',l,m) =l= 250*CapacityFactor('C_PV',l,m)*Purchase('C_PV');


*Maximum Size of Storage is 60 kWh in one unit is
equation ELC8(TIMESLICE,MONTH);
ELC8(l,m).. ProducedElectricity('H_BAT',l,m) =l= 60*Purchase('H_BAT');


*Maximum Size of Storage is 1 MW in one unit is
equation ELC9(TIMESLICE,MONTH);
ELC9(l,m).. ProducedElectricity('C_BAT',l,m) =l= 500*Purchase('C_BAT');


* Maximum Allowed Solar on the Roof is 16 kW
equation ELC10(TIMESLICE,MONTH);
ELC10(l,m).. ProducedElectricity('H_PV',l,m) =l= 15.3*CapacityFactor('H_PV',l,m)*Purchase('H_PV');

*max demnad is 2700 kWh using 1000 in case of extra use from water
equation ELC11(MONTH);
ELC11(m).. sum(l,ProducedElectricity('U_ELC5',l,m)) =l= 1000*Purchase('U_ELC5');

*equation ELC12;
*ELC12.. sum(EUTIL,Purchase(EUTIL))+Purchase('H_PV')+h*Purchase('C_HB')+h*Purchase('C_PV')+h*Purchase('C_WND') =g= h*b;

equation ELC13;
ELC13.. Purchase('U_ELC5') =l= Purchase('U_ELC4');

equation ELC14;
ELC14.. Purchase('U_ELC4') =l= Purchase('U_ELC3');

equation ELC15;
ELC15.. Purchase('U_ELC3') =l= Purchase('U_ELC2');

equation ELC16;
ELC16.. Purchase('U_ELC2') =l= Purchase('U_ELC1');

equation ELC17(TIMESLICE,MONTH);
ELC17(l,m).. StorageAdded('H_BAT',l,m) =l= ProducedElectricity('H_PV',l,m);

equation ELC18(TIMESLICE,MONTH);
ELC18(l,m).. StorageAdded('C_BAT',l,m) =l= ProducedElectricity('C_PV',l,m)+ProducedElectricity('C_WND',l,m)+
ProducedElectricity('C_HB',l,m);


*Capacity Factors Ensures all Techs have enough installed capacity to produce water or ELC

equation CapacityFactorLimits1(TECHNOLOGY,TIMESLICE,MONTH);
CapacityFactorLimits1(ELC,l,m).. ProducedElectricity(ELC,l,m) =l=  InstalledCapacity(ELC)*CapacityFactor(ELC,l,m);

equation CapacityFactorLimits2(TECHNOLOGY,TIMESLICE,MONTH);
CapacityFactorLimits2(WW,l,m).. ProducedWhiteWater(WW,l,m) =l=  InstalledCapacity(WW)*CapacityFactor(WW,l,m);

equation CapacityFactorLimits3(TECHNOLOGY,TIMESLICE,MONTH);
CapacityFactorLimits3(GW,l,m).. ProducedGreyWater(GW,l,m) =l=  InstalledCapacity(GW)*CapacityFactor(GW,l,m);


equation CapacityFactorLimits4(TIMESLICE,MONTH);
CapacityFactorLimits4(l,m).. StorageLevel('H_BAT',l,m) =l=  InstalledCapacity('H_BAT');

equation CapacityFactorLimits5(TIMESLICE,MONTH);
CapacityFactorLimits5(l,m).. StorageLevel('C_BAT',l,m) =l=  InstalledCapacity('C_BAT');

equation CapacityFactorLimits6(TIMESLICE,MONTH);
CapacityFactorLimits6(l,m).. StorageLevel('H_RWTANK',l,m) =l=  InstalledCapacity('H_RWTANK');

equation CapacityFactorLimits7(TIMESLICE,MONTH);
CapacityFactorLimits7(l,m).. StorageLevel('C_RWTANK',l,m) =l=  InstalledCapacity('C_RWTANK');

equation CapacityFactorLimits8(TIMESLICE,MONTH);
CapacityFactorLimits8(l,m).. ProducedElectricity('C_HB',l,m) =l=  InstalledCapacity('C_HB')*
(0.20*(CapacityFactor('C_PV',l,m)+0.015)+0.8*CapacityFactor('C_WND',l,m));





*Battery and Tank Storage Equations


*Calculates Battery Consumtion by the difference in stroage level multiplied by Efficiency
*There are efficiency losses both in charging and discharging.
*Needed extra variables to calculate







*equation BatteryConsumption1(TIMESLICE,MONTH);
*BatteryConsumption1(l,m)..      ConsumedElectricityP('H_BAT',l,m)-ConsumedElectricityN('H_BAT',l,m) =e=
*(StorageLevel('H_BAT',l,m)-StorageLevel('H_BAT',l-1,m))*EnergyUse('H_BAT') ;

*equation BatteryConsumption2(TIMESLICE,MONTH);
*BatteryConsumption2(l,m)..      ConsumedElectricityP('C_BAT',l,m)-ConsumedElectricityN('C_BAT',l,m) =e=
*(StorageLevel('C_BAT',l,m)-StorageLevel('C_BAT',l-1,m))*EnergyUse('C_BAT') ;

*equation BatteryConsumption3(TIMESLICE,MONTH);
*BatteryConsumption3(l,m).. ConsumedElectricityP('H_BAT','WDA1',m)-ConsumedElectricityN('H_BAT','WDA1',m) =e=
*(StorageLevel('H_BAT','WDA1',m)-StorageLevel('H_BAT','WEE48',m-1))*EnergyUse('H_BAT');

*equation BatteryConsumption4(TIMESLICE,MONTH);
*BatteryConsumption4(l,m).. ConsumedElectricityP('C_BAT','WDA1',m)-ConsumedElectricityN('C_BAT','WDA1',m) =e=
*(StorageLevel('C_BAT','WDA1',m)-StorageLevel('C_BAT','WEE48',m-1))*EnergyUse('C_BAT');







equation BatteryStoragetoTech1(TIMESLICE,MONTH);
BatteryStoragetoTech1(l+1,m).. ProducedElectricity('H_BAT',l+1,m) =l= StorageLevel('H_BAT',l,m)*(1-EnergyUse('H_BAT'));

equation BatteryStoragetoTech2(TIMESLICE,MONTH);
BatteryStoragetoTech2(l+1,m).. ProducedElectricity('C_BAT',l+1,m) =l= StorageLevel('C_BAT',l,m)*(1-EnergyUse('C_BAT'));



equation BatteryStoragetoTech3(MONTH);
BatteryStoragetoTech3(m+1).. ProducedElectricity('H_BAT','WDA1',m+1) =l= StorageLevel('H_BAT','WDE24',m)*(1-EnergyUse('H_BAT'));

equation BatteryStoragetoTech4(MONTH);
BatteryStoragetoTech4(m+1).. ProducedElectricity('C_BAT','WDA1',m+1) =l= StorageLevel('C_BAT','WDE24',m)*(1-EnergyUse('H_BAT'));


equation BatteryStoragetoTech5(TIMESLICE,MONTH);
BatteryStoragetoTech5(l+1,m).. StorageLevel('H_BAT',l+1,m) =e= StorageLevel('H_BAT',l,m)*(1-EnergyUse('H_BAT'))
+StorageAdded('H_BAT',l,m)-ProducedElectricity('H_BAT',l+1,m);

equation BatteryStoragetoTech6(TIMESLICE,MONTH);
BatteryStoragetoTech6(l+1,m).. StorageLevel('C_BAT',l+1,m) =e= StorageLevel('C_BAT',l,m)*(1-EnergyUse('C_BAT'))
+StorageAdded('C_BAT',l,m)-ProducedElectricity('C_BAT',l+1,m);



equation BatteryStoragetoTech7(MONTH);
BatteryStoragetoTech7(m+1).. StorageLevel('H_BAT','WDA1',m+1) =e= StorageLevel('H_BAT','WDE24',m)*(1-EnergyUse('C_BAT'))
+StorageAdded('H_BAT','WDA1',m)-ProducedElectricity('H_BAT','WDA1',m+1);

equation BatteryStoragetoTech8(MONTH);
BatteryStoragetoTech8(m+1).. StorageLevel('C_BAT','WDA1',m+1) =e= StorageLevel('C_BAT','WDE24',m)*(1-EnergyUse('C_BAT'))
+StorageAdded('C_BAT','WDA1',m)-ProducedElectricity('C_BAT','WDA1',m+1);




equation TankStoragetoTech1(TIMESLICE,MONTH);
TankStoragetoTech1(l+1,m).. ProducedWhiteWater('H_RWTANK',l+1,m) =l= StorageLevel('H_RWTANK',l,m);

equation TankStoragetoTech2(TIMESLICE,MONTH);
TankStoragetoTech2(l+1,m).. ProducedGreyWater('C_RWTANK',l+1,m) =l= StorageLevel('C_RWTANK',l,m);


equation TankStoragetoTech3(MONTH);
TankStoragetoTech3(m+1).. ProducedWhiteWater('H_RWTANK','WDA1',m+1) =l= StorageLevel('H_RWTANK','WDE24',m);

equation TankStoragetoTech4(MONTH);
TankStoragetoTech4(m+1).. ProducedGreyWater('C_RWTANK','WDA1',m+1) =l= StorageLevel('C_RWTANK','WDE24',m);



equation TankStoragetoTech5(TIMESLICE,MONTH);
TankStoragetoTech5(l+1,m).. StorageLevel('H_RWTANK',l+1,m) =e= StorageLevel('H_RWTANK',l,m)
+StorageAdded('H_RWTANK',l+1,m)-ProducedWhiteWater('H_RWTANK',l+1,m);

equation TankStoragetoTech6(TIMESLICE,MONTH);
TankStoragetoTech6(l+1,m).. StorageLevel('C_RWTANK',l+1,m) =e= StorageLevel('C_RWTANK',l,m)
+StorageAdded('C_RWTANK',l+1,m)-ProducedGreyWater('C_RWTANK',l+1,m);


equation TankStoragetoTech7(MONTH);
TankStoragetoTech7(m+1).. StorageLevel('H_RWTANK','WDA1',m+1) =e= StorageLevel('H_RWTANK','WDE24',m)
+StorageAdded('H_RWTANK','WDA1',m+1)-ProducedWhiteWater('H_RWTANK','WDA1',m+1);

equation TankStoragetoTech8(MONTH);
TankStoragetoTech8(m+1).. StorageLevel('C_RWTANK','WDA1',m+1) =e= StorageLevel('C_RWTANK','WDE24',m)
+StorageAdded('C_RWTANK','WDA1',m+1)-ProducedGreyWater('C_RWTANK','WDA1',m+1);






***

*$ontext

*Makes it so each house has equal distribution of technologies



Positive variables
HouseUtilityWater(WUTIL,HOUSE,MONTH) Water Utilities Used by House per Month
HouseUtilityELC(EUTIL,HOUSE,MONTH) Electric Utilities Used by House per Month
HouseTechELC(ETECH,HOUSE,MONTH) Amount of electricity that goes to each evenly per month
HouseTechWater(WTECH,HOUSE,MONTH) Amount of water that goes to each evenly per month;

Binary variables
PurchaseEUTIL(EUTIL,HOUSE)
PurchaseWUTIL(WUTIL,HOUSE);




* Water 2000,4000, 5000, 9000

*equation HouseWater1(HOUSE,MONTH);
*HouseWater1(hh,m)..  sum((WUTIL,l),ProducedWhiteWater(WUTIL,l,m)) *Proportion('GAL',hh,m) =g= sum(WUTIL,HouseUtilityWater(WUTIL,hh,m))*b;

*Can do even split of techs or proportions; doing both at first
equation HouseWater2(WTECH,HOUSE,MONTH);
HouseWater2(WTECH,hh,m)..  sum(l,ProducedWhiteWater(WTECH,l,m)-CurtailmentWater(WTECH,l,m))*Proportion('GAL',hh,m)
+ sum(l,ProducedWhiteWater(WTECH,l,m)-CurtailmentWater(WTECH,l,m))/h =g= HouseTechWater(WTECH,hh,m)*b;

equation HouseWater3(HOUSE,MONTH);
HouseWater3(hh,m).. HouseDemand('GAL',hh,m) =l= sum(WUTIL,HouseUtilityWater(WUTIL,hh,m))+sum(WTECH,HouseTechWater(WTECH,hh,m));

equation HouseWater4(WUTIL,MONTH);
HouseWater4(WUTIL,m).. sum(hh,HouseUtilityWater(WUTIL,hh,m))*b =l= sum(l,ProducedWhiteWater(WUTIL,l,m));

equation HouseWater5(WUTIL,hh);
HouseWater5(WUTIL,hh).. sum(m,HouseUtilityWater(WUTIL,hh,m))=l=200000*PurchaseWUTIL(WUTIL,hh);



HouseUtilityWater.up('U_H2O1',hh,m) = 2000;
HouseUtilityWater.up('U_H2O2',hh,m) = 4000;
HouseUtilityWater.up('U_H2O3',hh,m) = 5000;
HouseUtilityWater.up('U_H2O4',hh,m) = 9000;

*Need additional constraints for even splits




*ELC     500 all

*equation HouseElectricity1(EUTIL,HOUSE,MONTH);
*HouseElectricity1(EUTIL,hh,m)..  sum(l,ProducedElectricity(EUTIL,l,m)) *Proportion('kWh',hh,m) =g= HouseUtilityELC(EUTIL,hh,m)*b;

*Can do even split of techs or proportions; doing both at first
equation HouseElectricity2(ETECH,HOUSE,MONTH);
HouseElectricity2(ETECH,hh,m)..  sum(l,ProducedElectricity(ETECH,l,m)-CurtailmentElectricity(ETECH,l,m))*Proportion('kWh',hh,m)
+ sum(l,ProducedElectricity(ETECH,l,m)-CurtailmentElectricity(ETECH,l,m))/h =g= HouseTechELC(ETECH,hh,m)*b;

equation HouseElectricity3(HOUSE,MONTH);
HouseElectricity3(hh,m).. HouseDemand('kWh',hh,m) =l= sum(EUTIL,HouseUtilityELC(EUTIL,hh,m))+sum(ETECH,HouseTechELC(ETECH,hh,m));

equation HouseElectricity4(EUTIL,MONTH);
HouseElectricity4(EUTIL,m).. sum(hh,HouseUtilityELC(EUTIL,hh,m))*b =l= sum(l,ProducedElectricity(EUTIL,l,m));

equation HouseElectricity5(EUTIL,hh);
HouseElectricity5(EUTIL,hh).. sum(m,HouseUtilityELC(EUTIL,hh,m)) =l= 20000*PurchaseEUTIL(EUTIL,hh);

HouseUtilityELC.up('U_ELC1',hh,m) = 500;
HouseUtilityELC.up('U_ELC2',hh,m) = 500;
HouseUtilityELC.up('U_ELC3',hh,m) = 500;
HouseUtilityELC.up('U_ELC4',hh,m) = 500;

equation UtilityPurchase1(EUTIL);
UtilityPurchase1(EUTIL).. Purchase(EUTIL) =g= sum(hh,PurchaseEUTIL(EUTIL,hh))*b;

equation UtilityPurchase2(WUTIL);
UtilityPurchase2(WUTIL).. Purchase(WUTIL) =g= sum(hh,PurchaseWUTIL(WUTIL,hh))*b;



*Need additional constraints for even splits



*$offtext
*$offtext

***



*Previous Big M formulation
*scalar MM /99999999/;

*equation Invest(Technology);
*Invest(t).. InstalledCapacity(t) =l= MM*Purchase(t);

*equation Invest2(Technology);
*Invest2(EXCL).. InstalledCapacity(EXCL) =l= MM*Purchasem(EXCL);
