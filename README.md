# duplis
Duplis stands for 'Duplicate Symbols'

if you are executable consists of several static libs and dynamic libs ; then are high chances that many symbols in 
executable are replicated in dynamic libs too. This is dangerous situation, and it can cause the aborts/crashes and 
won't be able to debug such crashes.
duplis tool will be help in such  situation. you can use duplis tool with your executable, and it will generate the 
list of duplicate symbols for you.

```
kmg@kmgs-MacBook-Pro duplis % ./duplis --help
usage: duplis [-h] -i IFILE [-l LFILE] [-g GREP] [-o OFILE]

duplis

options:
  -h, --help            show this help message and exit
  -i IFILE, --ifile IFILE
                        Input executable or lib file
  -l LFILE, --lfile LFILE
                        lib file to find the duplicate, if not supplied lib extracted from input file
  -g GREP, --grep GREP  grep for NM
  -o OFILE, --ofile OFILE
                        Output/Results txt file

Please report issues at https://github.com/kmgowda/duplis
```




