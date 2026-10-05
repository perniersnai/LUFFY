import re, subprocess
repo='/workspace/dumps/workspace/LUFFY'
orig=subprocess.check_output(['git','-C',repo,'show','dev:README.md'], text=True)
files=subprocess.check_output(['git','-C',repo,'ls-files','*.py'], text=True).splitlines(); pat=re.compile(r'^\s*#\s*TODO\b',re.I)
src=[]
for f in files:
 for i,line in enumerate(open(f, errors='ignore').read().splitlines(),1):
  if pat.match(line):
   raw=line.split('TODO',1)[1].strip(); label=raw if raw.startswith('(') else raw.lstrip(':').strip()
   if label: src.append((f,i,label))
base=[(m.group(1),int(m.group(2)),m.group(3)) for m in map(re.match,[r'- \[ \] \*\*([^:]+):(\d+)\*\* - (.*)$' for _ in orig.splitlines()],orig.splitlines()) if m]
# Baseline TODOs are the developer-facing source-of-truth labels; union in changed TODOs, sorting after merging.
desired=set(base)|set(src)
desired=sorted(desired)
start=orig.index('### 📝 Complete TODO List'); end=orig.index('\n## 🤝 Contributing',start)
section='\n'.join(['### 📝 Complete TODO List','']+[f'- [ ] **{f}:{i}** - {m}' for f,i,m in desired])+'\n'
open('README.md','w').write(orig[:start]+section+orig[end:])
