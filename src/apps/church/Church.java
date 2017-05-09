/*
 * Copyright (c) 2016,2017 GrammaTech Inc
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

import java.util.function.*;

public class Church {
    private final Lambda l;
    private Church(Lambda l) { this.l = l; }

    @FunctionalInterface
    public static interface Lambda {
        public Object apply(UnaryOperator<Object> f, Object x);
    }
    private static final Lambda zero = (f,x) -> x;
    public static final Church ZERO = new Church(zero);
    
    
    public boolean isZero() { return (Boolean) l.apply(x -> false, true); }

    public Church succ() {
        return new Church((f,x) -> f.apply(l.apply(f,x)));
    }

    // pred = \n. \f. \x. n (\g. \h. h (g f)) (\ u.x) (\ u.u)
    @SuppressWarnings("unchecked")
    public Church pred() {
        return new Church(
            (f, x) -> 
                ((Function<UnaryOperator<Object>,Object>) 
                l.apply(
                    g -> 
                        (Function<UnaryOperator<Object>,Object>) 
                        (h -> h.apply(((Function<UnaryOperator<Object>,Object>)g).apply(f))),
                    (Function<UnaryOperator<Object>,Object>) 
                    (u -> x))
                ).apply(u -> u)
        );
    }
    
    public boolean isEven() { return (Boolean) l.apply(x -> !(Boolean)x, true); }
    public boolean isOdd()  { return (Boolean) l.apply(x -> !(Boolean)x, false); }

    public Church add(Church other) {
        return new Church(
            (f, x) -> l.apply(f, other.l.apply(f,x))
        );
    }
    
    public Church sub(Church other) {
        return (Church) other.l.apply(x -> ((Church) x).pred(), this);
    }
    
    public Church mul(Church other) {
        return new Church(
            (f, x) -> l.apply(x_ -> other.l.apply(f,x_), x)
        );
    }
    
    public String toString() {
        return "\\f x." + (String) l.apply(x -> "(f " + x + ")","x");
    }
    public int toInt() { return (Integer) l.apply(x -> (Integer) x + 1, 0); }
    public static Church fromInt(int n) {
        if(n < 0)
            throw new IllegalArgumentException();
        Lambda l = zero;
        while(n-- != 0) {
            final Lambda l_ = l;
            l = (f,x) -> f.apply(l_.apply(f,x));
        }
        return new Church(l);
    }
    
    private static <T> void runUnaryG(String name, Function<Church,T> f, Church a) {
        System.out.println(name + "(" + a.toInt() + "): " + f.apply(a).toString());
    }
    private static void runUnary(String name, Function<Church,Church> f, Church a) {
        System.out.println(name + "(" + a.toInt() + "): " + f.apply(a).toInt());
    }
    private static void runBinary(String name, BiFunction<Church,Church,Church> f, Church a, Church b) {
        System.out.println("" + a.toInt() + " " + name + " " + b.toInt() + ": " + f.apply(a,b).toInt());
    }
    public static void main(String[] args) {
        Church a[] = new Church[10];
        a[0] = ZERO;
        for(int i=1;i<a.length;i++)
            a[i] = a[i-1].succ();
        runUnaryG("toString", Church::toString, a[0]);
        runUnaryG("toString", Church::toString, a[2]);
        runUnary("succ", Church::succ, a[0]);
        runUnary("succ", Church::succ, a[3]);
        runUnary("pred", Church::pred, a[1]);
        runUnary("pred", Church::pred, a[3]);
        runUnaryG("isEven", Church::isEven, a[0]);
        runUnaryG("isEven", Church::isEven, a[1]);
        runUnaryG("isEven", Church::isEven, a[2]);
        runUnaryG("isOdd", Church::isOdd, a[0]);
        runUnaryG("isOdd", Church::isOdd, a[1]);
        runUnaryG("isOdd", Church::isOdd, a[2]);
        runBinary("+", Church::add, a[0], a[2]);
        runBinary("+", Church::add, a[1], a[2]);
        runBinary("+", Church::add, a[3], a[6]);
        runBinary("-", Church::sub, a[4], a[0]);
        runBinary("-", Church::sub, a[2], a[2]);
        runBinary("-", Church::sub, a[9], a[6]);
        runBinary("*", Church::mul, a[0], a[2]);
        runBinary("*", Church::mul, a[1], a[2]);
        runBinary("*", Church::mul, a[3], a[6]);
    }
}
