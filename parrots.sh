amount=10

for ((c=0; c<amount; c++))
do
    gnome-terminal -- curl parrot.live
    sleep 0.2
done
