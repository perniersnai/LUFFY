import re, subprocess
repo='/workspace/dumps/workspace/LUFFY'
def norm(s): return re.sub(r'^[^\w"\'“”]*(?:[A-Za-z0-9._-]+[) ]?[ ]*: )?','',s.strip()).rstrip('.')
files=subprocess.check_output(['git','-C',repo,'ls-files','*.py'], text=True).splitlines()
pat=re.compile(r'^\s*#\s*TODO\b',re.I)
src=[]
for f in files:
 for i,line in enumerate(open(f, errors='ignore').read().splitlines(),1):
  if pat.match(line):
   raw=line.split('TODO',1)[1].strip(); label=raw if raw.startswith('(') else raw.lstrip(':').strip()
   if label: src.append((f,i,label))
orig=subprocess.check_output(['git','-C',repo,'show','dev:README.md'], text=True)
base=[(m.group(1),int(m.group(2)),m.group(3)) for m in map(re.match,[r'- \[ \] \*\*([^:]+):(\d+)\*\* - (.*)$' for _ in orig.splitlines()],orig.splitlines()) if m]
# Desired list is union of TODO-normalized groups: for each normalized file/label, preserve entries from the Python TODOs if any are present; otherwise preserve baseline labels.
groups={}
for f,msg in [(f,norm(m)) for f,i,m in base+src]: groups.setdefault((f,msg),[]).append((f,msg))
final=[]
used_src=set()
for b in base:
 key=(b[0],norm(b[2]))
 ss=[x for x in src if x[0]==b[0] and norm(x[2])==norm(b[2])]
 if ss:
  for item in ss:
   if item not in final and item not in used_src: final.append(item); used_src.add(item)
 else:
  final.append(b)
# Preserve new TODO-normalized labels not represented in the baseline
for f,i,m in src:
 key=(f,norm(m))
 if not any(b[0]==f and norm(b[2])==norm(m) for b in base):
  if (f,i,m) not in final: final.append((f,i,m))
final=sorted(set(final))
start=orig.index('### 📝 Complete TODO List'); end=orig.index('\n## 🤝 Contributing',start)
section='\n'.join(['### 📝 Complete TODO List','']+[f'- [ ] **{f}:{i}** - {m}' for f,i,m in final])+'\n'
open('README.md','w').write(orig[:start]+section+orig[end:])
