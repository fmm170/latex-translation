import argparse
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('filename')

args = parser.parse_args()

#查找同目录下以.tex结尾的latex文件
if(re.search('.tex$',args.filename)==None):
    sys.exit('The input should be .tex file. Exit.')

print('LaTex file:',args.filename)

#按字符读入
with open(args.filename,'r') as source_file:
    source = source_file.read()
        
#以[1.1] [1,1]为标志
conflicts = re.findall('\[0123]*[\.\,][0-9]*',source)
if(conflicts!=[]):
    print('Token conflicts detected:',conflicts)
else:
    print('No token conflicts detected. Proceeding.')

latex = [] #存储一整段标签+其中的文字
bdoc = re.search(r'\\begin{document}',source)
edoc = re.search(r'\\end{document}',source)

#从文档中筛选出\begin{document} ...\end{document}之间的文本 并且替换labe为[1.0]
if(bdoc!=None):
    preamble = source[:bdoc.end()]
    latex.append(preamble)
    if(edoc!=None):
        text = '[1.0]' + source[bdoc.end():edoc.start()]
        postamble = source[edoc.start():]
    else:
        text = '[1.0]' + source[bdoc.end():]
        postamble = []
else:
    text = source
    postamble = []

#去掉文本中以%开头的注释 并替换为___GTEXFIXCOMMENT1___
recomment = re.compile(r'(?<!\\)[%].*')
comments = []

for m in recomment.finditer(text):
    comments.append(m.group())

ncomment = 0

def repl_comment():
    global ncomment
    ncomment +=1
    return '___GTEXFIXCOMMENT%d___'%(ncomment-1)
    
text = recomment.sub(repl_comment(),text)

#comments写入文件中
with open('comments.txt','w') as c:
    c.write(str(comments))

### Hide LaTeX constructs \begin{...} ... \end{...} 数学公式 图片 多行公式对齐 公式只换行不对齐 
# 参考文献宽度 表格 公式编号 公式对齐 无标号
#无标号行间公式
start_values = []
end_values = []
for m in re.finditer(r'\\begin{equation}|\\begin{figure}|\\begin{eqnarray}|\\begin{multline}'
    +r'|\\begin{thebibliography}|\\begin{verbatim}|\\begin{table}|\\begin{subequations}|\\begin{align}'
    +r'|\\begin{displaymath}|\\begin{gather}|\\\[',text):
    start_values.append(m.start())
for m in re.finditer(r'\\end{equation}|\\end{figure}|\\end{eqnarray}|\\end{multline}'
    +r'|\\end{thebibliography}|\\end{verbatim}|\\end{table}|\\end{subequations}|\\end{align}'
    +r'|\\end{displaymath}|\\end{gather}|\\\]',text):
    end_values.append(m.end())

#把之前找到的大段结构中label替换为[1.]
nitems = len(start_values)
assert(len(end_values)==nitems)
if(nitems>0):
    newtext = text[:start_values[0]]
    for neq in range(nitems-1):
        latex.append(text[start_values[neq]:end_values[neq]])
        newtext +='[1.%d]'%(len(latex)-1)+text[end_values[neq]:start_values[neq+1]]
    latex.append(text[start_values[nitems-1]:start_values[nitems-1]])
    newtext +='[1.%d]'%(len(latex)-1)+text[end_values[nitems-1]:]
    text = newtext

#处理\end{document}
if(postamble!=[]):
    latex.append(postamble)
    text +='[1.%d]'%(len(latex)-1)
    
with open('gtexifix_latex','w') as c:
    c.write(str(latex))

#r'(\$+)(?:(?!\1)[\s\S])*\1' 识别文本中的公式$...$ and $$...$$ from
recommand = re.compile(r'___GTEXFIXCOMMENT[0-9]*___|\\title|\\chapter|\\section|\\subsection|\\subsubsection|~*\\footnote[0-9]*|(\$+)(?:(?!\1)[\s\S])*\1|~*\\\w*\s*{[^}]*}|~*\\\w*')
commands = []
for m in recommand.finditer(text):
    commands.append(m.group())

nc = 0
def repl(obj):
    global nc
    nc +=1
    return'[2.%d]'%(nc-1)
text = recommand.sub(repl,text)

with open('gtexifix_commands','w') as c:
    c.write(str(commands))

#保存处理结果到 .txt file
limit=30000 
filebase = re.sub('.tex$','',args.filename)
start=0
npart=0
#找到文章结尾 写到多个文件中
for m in re.finditer(r'\.\n',text):
    if(m.end()-start<limit):
        end=m.end()
    else:
        output_filename = filebase+'_%d.txt'%npart
        npart+=1
        with open(output_filename, 'w') as txt_file:
	        txt_file.write(text[start:end])
        print('Output file:',output_filename)
        start=end
        end=m.end()
output_filename = filebase+'_%d.txt'%npart
with open(output_filename, 'w') as txt_file:
    txt_file.write(text[start:])
print('Output file:',output_filename)
print('Supply the output file(s) to Google Translate')
