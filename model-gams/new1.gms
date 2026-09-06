set i instances /1*32/;

file frun / run.gms /;

put frun /'* Run file to run ' card(i):0 'instances of mymodel'/;

loop(i,
put / '$call gams Water_Energy_Run.gms --inp='i.tl:0' lo=2 o=indata'i.tl:0'.lst lf=indata'i.tl:0'.log '
/ "$if errorlevel 1 $abort 'problems with instance"
i.tl:0 "'";
);
