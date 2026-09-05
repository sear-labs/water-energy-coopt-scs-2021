
*Parameters to Export

Parameter ELCFractionm(MONTH) fraction of electricity supplied by technology;
ELCFractionm(m) = sum((ETECH,l),ProducedElectricity.l(ETECH,l,m))/sum((t,l),ProducedElectricity.l(t,l,m)+0.00001);

Parameter WaterFractionm(MONTH) fraction of water supplied by technology;
WaterFractionm(m) = sum((WTECH,l),ProducedWhiteWater.l(WTECH,l,m)+ProducedGreyWater.l(WTECH,l,m))
/sum((t,l),ProducedWhiteWater.l(t,l,m)+ProducedGreyWater.l(t,l,m)+0.00001);

Parameter ELCFraction fraction of electricity supplied by technology;
ELCFraction = sum((ETECH,l,m),ProducedElectricity.l(ETECH,l,m))/sum((t,l,m),ProducedElectricity.l(t,l,m)+0.00001);

Parameter WaterFraction fraction of water supplied by technology;
WaterFraction = sum((WTECH,l,m),ProducedWhiteWater.l(WTECH,l,m)+ProducedGreyWater.l(WTECH,l,m))
/sum((t,l,m),ProducedWhiteWater.l(t,l,m)+ProducedGreyWater.l(t,l,m)+0.00001);

Parameter WWProductionByTechnology(t,MONTH) white water produced by each technology;
WWProductionByTechnology(t,m) = sum(l,ProducedWhiteWater.l(t,l,m));

Parameter GWProductionByTechnology(t,MONTH);
GWProductionByTechnology(t,m) = sum(l,ProducedGreyWater.l(t,l,m));

Parameter ELCProductionByTechnology(ELC,MONTH);
ELCProductionByTechnology(ELC,m) = sum(l,ProducedElectricity.l(ELC,l,m));

Parameter StorageLevelEnd(s,MONTH);
StorageLevelEnd(s,m) = StorageLevel.l(s,'WDE24',m);

Parameter CurtailmentELCm(ELC,MONTH);
CurtailmentELCm(ELC,m) = sum(l, CurtailmentElectricity.l(ELC,l,m));

Parameter CurtailmentWaterm(TECHNOLOGY,MONTH);
CurtailmentWaterm(t,m) = sum(l, CurtailmentWater.l(t,l,m));

Parameter StorageAddedm(Storage,MONTH);
StorageAddedm(s,m) = sum(l, StorageAdded.l(s,l,m));

Parameter StorageLoss1(MONTH);
StorageLoss1(m) = sum(l, StorageAdded.l('H_BAT',l,m)-ProducedElectricity.l('H_BAT',l,m));

Parameter StorageLoss2(MONTH);
StorageLoss2(m) = sum(l, StorageAdded.l('C_BAT',l,m)-ProducedElectricity.l('C_BAT',l,m));



$ontext
Parameter EvenSharedTechELCm(ETECH,MONTH);
EvenSharedTechELCm(ETECH,m) = sum(hh, EvenSharedTechELC.l(hh,ETECH,m));

Parameter EvenSharedTechWaterm(WTECH,MONTH);
EvenSharedTechWaterm(WTECH,m) = sum(hh, EvenSharedTechWater.l(hh,WTECH,m));

$offtext


Parameter HourlyDemand(FUEL,TIMESLICE,MONTH);
HourlyDemand(f,l,m) =  SpecifiedDemandProfile(f,l,m)*SpecifiedMonthlyDemand(f,m) ;

Parameter ActualDemand(FUEL,MONTH);
ActualDemand(f,m) = sum(l,HourlyDemand(f,l,m));

Parameter HourlyELC(ELC,TIMESLICE,MONTH);
HourlyELC(ELC,l,m) = ProducedElectricity.l(ELC,l,m);

Parameter HourlyWW(WW,TIMESLICE,MONTH);
HourlyWW(WW,l,m) = ProducedWhiteWater.l(WW,l,m);

Parameter HourlyGW(GW,TIMESLICE,MONTH);
HourlyGW(GW,l,m) = ProducedGreyWater.l(GW,l,m);


Parameter WWEnergyConsumption(WW,MONTH);
WWEnergyConsumption(WW,m) = sum(l, ConsumedElectricity.l(WW,l,m)) ;

Parameter GWEnergyConsumption(GW,MONTH);
GWEnergyConsumption(GW,m) = sum(l, ConsumedElectricity.l(GW,l,m));

Parameter BATEnergyConsumption(BAT,MONTH);
BATEnergyConsumption(BAT,m) = sum(l, ConsumedElectricity.l(BAT,l,m));

Parameter MSD1(MONTH);
MSD1(m) =  SpecifiedDemandProfile('GAL','WDA1',m)*SpecifiedMonthlyDemand('GAL',m);

Parameter MSD2(MONTH);
MSD2(m) =  SpecifiedDemandProfile('GAL','WDA1',m)*SpecifiedMonthlyDemand('W_H2O',m);





execute_unload 'ResultsWE_mod.gdx', z1.l, z2.l, z3.l, z4.l, z.l, h, b, ELCFraction, WaterFraction, Purchase.l, InstalledCapacity.l,
WWProductionByTechnology, GWProductionByTechnology, ELCProductionByTechnology,ELCFractionm,  WaterFractionm, StorageLevelEnd, StorageAdded.l, WWEnergyConsumption, GWEnergyConsumption, BATEnergyConsumption, ActualDemand, HourlyDemand, HourlyELC, HourlyWW,
HourlyGW, CurtailmentELCm, CurtailmentWaterm, StorageLoss1, StorageLoss2, SpecifiedMonthlyDemand, MSD1, MSD2, StorageLevel.l, ProducedElectricity.l ;


*,EvenSharedTechWaterm, EvenSharedTechELCm
* , HouseUtilityWater.l, HouseUtilityELC.l








