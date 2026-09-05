"""Household water-supply technology MILP - Python/gurobipy port of Project_Modelv4.gms."""
import gurobipy as gp
from gurobipy import GRB

TECHS = ["RWI", "RWO", "HGW", "CGW", "CSW"]
MONTHS = list(range(1, 13))


def build(cfg):
    h = cfg["households"]
    cc, co, eu, u1 = cfg["capital_cost"], cfg["operating_cost"], cfg["energy_use"], cfg["storage_cap"]
    dif, rwf, ckwh = cfg["demand_factor"], cfg["rainfall_factor"], cfg["price_kwh"]
    pw, pwt = cfg["price_water"], cfg["price_water_tiers"]
    ps, swi, ugw, M = cfg["pump_cost"], cfg["stormwater_factor"], cfg["usable_greywater"], cfg["big_m"]
    rf = cfg["rainfall_mm"]

    u = {i: u1[i] * h for i in TECHS}
    u["CGW"] = 12.0                                   # GAMS overrides this after scaling
    s0 = cfg["initial_storage"] * h
    dwi = {t: dif * cfg["indoor_demand"] * h for t in MONTHS}
    dwo = {t: dif * cfg["outdoor_demand"] * h for t in MONTHS}
    rw = {t: rwf * rf[t] * h / 25.4 * (620 / 264.172) for t in MONTHS}
    mw = [cfg["tier_limits"][k] * h for k in range(3)]

    m = gp.Model("water_energy")
    w  = m.addVars(MONTHS, name="w")
    wt = {k: m.addVars(MONTHS, name=f"wt{k+1}") for k in range(3)}
    x  = m.addVars(TECHS, MONTHS, name="x")
    v  = m.addVars(TECHS, MONTHS, name="v")
    s  = m.addVars(MONTHS, name="s")
    sf = m.addVars(MONTHS, lb=-GRB.INFINITY, name="sf")
    e  = m.addVars(MONTHS, name="e")
    y  = m.addVars(TECHS, name="y")
    y1 = m.addVars(TECHS, vtype=GRB.BINARY, name="y1")

    for t in MONTHS:                                   # v.fx / x.fx in GAMS
        v["RWI", t].UB = v["CGW", t].UB = 0.0
        x["CSW", t].UB = x["HGW", t].UB = x["RWO", t].UB = 0.0

    tot = lambda t: gp.quicksum(x[i, t] + v[i, t] for i in TECHS)
    buy = lambda t: w[t] + wt[0][t] + wt[1][t] + wt[2][t]

    # water1/iwater1 are declared over t but reference month 1 only -> 12 identical rows in GAMS.
    m.addConstr(tot(1) + buy(1) + s0 == dwi[1] + dwo[1] + sf[1], "water1")
    m.addConstr(gp.quicksum(x[i, 1] for i in TECHS) + buy(1) >= dwi[1], "iwater1")
    for t in MONTHS[1:]:
        m.addConstr(tot(t) + buy(t) + s[t - 1] == dwi[t] + dwo[t] + sf[t], f"water[{t}]")
        m.addConstr(gp.quicksum(x[i, t] for i in TECHS) + buy(t) >= dwi[t], f"iwater[{t}]")

    for i in TECHS:
        m.addConstr(gp.quicksum(x[i, t] for t in MONTHS) <= M * y1[i], f"investi[{i}]")
        m.addConstr(gp.quicksum(v[i, t] for t in MONTHS) <= M * y1[i], f"investo[{i}]")
        m.addConstr(y[i] <= h, f"uppery[{i}]")
    m.addConstr(y["CGW"] == h * y1["CGW"], "comrestrict1")
    m.addConstr(y["CSW"] == h * y1["CSW"], "comrestrict2")

    for t in MONTHS:
        m.addConstr(x["RWI", t] >= 0.01 * rw[t] * y1["RWI"], f"lowerrw[{t}]")
        m.addConstr(v["RWO", t] >= 0.01 * rw[t] * y1["RWO"], f"lowerrw1[{t}]")
        m.addConstr(v["CSW", t] >= 0.01 * swi * rw[t] * y1["CSW"], f"lowersw[{t}]")
        m.addConstr(x["RWI", t] <= rw[t] / h * y["RWI"], f"upperrw[{t}]")
        m.addConstr(v["RWO", t] <= rw[t] / h * y["RWO"], f"upperrw1[{t}]")
        m.addConstr(x["RWI", t] + v["RWO", t] <= rw[t], f"upperrw2[{t}]")
        m.addConstr(v["CSW", t] <= swi * rw[t] / h * y["CSW"], f"uppersw[{t}]")
        m.addConstr(x["CGW", t] <= ugw * dwi[t] * y1["CGW"], f"upperx[{t}]")
        m.addConstr(v["HGW", t] <= ugw * dwi[t] / h * y["HGW"], f"upperx1[{t}]")
        m.addConstr(x["CGW", t] + v["HGW", t] <= ugw * dwi[t], f"upperx2[{t}]")
        m.addConstr(w[t] <= mw[0], f"upperw[{t}]")
        m.addConstr(wt[0][t] <= mw[1], f"upperwt1[{t}]")
        m.addConstr(wt[1][t] <= mw[2], f"upperwt2[{t}]")
        m.addConstr(s[t] <= gp.quicksum(u[i] * y[i] for i in TECHS), f"storagebnd[{t}]")
        m.addConstr(sf[t] == s[t], f"storage[{t}]")
        m.addConstr(gp.quicksum(eu[i] * (x[i, t] + v[i, t]) for i in TECHS) == e[t], f"energyuse[{t}]")

    z1 = (gp.quicksum(cc[i] * y[i] for i in TECHS) - cc["CGW"] * y["CGW"] - cc["CSW"] * y["CSW"]
          + cc["CGW"] * y1["CGW"] + cc["CSW"] * y1["CSW"])
    z2 = (gp.quicksum(co[i] * (x[i, t] + v[i, t]) for i in TECHS for t in MONTHS)
          + gp.quicksum(w[t] * pw + wt[0][t] * pwt[0] + wt[1][t] * pwt[1] + wt[2][t] * pwt[2]
                        + ps * s[t] for t in MONTHS))
    z3 = gp.quicksum(ckwh * e[t] for t in MONTHS)
    m.setObjective(z1 + z2 + z3, GRB.MINIMIZE)
    m._vars = dict(w=w, wt=wt, x=x, v=v, s=s, e=e, y=y, y1=y1)
    m._costs = dict(z1=z1, z2=z2, z3=z3)
    return m
