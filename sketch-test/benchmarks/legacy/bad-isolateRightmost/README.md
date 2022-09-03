# Description

This is the benchmark [isolateRightmost.sk](http://people.csail.mit.edu/asolar/gal/isolateRightmost.sk.html) from Sketch.
We change its specification by silly examples to make it fail, and then use the k-rotation property to fix it.
We check the equivalence by letting Sketch verify `isolate0sk0 implements isolate0sk1`.

**Problem:** In `compress_pbe.sk` because of the non-deterministic feature of Sketch, with PBE we can sometimes synthesize correct
code, while sometimes we cannot. How to address this?

The order of the examples matters.
It seems Sketch consumes the examples one by one.

The same examples, but in different orders, can lead Sketch to synthesize different programs.

# Original Benchmark with specification

I removed some unused functions, and added suffix 0 to the functions' names.

## isolateRightmost.sk

```c
int W = 32;

bit[W] isolate0 (bit[W] x) {
    bit[W] ret = 0;
    for (int i = 0; i < W; i++)
        if (!x[i]) { ret[i] = 1; return ret;  }
}

generator bit[W] gen(bit[W] x, int bnd){
    assert bnd > 0;
    if(??) return x;
    if(??) return ??;
    if(??) return ~gen(x, bnd-1);
    if(??){
        return {| gen(x, bnd-1) (+ | & | ^) gen(x, bnd-1) |};
    }
}

bit[W] isolate0sk0 (bit[W] x)  implements isolate0 {
    return gen(x, 3);
}
```

## output

Result of executing `sketch --bnd-unroll-amnt 100 isolateRightmost.sk`:

```c
SKETCH version 1.7.4
Benchmark = isolateRightmost.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*isolate..htmost.sk:5*/

void isolate0 (bit[32] x, ref bit[32] _out)/*isolate..htmost.sk:5*/
{
  _out = ((bit[32])0);
  _out = ((bit[32])0);
  for(int i = 0; i < 32; i = i + 1)/*Canonical*/
  {
    if(!(x[i]))/*isolate..htmost.sk:8*/
    {
      _out[i] = 1;
      return;
    }
  }
}
/*isolate..htmost.sk:21*/

void isolate0sk0 (bit[32] x, ref bit[32] _out)  implements isolate0/*isolate..htmost.sk:21*/
{
  _out = ((bit[32])0);
  bit[32] _out_s18 = {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  _out = (x + _out_s18) & (!(x));
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 878
```

# Modified by examples

The sketch (i.e. code with holes) is same with the above one. I just removed the `isolate0`
specification and add the examples in `constraints`. This make the Sketch synthesize wrong code.

## failed PBE

```c
int W = 32;

generator bit[W] gen(bit[W] x, int bnd){
    assert bnd > 0;
    if(??) return x;
    if(??) return ??;
    if(??) return ~gen(x, bnd-1);
    if(??){
        return {| gen(x, bnd-1) (+ | & | ^) gen(x, bnd-1) |};
    }
}

bit[W] isolate0sk1 (bit[W] x) {
    return gen(x, 3);
}

harness void constraints() {
    assert isolate0sk1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})
                   == {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    assert isolate0sk1({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})
                   == {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    assert isolate0sk1({0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})
                   == {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
}
```

## failed output

Result of executing `sketch --bnd-unroll-amnt 100 isolateRightmost_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = isolateRightmost_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*isolate..st_pbe.sk:19*/

void constraints ()/*isolate..st_pbe.sk:19*/
{
  bit[32] _out_s2 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  isolate0sk1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s2);
  assert (_out_s2 == ({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at isolate..st_pbe.sk:20 (0)
  bit[32] _out_s4 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  isolate0sk1({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s4);
  assert (_out_s4 == ({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at isolate..st_pbe.sk:22 (0)
  bit[32] _out_s6 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  isolate0sk1({0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s6);
  assert (_out_s6 == ({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at isolate..st_pbe.sk:24 (0)
}
/*isolate..st_pbe.sk:19*/

void constraints__Wrapper ()  implements constraints__WrapperNospec/*isolate..st_pbe.sk:19*/
{
  constraints();
}
/*isolate..st_pbe.sk:19*/

void constraints__WrapperNospec ()/*isolate..st_pbe.sk:19*/
{ }
/*isolate..st_pbe.sk:15*/

void isolate0sk1 (bit[32] x, ref bit[32] _out)/*isolate..st_pbe.sk:15*/
{
  _out = ((bit[32])0);
  bit[32] _out_s8 = {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  _out = _out_s8;
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 957
```

## Fix it using k-rotation
We generate all the `W` examples, that is, the rotations and the corresponding outputs.

```c
harness void constraints() {
    assert_all_rotations({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
                         {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
}

bit[N] k_rotation(int N, bit[N] x, int k) {
    if (k == 0 || N == 0) {
        return x;
    }
    k = k % N;
    if (k < 0) {
        // rotate k elements leftwards
        // it is equal to rotate N-k elements rightwards.
        k = N+k;
    }
    int l = k;
    bit[l] tmp = x[N-l::l];
    x[l::N-l] = x[0::N-l];
    x[0::l] = tmp;
    return x;
}

void assert_all_rotations(bit[W] x, bit[W] o) {
    assert isolate0sk1(x) == o;
    if (o == ((bit[W])0) || x == ((bit[W])0)) {
        // In this case, rotation is useless
        return;
    }
    for (int i=1; i<W; ++i) {
        x = k_rotation(W, x, 1);
        if (x[0] == 1) {
            o = k_rotation(W, o, 1);
        } else {
            o = ((bit[W])1);
        }
        assert isolate0sk1(x) == o;
    }
}
```

## output

Result of executing `sketch --bnd-unroll-amnt 100 isolateRightmost_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = isolateRightmost_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*isolate..st_pbe.sk:48*/

void assert_all_rotations (bit[32] x_0, bit[32] o_1)/*isolate..st_pbe.sk:48*/
{
  bit[32] o = o_1;
  bit[32] x = x_0;
  bit[32] _out_s2 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  isolate0sk1(x_0, _out_s2);
  assert (_out_s2 == o_1); //Assert at isolate..st_pbe.sk:49 (0)
  if((o_1 == (((bit[32])0))) || (x_0 == (((bit[32])0))))/*isolate..st_pbe.sk:50*/
  {
    return;
  }
  for(int i = 1; i < 32; i = i + 1)/*Canonical*/
  {
    bit[32] x_s4 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    k_rotation(32, x, 1, x_s4);
    x = x_s4;
    if((x_s4[0]) == 1)/*isolate..st_pbe.sk:56*/
    {
      bit[32] o_s6 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
      k_rotation(32, o, 1, o_s6);
      o = o_s6;
    }
    else
    {
      o = ((bit[32])1);
    }
    bit[32] _out_s8 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    isolate0sk1(x_s4, _out_s8);
    assert (_out_s8 == o); //Assert at isolate..st_pbe.sk:61 (0)
  }
}
/*isolate..st_pbe.sk:19*/

void constraints ()/*isolate..st_pbe.sk:19*/
{
  assert_all_rotations({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
}
/*isolate..st_pbe.sk:19*/

void constraints__Wrapper ()  implements constraints__WrapperNospec/*isolate..st_pbe.sk:19*/
{
  constraints();
}
/*isolate..st_pbe.sk:19*/

void constraints__WrapperNospec ()/*isolate..st_pbe.sk:19*/
{ }
/*isolate..st_pbe.sk:15*/

void isolate0sk1 (bit[32] x, ref bit[32] _out)/*isolate..st_pbe.sk:15*/
{
  _out = ((bit[32])0);
  bit[32] _out_s26 = {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  _out = (!(x)) & (x + _out_s26);
  return;
}
/*isolate..st_pbe.sk:31*/

void k_rotation (int N, bit[N] x_0, int k_1, ref bit[N] _out)/*isolate..st_pbe.sk:31*/
{
  _out = ((bit[N])0);
  int k = k_1;
  bit[N] x = x_0;
  if((k_1 == 0) || (N == 0))/*isolate..st_pbe.sk:32*/
  {
    _out = x_0;
    return;
  }
  k = k_1 % N;
  if(k < 0)/*isolate..st_pbe.sk:36*/
  {
    k = N + k;
  }
  bit[k] tmp = x_0[N - k::k];
  x[k::N - k] = x_0[0::N - k];
  x[0::k] = tmp;
  _out = x;
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 1335
```
