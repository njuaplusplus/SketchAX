# Description

This is the benchmark [reverse.sk](http://people.csail.mit.edu/asolar/gal/reverse.sk.html) from Sketch.
But `sketch reverse_pbe_fixed.sk` raises an error. To be checked later.

```
SKETCH version 1.7.4
Benchmark = reverse_pbe_fixed.sk
Error: input ids cannot be zero (addAndClause)

ERROR WAS IN THE FOLLOWING NODE: name_14__AND



*** Rejected
    [1508771430.7290 - ERROR] [SKETCH] Sketch Not Resolved Error: Error: input ids cannot be zero (addAndClause)

ERROR WAS IN THE FOLLOWING NODE: name_14__AND



*** Rejected
The sketch could not be resolved.
    [1508771430.7320 - DEBUG] [SKETCH] stack trace written to file: /home/aplusplus/.sketch/tmp/stacktrace.txt
    [1508771430.7330 - DEBUG] Backend solver input file at /home/aplusplus/.sketch/tmp/reverse_pbe_fixed.sk/input0.tmp
Total time = 3647
```

But it is fixed by explicitly providing all the assertions.
