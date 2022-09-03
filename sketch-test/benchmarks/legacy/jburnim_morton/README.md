# Description

This is the benchmark [jburnim_morton.sk](http://people.csail.mit.edu/asolar/gal/jburnim_morton.sk.html) from Sketch.
We change its specification by silly examples to make it fail, and then use the permutation property to fix it.
We check the equivalence by letting Sketch verify `sketch0 implements sketch1`.

**Problem:** the non-deterministic feature of Sketch.

# Original Benchmark with specification

I removed some unused functions, and added suffix 0 to the functions' names.

## compress.sk

```c
int W = 16;

bit[2*W] interleave_bits(bit[W] x, bit[W] y) {
  bit[2*W] ret = 0;
  for (int i = 0; i < W; i++) {
    ret[i*2] = x[i];
    ret[i*2+1] = y[i];
  }
  return ret;
}

bit[2*W] sketch0(bit[W] x, bit[W] y) implements interleave_bits {
  // Idea: It should be possible to shift all of the bits "in parallel"
  // using only log2(W) shifts.
  bit[2*W] x2 = x;
  int pt = 4*W;
  repeat(??) {
    int t = ??;
    // Shift some of the bits, and mask out their original positions.
    x2 = (x2 | (x2 << t)) & ??;
    assert t < pt; pt = t;
  }

  bit[2*W] y2 = y;
  repeat(??) {
    // Shift some of the bits, and mask out their original positions.
    y2 = (y2 | (y2 << ??)) & ??;
  }

  return x2 | (y2 << 1);
}
```

## output

Result of executing `sketch --bnd-unroll-amnt 20 jburnim_morton.sk`:

```c
SKETCH version 1.7.4
Benchmark = jburnim_morton.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*jburnim_morton.sk:18*/

void interleave_bits (bit[16] x, bit[16] y, ref bit[32] _out)/*jburnim_morton.sk:18*/
{
  _out = ((bit[32])0);
  _out = ((bit[32])0);
  for(int i = 0; i < 16; i = i + 1)/*Canonical*/
  {
    _out[i * 2] = x[i];
    _out[(i * 2) + 1] = y[i];
  }
  return;
}
/*jburnim_morton.sk:27*/

void sketch0 (bit[16] x, bit[16] y, ref bit[32] _out)  implements interleave_bits/*jburnim_morton.sk:27*/
{
  _out = ((bit[32])0);
  bit[32] x2 = ((bit[32])x);
  x2 = (x2 | (x2 << 8)) & ({1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0});
  x2 = (x2 | (x2 << 4)) & ({1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0});
  x2 = (x2 | (x2 << 2)) & ({1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0});
  x2 = (x2 | (x2 << 1)) & ({1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0});
  bit[32] y2 = ((bit[32])y);
  y2 = (y2 | (y2 << 8)) & ({1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0});
  y2 = (y2 | (y2 << 4)) & ({1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0});
  y2 = (y2 | (y2 << 2)) & ({1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0});
  y2 = (y2 | (y2 << 1)) & ({1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0});
  _out = x2 | (y2 << 1);
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 43698

```

# Modified by examples

The sketch (i.e. code with holes) is same with the above one. I just removed the `interleave_bits`
specification and add the examples in `constraints`. This make the Sketch synthesize wrong code.

## failed PBE

```c
int W = 16;

bit[2*W] sketch1(bit[W] x, bit[W] y) {
  // Idea: It should be possible to shift all of the bits "in parallel"
  // using only log2(W) shifts.
  bit[2*W] x2 = x;
  int pt = 4*W;
  repeat(??) {
    int t = ??;
    // Shift some of the bits, and mask out their original positions.
    x2 = (x2 | (x2 << t)) & ??;
    assert t < pt; pt = t;
  }

  bit[2*W] y2 = y;
  repeat(??) {
    // Shift some of the bits, and mask out their original positions.
    y2 = (y2 | (y2 << ??)) & ??;
  }

  return x2 | (y2 << 1);
}

harness void constraints(int[W] ind) {
    assert sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})
                == {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0};

    assert sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})
                == {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1};

    assert sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0})
                == {0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0};

    assert sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1})
                == {1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1};
}
```

## failed output

Result of executing `sketch --bnd-unroll-amnt 20 jburnim_morton_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = jburnim_morton_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*jburnim..on_pbe.sk:24*/

void constraints (int[16] ind)/*jburnim..on_pbe.sk:24*/
{
  bit[32] _out_s1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1}, {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s1);
  assert (_out_s1 == ({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0})); //Assert at jburnim..on_pbe.sk:25 (0)
  bit[32] _out_s3 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, _out_s3);
  assert (_out_s3 == ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1})); //Assert at jburnim..on_pbe.sk:28 (0)
  bit[32] _out_s5 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0}, _out_s5);
  assert (_out_s5 == ({0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0})); //Assert at jburnim..on_pbe.sk:31 (0)
  bit[32] _out_s7 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, _out_s7);
  assert (_out_s7 == ({1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1})); //Assert at jburnim..on_pbe.sk:34 (0)
}
/*jburnim..on_pbe.sk:24*/

void constraints__Wrapper (int[16] ind)  implements constraints__WrapperNospec/*jburnim..on_pbe.sk:24*/
{
  constraints(ind);
}
/*jburnim..on_pbe.sk:24*/

void constraints__WrapperNospec (int[16] ind)/*jburnim..on_pbe.sk:24*/
{ }
/*jburnim..on_pbe.sk:3*/

void sketch1 (bit[16] x, bit[16] y, ref bit[32] _out)/*jburnim..on_pbe.sk:3*/
{
  _out = ((bit[32])0);
  bit[32] x2 = ((bit[32])x);
  x2 = (x2 | (x2 << 6)) & ({1,1,1,0,0,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0});
  x2 = (x2 | (x2 << 5)) & ({1,0,1,0,0,1,1,1,1,0,0,0,1,0,1,1,0,1,0,1,0,1,1,0,1,0,1,0,0,0,0,0});
  x2 = (x2 | (x2 << 4)) & ({1,0,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0,1,0,0,0,1,0,1,0,1,0});
  x2 = (x2 | (x2 << 3)) & ({1,0,1,1,0,0,1,1,0,0,1,1,0,0,1,0,0,0,1,1,0,1,1,0,0,1,1,0,0,0,1,1});
  x2 = (x2 | (x2 << 2)) & ({1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,1});
  bit[32] y2 = ((bit[32])y);
  y2 = (y2 | (y2 << 0)) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
  y2 = (y2 | (y2 << 30)) & ({1,1,1,0,1,1,1,0,0,1,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
  y2 = (y2 | (y2 << 20)) & ({1,1,0,0,0,0,0,0,0,1,1,0,0,1,0,1,0,0,0,0,1,1,0,0,0,0,1,0,0,0,0,1});
  y2 = (y2 | (y2 << 2)) & ({1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1});
  y2 = (y2 | (y2 << 3)) & ({1,0,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,1,1,0,1,1,0,1,0,0,0,0,0});
  y2 = (y2 | (y2 << 1)) & ({1,1,1,0,0,0,1,0,0,0,1,1,0,0,1,0,0,1,0,0,1,0,1,1,0,1,1,0,0,0,0,0});
  y2 = (y2 | (y2 << 2)) & ({1,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,1,1,0,1,1,0,0,1,0,0,1,1,0,0,0,0});
  y2 = (y2 | (y2 << 8)) & ({1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,0,0,0});
  _out = x2 | (y2 << 1);
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 919
```

## Fix it using permutation
We generate all the permutations of 3 examples.

```c
harness void constraints(int[W] ind) {
    assert sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})
                == {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0};

    assert sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})
                == {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1};

    assert sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0})
                == {0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0};

    assert sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1})
                == {1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1};

    assert_one_permutation({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
                           {0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0}, ind);

    assert_one_permutation({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                           {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1}, ind);

    assert_one_permutation({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0},{0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                            {1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1}, ind);
}

void assert_one_permutation(bit[W] x, bit[W] y, bit[2*W] o, int[W] ind) {
    if (!is_permutation(W, ind)) return;
    bit[W] xp = permute(W, x, ind);
    bit[W] yp = permute(W, y, ind);
    bit[2*W] op = 0;
    for (int i=0; i<W; ++i) {
        op[2*i] = o[2*ind[i]];
        op[2*i+1] = o[2*ind[i]+1];
    }
    assert sketch1(xp, yp) == op;
    // assert interleave_bits(xp,yp) == op;
}

bit is_permutation(int N, int[N] ind) {
    bit[N] res = 0;
    for (int i=0; i<N; ++i) {
        if (ind[i]<0 || ind[i]>=N || res[ind[i]] == 1) {
            return 0;
        } else {
            res[ind[i]] = 1;
        }
    }
    return 1;
}

bit[N] permute(int N, bit[N]x, int[N] ind){
    bit[N] res = 0;
    for(int i=0; i<N; ++i){
        res[i]= x[ind[i]];
    }
    return res;
}
```

## output

Result of executing `sketch --bnd-unroll-amnt 20 jburnim_morton_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = jburnim_morton_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*jburnim..on_pbe.sk:68*/

void assert_one_permutation (bit[16] x, bit[16] y, bit[32] o, int[16] ind)/*jburnim..on_pbe.sk:68*/
{
  bit _out_s9 = 0;
  is_permutation(16, ind, _out_s9);
  if(!(_out_s9))/*jburnim..on_pbe.sk:69*/
  {
    return;
  }
  bit[16] xp_s11 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  permute(16, x, ind, xp_s11);
  bit[16] yp_s13 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  permute(16, y, ind, yp_s13);
  bit[32] op = ((bit[32])0);
  for(int i = 0; i < 16; i = i + 1)/*Canonical*/
  {
    op[2 * i] = o[2 * (ind[i])];
    op[(2 * i) + 1] = o[(2 * (ind[i])) + 1];
  }
  bit[32] _out_s15 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1(xp_s11, yp_s13, _out_s15);
  assert (_out_s15 == op); //Assert at jburnim..on_pbe.sk:77 (0)
}
/*jburnim..on_pbe.sk:24*/

void constraints (int[16] ind)/*jburnim..on_pbe.sk:24*/
{
  bit[32] _out_s1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1}, {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s1);
  assert (_out_s1 == ({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0})); //Assert at jburnim..on_pbe.sk:25 (0)
  bit[32] _out_s3 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, _out_s3);
  assert (_out_s3 == ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1})); //Assert at jburnim..on_pbe.sk:28 (0)
  bit[32] _out_s5 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0}, _out_s5);
  assert (_out_s5 == ({0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0})); //Assert at jburnim..on_pbe.sk:31 (0)
  bit[32] _out_s7 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  sketch1({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, _out_s7);
  assert (_out_s7 == ({1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1})); //Assert at jburnim..on_pbe.sk:34 (0)
  assert_one_permutation({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0}, {0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,0}, ind);
  assert_one_permutation({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1}, ind);
  assert_one_permutation({1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0}, {0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1}, {1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1}, ind);
}
/*jburnim..on_pbe.sk:24*/

void constraints__Wrapper (int[16] ind)  implements constraints__WrapperNospec/*jburnim..on_pbe.sk:24*/
{
  constraints(ind);
}
/*jburnim..on_pbe.sk:24*/

void constraints__WrapperNospec (int[16] ind)/*jburnim..on_pbe.sk:24*/
{ }
/*jburnim..on_pbe.sk:81*/

void is_permutation (int N, int[N] ind, ref bit _out)/*jburnim..on_pbe.sk:81*/
{
  _out = 0;
  bit[N] res = ((bit[N])0);
  for(int i = 0; i < N; i = i + 1)/*Canonical*/
  {
    if((((ind[i]) < 0) || ((ind[i]) >= N)) || ((res[ind[i]]) == 1))/*jburnim..on_pbe.sk:84*/
    {
      _out = 0;
      return;
    }
    else
    {
      res[ind[i]] = 1;
    }
  }
  _out = 1;
  return;
}
/*jburnim..on_pbe.sk:93*/

void permute (int N, bit[N] x, int[N] ind, ref bit[N] _out)/*jburnim..on_pbe.sk:93*/
{
  _out = ((bit[N])0);
  _out = ((bit[N])0);
  for(int i = 0; i < N; i = i + 1)/*Canonical*/
  {
    _out[i] = x[ind[i]];
  }
  return;
}
/*jburnim..on_pbe.sk:3*/

void sketch1 (bit[16] x, bit[16] y, ref bit[32] _out)/*jburnim..on_pbe.sk:3*/
{
  _out = ((bit[32])0);
  bit[32] x2 = ((bit[32])x);
  x2 = (x2 | (x2 << 8)) & ({1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0});
  x2 = (x2 | (x2 << 4)) & ({1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0});
  x2 = (x2 | (x2 << 2)) & ({1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0});
  x2 = (x2 | (x2 << 1)) & ({1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0});
  bit[32] y2 = ((bit[32])y);
  y2 = (y2 | (y2 << 8)) & ({1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0});
  y2 = (y2 | (y2 << 4)) & ({1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0});
  y2 = (y2 | (y2 << 2)) & ({1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0});
  y2 = (y2 | (y2 << 1)) & ({1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0});
  _out = x2 | (y2 << 1);
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 39475
```
