def parseMRI(f,optimwrt_ori):
    optimwrt = optimwrt_ori.lower().capitalize()
    with open(f,'r') as fin:
        data = [x.strip() for x in fin]
    summary = []
    max_metric = float("-inf")
    bestparam = []
    for d in data:
        raw = d.split('{')[1].split('}')[1]
        if not 'Final Extremes' in raw:
            continue
	if optimwrt == 'Accuracy':
	    choice = 2
	    mlt = 1;
        elif optimwrt == 'Loss':
	    choice = 4
	    mlt = -1
        try:
            metric = mlt  * float(d.split('Final Extremes')[1].split(optimwrt)[1].split(')')[0].split(' ')[choice])
        except IndexError:
            metric = max_metric

        if metric >  max_metric:
            max_metric = metric
            param = d.split('{')[1].split('}')[0].split(',')
            param_dic = {}
            for p in param:
                a = p.split('\'')
                param_dic['\%\{'+a[1]+'\}\%'] = a[3]

            bestparam = param_dic
    if len(bestparam) == 0:
        print 'Error: Can\'t find any final extremes usable! Check the mri.log file.'
    return bestparam
