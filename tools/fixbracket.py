import glob,sys
for p in glob.glob("kb/w/*/summary.typ"):
    s=open(p,encoding="utf-8").read()
    o,c=s.count("["),s.count("]")
    if o>c:
        s=s.rstrip("\n")+"\n"*1+"]\n"*(o-c)
        open(p,"w",encoding="utf-8").write(s)
        print("fixed",p,o,c)
