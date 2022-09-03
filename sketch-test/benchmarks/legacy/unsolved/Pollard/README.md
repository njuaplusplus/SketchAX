# Description

This is the benchmark [Pollard.sk](http://people.csail.mit.edu/asolar/gal/Pollard.sk.html) from Sketch.
However Sketch synthesized the wrong program.

The output from Sketch is:

```c
SKETCH version 1.7.4
Benchmark = /tmp/1508352399396358.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*1508352..396358.sk:7*/
 
void dup (int[17] in, ref bit _out)/*1508352..396358.sk:7*/
{
  _out = 0;
  int[17] tab = ((int[17])0);
  for(int i = 0; i < 17; i = i + 1)/*Canonical*/
  {
    tab[in[i]] = (tab[in[i]]) + 1;
  }
  int count = 0;
  for(int i_0 = 0; i_0 < 17; i_0 = i_0 + 1)/*Canonical*/
  {
    if((tab[i_0]) > 1)/*1508352..396358.sk:13*/
    {
      count = count + 1;
    }
  }
  if(count >= 1)/*1508352..396358.sk:14*/
  {
    _out = 1;
    return;
  }
  _out = 0;
  return;
}
/*1508352..396358.sk:33*/
 
void dupSketched (int[17] in, ref bit _out)  implements dup/*1508352..396358.sk:33*/
{
  _out = 0;
  int count3 = 0;
  for(int i = 0; i < 17; i = i + 1)/*Canonical*/
  {
    if((in[i]) == 16)/*1508352..396358.sk:60*/
    {
      count3 = count3 + 1;
    }
  }
  if(count3 >= 18)/*1508352..396358.sk:62*/
  {
    _out = 0;
    return;
  }
  _out = 1;
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 5276
```

It seems that `dupSketched` always returns `1` except for the array consisting of all 16. Is this related to the search space of the input in Sketch?

```c
    assert dupSketched({16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16}) == 0;
    assert dup({16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16}) == 1;
```
