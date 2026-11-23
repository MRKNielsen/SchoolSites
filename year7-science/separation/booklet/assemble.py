"""Assemble Separation_Experiment_Booklet_Yr7.tex from its parts.
Adds a \\label to every key-vocabulary word and builds the glossary from them."""
import re
parts=['pre.tex','exp-preamble.tex','st-cover.tex','style.tex','front.tex','exp1.tex','exp2.tex','exp3.tex','exp4.tex','exp5.tex','exp6.tex','exp7.tex','exp8.tex','exp9.tex']
txt={p:open(p).read() for p in parts}
words=[]
def lab(m):
    w=m.group(2); slug=re.sub(r'[^a-z0-9]+','-',w.lower()).strip('-')
    if any(l=='voc:'+slug for _,l in words): return m.group(0)
    words.append((w,'voc:'+slug))
    return m.group(1)+'\\label{voc:'+slug+'}'+m.group(3)
for p in ['exp%d.tex'%i for i in range(1,10)]:
    s=txt[p]
    a=s.index('\\vocabhead'); b=s.index('\\end{ctab}',a)
    v=s[a:b]
    v=re.sub(r'(\\textbf\{([^}]+)\})(\}?\s*&)', lab, v)
    txt[p]=s[:a]+v+s[b:]
gl=['\\clearpage','\\hypertarget{glossary}{}\\pdfbookmark[1]{Glossary}{glossarybm}',
    '\\markboth{Glossary}{}{\\headingfont\\bfseries\\LARGE Glossary}\\label{sec:glossary}\\par\\vspace{1mm}\\noindent\\rule{\\linewidth}{0.6pt}\\par',
    'Every key vocabulary word in this booklet, and the page where you wrote what it means.\\par',
    '\\renewcommand{\\arraystretch}{1.4}',
    '\\begin{longtable}{|L{6cm}|C{2cm}|}','\\hline\\thead{Word} & \\thead{Page} \\\\ \\hline \\endhead']
for w,l in sorted(words,key=lambda x:x[0].lower()):
    gl.append('\\glossrow{%s}{%s}'%(w,l))
gl+=['\\end{longtable}','']
e=txt['exp9.tex']; i=e.rindex('\\end{document}')
txt['exp9.tex']=e[:i]+'\n'.join(gl)+'\n'+e[i:]
open('Separation_Experiment_Booklet_Yr7.tex','w').write(''.join(txt[p] for p in parts))
print(len(words),'glossary words')
