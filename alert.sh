say "This computer will turn off in..."

for i in {0..5}
do
	j=$(expr 5 - $i)
	say $j
	sleep 1s
done

say "AHAHAHAHA I'm joking."
