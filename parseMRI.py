def parseMRI(f):
    with open(f,'r') as fin:
        data = [x.strip() for x in fin]
    summary = []
    max_acc = -1
    bestparam = []
    for d in data:
        raw = d.split('{')[1].split('}')[1]
        if not ',' in raw:
            continue
        acc = float(d.split('{')[1].split('}')[1].split(',')[1].split('\'')[1].split()[2])
        if acc >  max_acc:
            max_acc = acc
            param = d.split('{')[1].split('}')[0].split(',')
            param_dic = {}
            for p in param:
                a = p.split('\'')
                param_dic['\%\{'+a[1]+'\}\%'] = a[3]

            bestparam = param_dic
    if len(bestparam) == 0:
        print 'Error: Can\'t find any final extremes usable! Check the mri.log file.'
    return bestparam
