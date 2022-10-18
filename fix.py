import argparse
import re
import sys
parser = argparse.ArgumentParser()
parser.add_argument('fix_filename')
args = parser.parse_args()

if(re.search('.txt$',args.fix_filename)==None):
    sys.exit('The input should be .tex file. Exit.')

print('Fix_filename:',args.fix_filename)

with open(args.fix_filename,'r') as source_file:
    source = source_file.read()
nl = 0
nl_1 = 0
for m in re.finditer('\[ *[012][\.\,][0-9]+\]',source):
    #提取.前面的数字
    t=int( re.search('(?<=[\[ ])[0123](?=[\.\,])',m.group()).group() )
    #提取.后面的数字
    n=int( re.search('(?<=[\.\,])[0-9]+(?=\])',m.group()).group() )
    if(t==1):
        if(n==nl):
            nl +=1
        else:
            source = source[:m.start()] + f'[{t}.{nl}]' + source[m.end():]
            # source = text.replace(text[m.start():m.end()],'[%d.%d]'%(t,nl))
            nl +=1
    if(t==2):
        if(n==nl_1):
            nl_1 +=1
        else:
            source = source[:m.start()] + f'[{t}.{nl_1}]' + source[m.end():]
            # source = text.replace(text[m.start():m.end()],'[%d.%d]'%(t,nl_1))
            nl_1 +=1
with open('fix_'+args.fix_filename,'w') as f:
    f.write(source)
print('The',args.fix_filename,' has been corrected')