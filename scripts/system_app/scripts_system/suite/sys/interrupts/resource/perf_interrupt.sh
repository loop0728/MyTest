casename=$(basename $1 .json)
resultpath=/mnt/out/Interrupts/$casename

mkdir -p $resultpath

rm -rf perf.data

./perfbin/perf record -e irq:irq_handler_entry -e irq:irq_handler_exit -e irq:softirq_entry -e irq:softirq_exit -a -g -o perf.data -- sleep 10

sleep 5

./perfbin/perf script > $resultpath/irq_report.txt

echo "========================irq_handler count==============================" | tee $resultpath/interrupt_result.txt

awk '/irq_handler_entry/ { start[$6] = gensub(/:$/, "", "g", $4) } /irq_handler_exit/ { end[$6] = gensub(/:$/, "", "g", $4); print $6, (end[$6] - start[$6]) * 1000, $7, $3 }' /mnt/out/Interrupts/irq_report.txt | awk '!/kernel.kallsyms/' | awk '{ if ($2 > max[$1]) max[$1] = $2; count[$1]++ ; alin[$1] = $3; cpu[$1] = $4 } END { for (name in max) print name, max[name], count[name], alin[name], cpu[name] }' | sort -k2nr | tee -a $resultpath/interrupt_result.txt

echo "=======================/proc/interrupts================================" | tee -a $resultpath/interrupt_result.txt
cat /proc/interrupts | tee -a $resultpath/interrupt_result.txt

echo "=======================softirq count===================================" | tee -a $resultpath/interrupt_result.txt
awk '/softirq_entry/ { start[$6] = gensub(/:$/, "", "g", $4) } /softirq_exit/ { end[$6] = gensub(/:$/, "", "g", $4); print $6, (end[$6] - start[$6]) * 1000, $7, $3 }' /mnt/out/Interrupts/irq_report.txt  | awk '!/kernel.kallsyms/'| awk '{ if ($2 > max[$1]) max[$1] = $2; count[$1]++ ; alin[$1] = $3; cpu[$1] = $4 } END { for (name in max) print name, max[name], count[name], alin[name], cpu[name] }' | sort -k2nr | tee -a $resultpath/interrupt_result.txt

echo "=======================/proc/softirqs==================================" | tee -a $resultpath/interrupt_result.txt
cat /proc/softirqs | tee -a $resultpath/interrupt_result.txt
