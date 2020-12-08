import progressbar # python3 -m pip install progressbar2

CUSTOM_CHAR_LEN_MAP = {
	'█'  : 1,
}

PROGBAR_WIDGETS = [
	progressbar.Percentage(),
	' (', progressbar.SimpleProgress(), ') ',
	progressbar.Bar(marker='█', left=' |', right='| ', fill='_'),
	' ', progressbar.Timer(),
	' | ', progressbar.ETA(),
]

def ProgBarCustomLenFunc(value):

	total = 0
	for c in value:
		total += CUSTOM_CHAR_LEN_MAP.get(c, 1)

	return total

PROGBAR_ARGS = {
	'widgets' : PROGBAR_WIDGETS,
	'len_func' : ProgBarCustomLenFunc
}
