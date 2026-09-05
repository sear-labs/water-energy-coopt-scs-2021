*All Discrete Decisions

Sets
       i   technology   / RWI, RWO, HGW, CGW, CSW /
*j   size / 100, 500, 1000/  Can add them as techs later
       t(t) subset of month /1*12/  ;

*Base Case is 100 houses
Scalar h number of households /100/

*Have to change manually
*They all include the capital, installation, and an aggregated sum of maintance cost i.e. changing filters
*Base case has a discount rate of 5% and a payback period of 5 years
*Assume 1000 gallon tanks for RW $2200 for outside, $3000 for inside use
*Household Greywater $2000
*Community Stormwater assume $100/kL and sized it at 6 kL/house * houses and half of the average amount of rain
*Community Greywater used the cost for the MIT system $10,000 annuitized


Parameter cc(i) annutized capital and fixed cost of tech i $ per kL

*/   RWI      692
*    RWO      508
*    HGW      461
*    CSW      17323
*    CGW      4620/;

*Discount rates of 10% PBP 5 years
*/   RWI      791.39
*    RWO      580.35
*    HGW      527.59
*    CSW      19784
*    CGW      5276/

*Discount rates of 5% PBP 10 years
/   RWI      388.51
     RWO      284.91
    HGW      259.01
    CSW      9712.84
    CGW      2590.09/;

*Changing Cost Paradigm
*cc(i) = cc(i)*3.9
*cc('RWO') = cc('RWO')*0.5;
*cc('RWI') = cc('RWI')*0.5;
*cc('HGW') = cc('HGW')*0.5;
*cc('CGW') = cc('CGW')*20;
*cc('CSW') = cc('CSW')*20;


*We take into account the maintance and usage cost in either energy or as annutized maintance cost
Parameter co(i) operating cost of each tech i $ per kL

/   RWI      0.0
    RWO      0.0
    HGW      0.0
    CSW      0.0
    CGW      0.0/

*Have to change manually
*Got from a paper that shows the energy use of rainwater pumps, doubled it for indoor water use which would probably include more filters and a UV light
*The grey water is from the Aqua2Use grey water manual
*Guessed for Stormwater its mostly just pumps  used pump that would handle the volume assumed 100 W 0.071 kwh every time used round up to 0.1
*This can be calculated using the RO energy from either Vitter or MIT
*Vitter used 10000 kwh/MMgal which is about 2.5 kwh/kL
*The MIT paper for their 6kL systems used the RO to clean the well and cistern water at a rate as low as 0.25 kwh/kL but I used a 0.5 kwh/kL

Parameter eu(i) energy use of each tech i kwh per kL

/   RWI      1.1
    RWO      0.55
    HGW      2.0
    CSW      0.1
    CGW      0.5/

*Price per kwh
Scalar ckwh cost of kwh $ per kwh /0.1/

Parameter ce(i) energy cost of each tech $ per kwh per kL;
         ce(i) = eu(i)*ckwh;


*assume 1000 gallon tank (3.78 kL) for rainwater per house, 25 gal (0.09 kL) for greywater per house
*For outdoor greywater assumed the community scale with RO is 12 kL which would be about 2 of the MIT systems
*The Vitter paper explored RO at a much larger scale with varying levels
*assume stormwater can hold half of the average rainfall per month 2.5in * 1000*h*.62 = 6*h kL
Parameter u1(i) upper bound (storage capacity) of each tech

/   RWI      3.78
    RWO      3.78
    HGW      0.09
    CSW      6
    CGW      1/



Parameter u(i) upper bound (storage capcity) of each tech ;
u(i) = u1(i)*h;
u('CGW') = 12;

*Assume at the begining you have 0 kL (0/264.172 gal) in the tank but can be changed
Scalar s0 intital storage capacity per household /0/;
s0 = s0*h;







*Household demand is assumed to be 185L/d (48 gal/day) which translates to 5.55 kL/Month and 35% is outside
*Can modify each demand (outside and inside) below
*Original indoor demand is 3.6
Scalar dif /1/;
Scalar rwf /1/;
Parameter  dwi(t)   demand for inside water at time t;
         dwi(t) = dif*3.6*h;
*/1*12 3.6*h/

*Original outdoor demand is 3.85
Parameter  dwo(t)   demand for outside water at time t;
         dwo(t) = dif*1.95*h;




*gathered from the weather service this is in mm
Parameter  rf(t)   rainfall capetown in mm
         /1  20
          2  20
          3  30
          4  50
          5  70
          6  90
          7  100
          8  70
          9  50
          10 40
          11 20
          12 20/;

*Rainfall available in kL  Assume 1000 sq ft roof that yields 620 gal/in of water
Parameter rw(t) total rainwater available in kL ;
rw(t) = rwf*rf(t)*h/25.4*(620/264.172);




Parameter
*Price includes the water charge, sanitation charge, and the fixed fee for a 15mm connection
*Note the base case is on the new restrictions which are lower than the original severe restrictions
*Severe: Price per kL $7.68504/ kL from 108.24 Rand (1 rand equals $0.071), $9.85338, $12.53647, $59.1927
*Current: Price per kL $5.55/ kL from 78.22 Rand (1 rand equals $0.071), $5.97, $6.66, $8.33

*price before higher tarriff
         pw price of water /5.55/

*Price per kL over the tariffs
         pwt1 price of water over the tariff /5.97/
         pwt2 price of water over the tariff /6.66/
         pwt3 price of water over the tariff /8.33/

*Cost of Pumping Water from storage
*This is almost zero (neglible), but want the model to have to make the decision to use this.
         ps cost to pump water from storage /0.0005/

*The tariff limits are based on the Cape Town Costs
*0 to 6, 6 to 10.5, 10.5 to 35
         mwt1 max water from mains before tariff /6/
         mwt2 max water from mains before tariff /4.5/
         mwt3 max water from mains before tariff /24.5/

         M /1000000/

*By household
         mw max water from mains before tariff;
         mw = mwt1*h;

         Parameter
         mw1 max water from mains before tariff;
         mw1 = mwt2*h;

         Parameter
         mw2 max water from mains before tariff;
         mw2 = mwt3*h;







Positive Variables
     w(t) Water bought at time t under the tariff
     wt1(t) Water bought at time t over the tariff
     wt2(t) Water bought at time t over the tariff
     wt3(t) Water bought at time t over the tariff
     x(i,t) Indoor Water from techology i at time t
     v(i,t) Outdoor water from technology i at time t
     s(t) storage at time t
     ed(t) daytime energy use
     en(t) night time energy use
     e(t) total energy use;

*Initializing Solution
x.l(i,t) = 0;
v.l(i,t) = 0;
w.l(t) = mw;

*Making sure you can only use the outside technolgies outside and the inside flows aren't accounted for with the outside variable
     v.fx('RWI',t) = 0;
     v.fx('CGW',t) = 0;
     x.fx('CSW',t) = 0;
     x.fx('HGW',t) =0;
     x.fx('RWO',t) =0;





Variable
     z      total cost
     z1     cost of buying equipment
     z2     cost of the water
     z3     energy costs
     sf(t) flow to storage;

sf.l(t) = 0;



Binary variables
y(i) decision buy technology i;
*Want to make this a continous variable so that it can choose to invest in a certain amount of a tech instead of assuming all houses do it or none.

y.l(i) = 0;



Equations
     cost1     cost of buying the equipment
     cost2     cost of the water
     cost3     energy cost of using the equipment
     cost        define objective function

     water(t)   controlling for water produced
     water1(t)   controlling for water produced
     iwater(t)  indoor water
*iwater1(t)  indoor water

     investi(i)    invest in inside water technolgies
     investo(i)  invest in outside water technologies

     lowerrw(t)  lower bound for rainwater I
     lowerrw1(t)  lower bound for rainwater O
     lowersw(t)  lower bound for stormwater
     upperrw(t)  upper bound for rainwater   I
     upperrw1(t)  upper bound for rainwater O
     upperrw2(t)  upper bound for rainwater
     uppersw(t)  upper bound for stormwater

     upperx(t)  upper bound for water x not rainwater
     upperx1(t)  upper bound for water v  not rainwater
     upperx2(t)  upper bound for indoor water

     upperw(t)  upper bound for water w
     upperwt1(t)  upper bound for tariff water wt1
     upperwt2(t)  upper bound for tariff water wt2

     storage(t) level of storage at time t
     storagebnd(t) storage bound

     energyuse(t) energy use at time t

*uppery(i) upper bound for how much
     ;


cost1..         z1  =e=  sum((i),cc(i)*h*y(i))-h*cc('CGW')*y('CGW')-h*cc('CSW')*y('CSW')+cc('CGW')*y('CGW')+cc('CSW')*y('CSW') ;
cost2..         z2 =e= sum((i,t),co(i)*(x(i,t)+v(i,t)))+sum(t,w(t)*pw+wt1(t)*pwt1+wt2(t)*pwt2+wt3(t)*pwt3+ps*s(t));
cost3..         z3 =e= sum(t,ckwh*e(t));
cost..          z =e= z1+z2+z3;

water1(t)..      sum((i),x(i,'1')+v(i,'1'))+w('1')+wt1('1')+wt2('1')+wt3('1')+s0 =e= dwi('1') + dwo('1')+sf('1') ;
water(t+1)..      sum((i),x(i,t+1)+v(i,t+1))+w(t+1)+wt1(t+1)+wt2(t+1)+wt3(t+1)+s(t) =e= dwi(t+1) + dwo(t+1)+sf(t+1) ;



*Linear Lag and Lead in Equations from GAMS
*Note storage water cannot be used for inside demand (this addresses the sitting water concern)
iwater(t)..     sum((i),x(i,t))+w(t)+wt1(t)+wt2(t)+wt3(t) =g= dwi(t);
*iwater1(t)..     sum((i),x(i,'1'))+w('1')+wt1('1')+wt2('1')+wt3('1') =g= dwi('1');

investi(i)..  sum(t,x(i,t))  =l=  M*y(i);
investo(i)..  sum(t,v(i,t))  =l=  M*y(i);

*uppery(i).. y(i) =l= h;


*stormwate inflation factor for the neighborhood area
Scalar swi /10/;
*Usable Greywater from the houses
Scalar ugw /0.75/;

*Lower and Upper Bounds for how much rain has to be captured and how much can be used
lowerrw(t)..      x('RWI',t) =g= 0.01*rw(t)*y('RWI');
lowerrw1(t)..      v('RWO',t) =g= 0.01*rw(t)*y('RWO');
lowersw(t)..      v('CSW',t) =g= 0.01*swi*rw(t)*y('CSW');

upperrw(t)..      x('RWI',t) =l= rw(t)*y('RWI');
upperrw1(t)..      v('RWO',t) =l= rw(t)*y('RWO');
upperrw2(t)..      x('RWI',t) + v('RWO',t) =l= rw(t);

uppersw(t)..      v('CSW',t) =l= swi*rw(t)/h*y('CSW');

upperx(t)..      x('CGW',t) =l= ugw*dwi(t)*y('CGW');
upperx1(t)..      v('HGW',t) =l= ugw*dwi(t)*y('HGW');
upperx2(t)..      x('CGW',t) + v('HGW',t) =l= ugw*dwi(t);

*Forces you to use different cost water by setting upper bounds
upperw(t)..         w(t) =l= mw;
upperwt1(t)..         wt1(t) =l= mw1;
upperwt2(t)..         wt2(t) =l= mw2;


*These keep track of how much water is stored at each period and makes sure it doesn't exceed tank capacity
storagebnd(t)..  s(t) =l= sum(i,u(i)*y(i));
storage(t)..     sf(t) =e= s(t);


*Can separate the energy use into night and daytime use later
energyuse(t)..      sum(i,eu(i)*x(i,t)+eu(i)*v(i,t)) =e= e(t);












Model program / all /

option optcr = 0.0001, optca = 0.0001, mip = cplex;





solve program using mip min z;

display z1.l, z2.l, z3.l, z.l, x.l, v.l, y.l, w.l, wt1.l, s.l, sf.l, e.l;

