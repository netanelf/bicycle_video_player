#!/bin/bash
randomKeys=(Shift_L Shift_R Control_L Control_R)
keysCount=${#randomKeys[*]}
while [  true ]; do 
  #random sign
  sign='+'
  if [ $((RANDOM%2+0)) -eq 0 ]
  then sign='-'
  fi
  #random mouse coordinates
  x=$((RANDOM%50+1))
  y=$((RANDOM%50+1))
  #mouse move
  xte "mousermove $sign$x $sign$y"
  #random key press
  randomKey=${randomKeys[$((RANDOM%$keysCount+0))]}
  xte "key $randomKey"
  sleep 10
done
