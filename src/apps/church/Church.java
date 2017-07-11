/*
 * This material is based upon work supported by the United States Air Force
 * and DARPA under Contract No. FA8750-15-C-0082. Any opinions, findings and
 * conclusions or recommendations expressed in this material are those of
 * the author(s) and do not necessarily reflect the views of the United
 * States Air Force and DARPA.
 *
 *
 * Copyright 2017 GrammaTech, Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * If you are interested in making contributions, then please contact
 * info@grammatech.com
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
