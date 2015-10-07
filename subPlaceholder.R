args = commandArgs(T)
infile = args[1]
placeholder = args[2]
value = args[3]
outfile = args[4]

placeholder = strsplit(placeholder,';')[[1]]
value= strsplit(value,';')[[1]]

rl=readLines(infile)
for (i in 1:length(value)){
	rl=gsub(placeholder[i],value[i],rl)
}

system(paste0('printf \'',paste0(rl,collapse='\n'),'\' > ',outfile))
