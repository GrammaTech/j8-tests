import java.util.stream.Stream;

public class Stub {
    public static void main(String[] args)
    {
        // This tiny example causes analysis to reach code in the
        // java runtime with lambda's that have previously been
        // problematic for some tools
        Stream.Builder<Integer> builder = Stream.builder();
        for(int i=0;i<10;i++)
            builder.accept(Integer.valueOf(i));
        builder.build().forEach(System.out::println);
    }
}
