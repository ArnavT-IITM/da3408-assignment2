#!/bin/bash

N=20
URL=http://localhost:8080/predict

time_pass() {
    total=0
    for i in $(seq 1 $N); do
        t=$(curl -s -o /dev/null -w "%{time_total}" -X POST $URL \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"WIN a FREE iPhone now! Click here: bit.ly/xyz123 ref=$RUN-$i\"}")
        total=$(echo "$total + $t" | bc -l)
    done
    echo "scale=2; $total * 1000 / $N" | bc -l
}

RUN=$(date +%s)
curl -s -o /dev/null -X POST $URL -H 'Content-Type: application/json' -d '{"text":"warmup"}'

miss=$(time_pass)
hit=$(time_pass)

echo "cache MISS (first request for each message) : ${miss} ms average"
echo "cache HIT  (same messages, second time)     : ${hit} ms average"
echo "speedup: $(echo "scale=2; $miss / $hit" | bc -l)x"
