public class Hello {
    public static void main(String[] args) {
        foo(3,4);
    }
    
    public static void foo(int x, int y) {
        bar(1 + y);
    }
    public static void bar(int x) {
        System.exit(x);
    }
    
    
}
