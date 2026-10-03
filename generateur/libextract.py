import re
L='ks/usr/share/kicad/symbols/'
def blocks(lib):
    t=open(L+lib+'.kicad_sym').read()
    out={}; i=0
    for m in re.finditer(r'\n  \(symbol "([^"]+)"',t):
        s=m.start()+3; d=0; j=s; ins=False
        while True:
            c=t[j]
            if ins:
                if c=='\\': j+=2; continue
                if c=='"': ins=False
            elif c=='"': ins=True
            elif c=='(': d+=1
            elif c==')':
                d-=1
                if d==0: break
            j+=1
        out[m.group(1)]=t[s:j+1]
    return out
def flat(lib,name):
    B=blocks(lib); b=B[name]
    m=re.match(r'\(symbol "[^"]+" \(extends "([^"]+)"\)',b)
    if not m: body=b
    else:
        par=m.group(1); pb=flat(lib,par)
        # child props
        cprops=re.findall(r'\n    \(property "([^"]+)" "((?:[^"\\]|\\.)*)"',b)
        body=pb.replace(f'(symbol "{par}"',f'(symbol "{name}"',1)
        body=re.sub(rf'\(symbol "{re.escape(par)}_(\d+_\d+)"',lambda mm:f'(symbol "{name}_{mm.group(1)}"',body)
        for k,v in cprops:
            body=re.sub(rf'(\(property "{re.escape(k)}" )"((?:[^"\\]|\\.)*)"',lambda mm:mm.group(1)+'"'+v.replace('\\','\\\\')+'"',body,count=1)
    return body
def full(lib,name):
    b=flat(lib,name)
    b=b.replace(f'(symbol "{name}"',f'(symbol "{lib}:{name}"',1)
    b=re.sub(r'(?<=[\s\)])hide(?=[\s\)])','(hide yes)',b)
    return b
def pins(b):
    return re.findall(r'\(pin (\w+) \w+ \(at ([-\d.]+) ([-\d.]+) (\d+)\) \(length [\d.]+\)(?:\s*\(hide yes\))?\s*\(name "([^"]*)"[^\n]*\n?\s*\(number "([^"]+)"',b)
