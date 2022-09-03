# Description

This is the benchmark [compress.sk](http://people.csail.mit.edu/asolar/gal/compress.sk.html) from Sketch.
We change its specification by silly examples to make it fail, and then use the k-rotation property to fix it.
We check the equivalence by letting Sketch verify `fast0 implements fast1`.

**Problem:** because of the non-deterministic feature of Sketch, with PBE we can sometimes synthesize correct
code, while sometimes we cannot. How to address this?

# Original Benchmark with specification

I removed some unused functions, and added suffix 0 to the functions' names.

## compress.sk

```c
int W = 16;

bit[W] compress(bit[W] x, bit[W] m){
  int i=0;
  bit[W] out = 0;
  for(int j=0; j<W; ++j){
      if(m[j]){
        out[i] = x[j];
        i = i+1;
      }
  }
  return out;
}

bit[W] xor_reduce0(bit[W] in){
  bit[W] out = 0;
  out[0] = in[0];
  for(int i=1; i<W; ++i){
      out[i] = in[i] ^ out[i-1];
  }
  return out;
}

bit[W] xor_reduceFast0(bit[W] in) implements xor_reduce0{
    bit[W] out = in;
    repeat(??){
        out = (out<<?? & ??) ^ (out<<?? & ??);
    }
    return out;
  }

generator bit[W] maskedShift(bit[W] in, bit[W] mask, int s){ /* automatically rewritten */
    bit[W] t = in & mask;
    return (in ^ t) | t >> s;
}

bit[W] fast0(bit[W] x, bit[W] m) implements compress{
    bit[W] mk=0;
    bit[W] mp=0;
    bit[W] mv=0;
    bit[W] t=0;
    int i=0;
    x = x & m;
    mk = (!m) << ??;
    repeat(??){
      mp = xor_reduceFast0(mk);
      mv = mp & m;
      m = maskedShift(m, mv, ??);
      x = maskedShift(x, mv, ??);
      mk = mk & !mp;
    }
    return x;
}
```

## output

Result of executing `sketch --bnd-unroll-amnt 100 compress.sk`:

```c
SKETCH version 1.7.4
Benchmark = compress.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*compress.sk:5*/

void compress (bit[16] x, bit[16] m, ref bit[16] _out)/*compress.sk:5*/
{
  _out = ((bit[16])0);
  _out = ((bit[16])0);
  int i = 0;
  for(int j = 0; j < 16; j = j + 1)/*Canonical*/
  {
    if(m[j])/*compress.sk:9*/
    {
      _out[i] = x[j];
      i = i + 1;
    }
  }
  return;
}
/*compress.sk:39*/

void fast0 (bit[16] x_0, bit[16] m_1, ref bit[16] _out)  implements compress/*compress.sk:39*/
{
  _out = ((bit[16])0);
  bit[16] x = x_0;
  x = x_0 & m_1;
  bit[16] mk = (!(m_1)) << 1;
  bit[16] mp_s1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast0(mk, mp_s1);
  bit[16] mv = mp_s1 & m_1;
  bit[16] t = m_1 & mv;
  bit[16] m_s3 = (m_1 ^ t) | (t >> 1);
  bit[16] t_0 = x & mv;
  bit[16] x_s5 = (x ^ t_0) | (t_0 >> 1);
  mk = mk & (!(mp_s1));
  bit[16] mp_s1_0 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast0(mk, mp_s1_0);
  mv = mp_s1_0 & m_s3;
  bit[16] t_1 = m_s3 & mv;
  bit[16] m_s3_0 = (m_s3 ^ t_1) | (t_1 >> 2);
  bit[16] t_2 = x_s5 & mv;
  bit[16] x_s5_0 = (x_s5 ^ t_2) | (t_2 >> 2);
  mk = mk & (!(mp_s1_0));
  bit[16] mp_s1_1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast0(mk, mp_s1_1);
  mv = mp_s1_1 & m_s3_0;
  bit[16] t_3 = m_s3_0 & mv;
  bit[16] t_4 = x_s5_0 & mv;
  bit[16] x_s5_1 = (x_s5_0 ^ t_4) | (t_4 >> 4);
  mk = mk & (!(mp_s1_1));
  bit[16] mp_s1_2 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast0(mk, mp_s1_2);
  mv = mp_s1_2 & ((m_s3_0 ^ t_3) | (t_3 >> 4));
  bit[16] t_5 = x_s5_1 & mv;
  _out = (x_s5_1 ^ t_5) | (t_5 >> 8);
  return;
}
/*compress.sk:17*/

void xor_reduce0 (bit[16] in, ref bit[16] _out)/*compress.sk:17*/
{
  _out = ((bit[16])0);
  _out = ((bit[16])0);
  _out[0] = in[0];
  for(int i = 1; i < 16; i = i + 1)/*Canonical*/
  {
    _out[i] = (in[i]) ^ (_out[i - 1]);
  }
  return;
}
/*compress.sk:26*/

void xor_reduceFast0 (bit[16] in, ref bit[16] _out)  implements xor_reduce0/*compress.sk:26*/
{
  _out = ((bit[16])0);
  _out = in;
  _out = ((in << 3) & ({0,0,0,1,0,1,0,0,1,0,0,0,0,0,1,0})) ^ ((in << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 3) & ({0,0,0,1,0,1,0,0,1,0,0,0,0,0,1,0})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 4) & ({0,0,0,0,1,1,0,1,1,1,1,1,1,1,0,0}));
  _out = ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 8) & ({0,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0}));
  _out = ((_out << 2) & ({0,0,1,0,1,1,0,1,1,1,1,1,1,1,0,0})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 2) & ({0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,1}));
  _out = ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 1) & ({0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 34696
```

# Modified by examples

The sketch (i.e. code with holes) is same with the above one. I just removed the `compress`
specification and add the examples in `constraints`. This make the Sketch synthesize wrong code.

## failed PBE

```c
//@Description Given a bit-vector and a bit-mask, the task is select from the bit-vector 
all the bits selected by the bit-mask and pack them in the beginning of the word.

int W = 16;

harness void constraints() {
    assert fast1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}) == {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    assert fast1({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}) == {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    assert fast1({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0}) == {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
}

bit[W] xor_reduce1(bit[W] in){
  bit[W] out = 0;
  out[0] = in[0];
  for(int i=1; i<W; ++i){
      out[i] = in[i] ^ out[i-1];
  }
  return out;
}

bit[W] xor_reduceFast1(bit[W] in) implements xor_reduce1{
    bit[W] out = in;
    repeat(??){
        out = (out<<?? & ??) ^ (out<<?? & ??);
    }
    return out;
  }

generator bit[W] maskedShift(bit[W] in, bit[W] mask, int s){ /* automatically rewritten */
    bit[W] t = in & mask;
    return (in ^ t) | t >> s;
}

bit[W] fast1(bit[W] x, bit[W] m){
    bit[W] mk=0;
    bit[W] mp=0;
    bit[W] mv=0;
    bit[W] t=0;
    int i=0;
    x = x & m;
    mk = (!m) << ??;
    repeat(??){
      mp = xor_reduceFast1(mk);
      mv = mp & m;
      m = maskedShift(m, mv, ??);
      x = maskedShift(x, mv, ??);
      mk = mk & !mp;
    }
    return x;
}
```

## failed output

Result of executing `sketch --bnd-unroll-amnt 100 compress_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = compress_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*compress_pbe.sk:5*/

void constraints ()/*compress_pbe.sk:5*/
{
  bit[16] _out_s1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  fast1({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s1);
  assert (_out_s1 == ({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at compress_pbe.sk:6 (0)
  bit[16] _out_s3 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  fast1({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s3);
  assert (_out_s3 == ({0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at compress_pbe.sk:7 (0)
  bit[16] _out_s5 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  fast1({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0}, _out_s5);
  assert (_out_s5 == ({1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0})); //Assert at compress_pbe.sk:8 (0)
}
/*compress_pbe.sk:5*/

void constraints__Wrapper ()  implements constraints__WrapperNospec/*compress_pbe.sk:5*/
{
  constraints();
}
/*compress_pbe.sk:5*/

void constraints__WrapperNospec ()/*compress_pbe.sk:5*/
{ }
/*compress_pbe.sk:78*/

void fast1 (bit[16] x_0, bit[16] m_1, ref bit[16] _out)/*compress_pbe.sk:78*/
{
  _out = ((bit[16])0);
  bit[16] x = x_0;
  x = x_0 & m_1;
  bit[16] mp_s7 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast1((!(m_1)) << 0, mp_s7);
  bit[16] t = x & (mp_s7 & m_1);
  _out = (x ^ t) | (t >> 1);
  return;
}
/*compress_pbe.sk:56*/

void xor_reduce1 (bit[16] in, ref bit[16] _out)/*compress_pbe.sk:56*/
{
  _out = ((bit[16])0);
  _out = ((bit[16])0);
  _out[0] = in[0];
  for(int i = 1; i < 16; i = i + 1)/*Canonical*/
  {
    _out[i] = (in[i]) ^ (_out[i - 1]);
  }
  return;
}
/*compress_pbe.sk:65*/

void xor_reduceFast1 (bit[16] in, ref bit[16] _out)  implements xor_reduce1/*compress_pbe.sk:65*/
{
  _out = ((bit[16])0);
  _out = in;
  _out = ((in << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((in << 8) & ({0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1}));
  _out = ((_out << 4) & ({0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 1) & ({0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 1) & ({0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 2) & ({0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 3230
```

## Fix it using k-rotation
We generate all the `W` examples, that is, the rotations and the corresponding outputs.

```c
harness void constraints() {
    assert_all_rotations({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
}

int num_of_ones_in_mask(bit[W] mask) {
    int n = 0;
    for (int i=0; i<W; ++i) {
        if(mask[i]) {
            n += 1;
        }
    }
    return n;
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

void assert_all_rotations(bit[W] x, bit[W] m, bit[W] o) {
    assert fast1(x,m) == o;
    int s = num_of_ones_in_mask(m);
    bit[s] t = o[0::s];
    for (int i=1; i<W; ++i) {
        x = k_rotation(W, x, 1);
        m = k_rotation(W, m, 1);
        if (m[0] == 1) {
            t = k_rotation(s, t, 1);
        }
        assert fast1(x,m) == (bit[W])t;
    }
}

```

## output

Result of executing `sketch --bnd-unroll-amnt 100 compress_pbe.sk`:

```c
SKETCH version 1.7.4
Benchmark = compress_pbe.sk
/* BEGIN PACKAGE ANONYMOUS*/
/*compress_pbe.sk:42*/

void assert_all_rotations (bit[16] x_0, bit[16] m_1, bit[16] o)/*compress_pbe.sk:42*/
{
  bit[16] m = m_1;
  bit[16] x = x_0;
  bit[16] _out_s1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  fast1(x_0, m_1, _out_s1);
  assert (_out_s1 == o); //Assert at compress_pbe.sk:43 (0)
  int s_s3 = 0;
  num_of_ones_in_mask(m_1, s_s3);
  int s;
  s = s_s3;
  bit[s] t = o[0::s_s3];
  for(int i = 1; i < 16; i = i + 1)/*Canonical*/
  {
    bit[16] x_s5 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    k_rotation(16, x, 1, x_s5);
    x = x_s5;
    bit[16] m_s7 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    k_rotation(16, m, 1, m_s7);
    m = m_s7;
    if((m_s7[0]) == 1)/*compress_pbe.sk:49*/
    {
      bit[s] t_s9;
      k_rotation(s_s3, t, 1, t_s9);
      t = t_s9;
    }
    bit[16] _out_s11 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    fast1(x_s5, m_s7, _out_s11);
    assert (_out_s11 == (((bit[16])t))); //Assert at compress_pbe.sk:52 (0)
  }
}
/*compress_pbe.sk:5*/

void constraints ()/*compress_pbe.sk:5*/
{
  assert_all_rotations({0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0}, {0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0}, {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0});
}
/*compress_pbe.sk:5*/

void constraints__Wrapper ()  implements constraints__WrapperNospec/*compress_pbe.sk:5*/
{
  constraints();
}
/*compress_pbe.sk:5*/

void constraints__WrapperNospec ()/*compress_pbe.sk:5*/
{ }
/*compress_pbe.sk:78*/

void fast1 (bit[16] x_0, bit[16] m_1, ref bit[16] _out)/*compress_pbe.sk:78*/
{
  _out = ((bit[16])0);
  bit[16] x = x_0;
  x = x_0 & m_1;
  bit[16] mk = (!(m_1)) << 0;
  bit[16] mp_s13 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast1(mk, mp_s13);
  bit[16] mv = mp_s13 & m_1;
  bit[16] t = m_1 & mv;
  bit[16] m_s15 = (m_1 ^ t) | (t >> 1);
  bit[16] t_0 = x & mv;
  bit[16] x_s17 = (x ^ t_0) | (t_0 >> 1);
  mk = mk & (!(mp_s13));
  bit[16] mp_s13_0 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast1(mk, mp_s13_0);
  mv = mp_s13_0 & m_s15;
  bit[16] t_1 = m_s15 & mv;
  bit[16] m_s15_0 = (m_s15 ^ t_1) | (t_1 >> 2);
  bit[16] t_2 = x_s17 & mv;
  bit[16] x_s17_0 = (x_s17 ^ t_2) | (t_2 >> 2);
  mk = mk & (!(mp_s13_0));
  bit[16] mp_s13_1 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast1(mk, mp_s13_1);
  mv = mp_s13_1 & m_s15_0;
  bit[16] t_3 = m_s15_0 & mv;
  bit[16] t_4 = x_s17_0 & mv;
  bit[16] x_s17_1 = (x_s17_0 ^ t_4) | (t_4 >> 4);
  mk = mk & (!(mp_s13_1));
  bit[16] mp_s13_2 = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  xor_reduceFast1(mk, mp_s13_2);
  mv = mp_s13_2 & ((m_s15_0 ^ t_3) | (t_3 >> 4));
  bit[16] t_5 = x_s17_1 & mv;
  _out = (x_s17_1 ^ t_5) | (t_5 >> 8);
  return;
}
/*compress_pbe.sk:25*/

void k_rotation (int N, bit[N] x_0, int k_1, ref bit[N] _out)/*compress_pbe.sk:25*/
{
  _out = ((bit[N])0);
  int k = k_1;
  bit[N] x = x_0;
  if((k_1 == 0) || (N == 0))/*compress_pbe.sk:26*/
  {
    _out = x_0;
    return;
  }
  k = k_1 % N;
  if(k < 0)/*compress_pbe.sk:30*/
  {
    k = N + k;
  }
  bit[k] tmp = x_0[N - k::k];
  x[k::N - k] = x_0[0::N - k];
  x[0::k] = tmp;
  _out = x;
  return;
}
/*compress_pbe.sk:15*/

void num_of_ones_in_mask (bit[16] mask, ref int _out)/*compress_pbe.sk:15*/
{
  _out = 0;
  _out = 0;
  for(int i = 0; i < 16; i = i + 1)/*Canonical*/
  {
    if(mask[i])/*compress_pbe.sk:18*/
    {
      _out = _out + 1;
    }
  }
  return;
}
/*compress_pbe.sk:56*/

void xor_reduce1 (bit[16] in, ref bit[16] _out)/*compress_pbe.sk:56*/
{
  _out = ((bit[16])0);
  _out = ((bit[16])0);
  _out[0] = in[0];
  for(int i = 1; i < 16; i = i + 1)/*Canonical*/
  {
    _out[i] = (in[i]) ^ (_out[i - 1]);
  }
  return;
}
/*compress_pbe.sk:65*/

void xor_reduceFast1 (bit[16] in, ref bit[16] _out)  implements xor_reduce1/*compress_pbe.sk:65*/
{
  _out = ((bit[16])0);
  _out = in;
  _out = ((in << 2) & ({0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((in << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 8) & ({0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 4) & ({0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  _out = ((_out << 1) & ({0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1})) ^ ((_out << 0) & ({1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}));
  return;
}
/* END PACKAGE ANONYMOUS*/
[SKETCH] DONE
Total time = 5303
```
