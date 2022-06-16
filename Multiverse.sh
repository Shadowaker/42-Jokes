
# This script needs Matrix.py

amount=50

for ((c=0; c<amount; c++))
do
    osascript -e 'tell app "Terminal"
        do script "python3 Desktop/p.py"
    end tell'
    sleep 0.2
done

for ((c=0; c<amount; c++))
do
    osascript -e 'tell app "Terminal"
        do script "curl parrot.live"
    end tell'
    sleep 0.2
done
