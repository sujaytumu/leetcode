import java.util.*;

// Minimal JSON reader/writer used by the generated test driver.
public class Json {
    private final String s;
    private int p = 0;

    private Json(String s) { this.s = s; }

    public static Object parse(String s) { return new Json(s).value(); }

    private void ws() {
        while (p < s.length() && Character.isWhitespace(s.charAt(p))) p++;
    }

    private String str() {
        StringBuilder r = new StringBuilder();
        p++;
        while (s.charAt(p) != '"') {
            char c = s.charAt(p);
            if (c == '\\') {
                p++;
                char e = s.charAt(p);
                if (e == 'n') r.append('\n');
                else if (e == 't') r.append('\t');
                else if (e == 'r') r.append('\r');
                else if (e == 'u') {
                    r.append((char) Integer.parseInt(s.substring(p + 1, p + 5), 16));
                    p += 4;
                } else r.append(e);
                p++;
            } else {
                r.append(c);
                p++;
            }
        }
        p++;
        return r.toString();
    }

    private Object value() {
        ws();
        char c = s.charAt(p);
        if (c == '{') {
            Map<String, Object> m = new LinkedHashMap<>();
            p++;
            ws();
            if (s.charAt(p) == '}') { p++; return m; }
            while (true) {
                ws();
                String k = str();
                ws();
                p++;
                m.put(k, value());
                ws();
                if (s.charAt(p) == ',') { p++; continue; }
                p++;
                break;
            }
            return m;
        }
        if (c == '[') {
            List<Object> l = new ArrayList<>();
            p++;
            ws();
            if (s.charAt(p) == ']') { p++; return l; }
            while (true) {
                l.add(value());
                ws();
                if (s.charAt(p) == ',') { p++; continue; }
                p++;
                break;
            }
            return l;
        }
        if (c == '"') return str();
        if (s.startsWith("true", p)) { p += 4; return Boolean.TRUE; }
        if (s.startsWith("false", p)) { p += 5; return Boolean.FALSE; }
        if (s.startsWith("null", p)) { p += 4; return null; }
        int st = p;
        boolean fl = false;
        while (p < s.length() && "0123456789+-.eE".indexOf(s.charAt(p)) >= 0) {
            char d = s.charAt(p);
            if (d == '.' || d == 'e' || d == 'E') fl = true;
            p++;
        }
        String num = s.substring(st, p);
        return fl ? (Object) Double.valueOf(num) : (Object) Long.valueOf(num);
    }

    // ---------- JSON -> Java ----------
    private static List<?> L(Object o) { return (List<?>) o; }
    public static int iv(Object o) { return ((Number) o).intValue(); }
    public static long lv(Object o) { return ((Number) o).longValue(); }
    public static double dv(Object o) { return ((Number) o).doubleValue(); }
    public static char cv(Object o) { return ((String) o).charAt(0); }

    public static int[] ia(Object o) { List<?> l = L(o); int[] r = new int[l.size()]; for (int i = 0; i < r.length; i++) r[i] = iv(l.get(i)); return r; }
    public static long[] la(Object o) { List<?> l = L(o); long[] r = new long[l.size()]; for (int i = 0; i < r.length; i++) r[i] = lv(l.get(i)); return r; }
    public static double[] da(Object o) { List<?> l = L(o); double[] r = new double[l.size()]; for (int i = 0; i < r.length; i++) r[i] = dv(l.get(i)); return r; }
    public static boolean[] ba(Object o) { List<?> l = L(o); boolean[] r = new boolean[l.size()]; for (int i = 0; i < r.length; i++) r[i] = (Boolean) l.get(i); return r; }
    public static String[] sa(Object o) { List<?> l = L(o); String[] r = new String[l.size()]; for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i); return r; }
    public static char[] ca(Object o) { List<?> l = L(o); char[] r = new char[l.size()]; for (int i = 0; i < r.length; i++) r[i] = cv(l.get(i)); return r; }

    public static int[][] iaa(Object o) { List<?> l = L(o); int[][] r = new int[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = ia(l.get(i)); return r; }
    public static long[][] laa(Object o) { List<?> l = L(o); long[][] r = new long[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = la(l.get(i)); return r; }
    public static double[][] daa(Object o) { List<?> l = L(o); double[][] r = new double[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = da(l.get(i)); return r; }
    public static boolean[][] baa(Object o) { List<?> l = L(o); boolean[][] r = new boolean[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = ba(l.get(i)); return r; }
    public static String[][] saa(Object o) { List<?> l = L(o); String[][] r = new String[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = sa(l.get(i)); return r; }
    public static char[][] caa(Object o) { List<?> l = L(o); char[][] r = new char[l.size()][]; for (int i = 0; i < r.length; i++) r[i] = ca(l.get(i)); return r; }

    public static ListNode ln(Object o) {
        ListNode dummy = new ListNode(0), cur = dummy;
        for (Object e : L(o)) { cur.next = new ListNode(iv(e)); cur = cur.next; }
        return dummy.next;
    }

    public static TreeNode tn(Object o) {
        List<?> a = L(o);
        if (a.isEmpty() || a.get(0) == null) return null;
        TreeNode root = new TreeNode(iv(a.get(0)));
        ArrayDeque<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        int i = 1;
        while (!q.isEmpty() && i < a.size()) {
            TreeNode n = q.poll();
            if (i < a.size() && a.get(i) != null) { n.left = new TreeNode(iv(a.get(i))); q.add(n.left); }
            i++;
            if (i < a.size() && a.get(i) != null) { n.right = new TreeNode(iv(a.get(i))); q.add(n.right); }
            i++;
        }
        return root;
    }

    // ---------- Java -> JSON ----------
    public static String esc(String s) {
        StringBuilder r = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '"') r.append("\\\"");
            else if (c == '\\') r.append("\\\\");
            else if (c == '\n') r.append("\\n");
            else if (c == '\r') r.append("\\r");
            else if (c == '\t') r.append("\\t");
            else if (c < 32) r.append(String.format("\\u%04x", (int) c));
            else r.append(c);
        }
        return r.append('"').toString();
    }

    private static String join(List<String> parts) { return "[" + String.join(",", parts) + "]"; }

    // Typed entry points: a null ListNode/TreeNode means an empty list/tree, not JSON null.
    public static String serLn(ListNode h) { return h == null ? "[]" : ser(h); }
    public static String serTn(TreeNode t) { return t == null ? "[]" : ser(t); }

    public static String ser(Object o) {
        if (o == null) return "null";
        if (o instanceof String) return esc((String) o);
        if (o instanceof Character) return esc(String.valueOf(o));
        if (o instanceof Boolean || o instanceof Integer || o instanceof Long) return o.toString();
        if (o instanceof Double || o instanceof Float) {
            double d = ((Number) o).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) return "null";
            return String.valueOf(d);
        }
        List<String> parts = new ArrayList<>();
        if (o instanceof int[]) { for (int x : (int[]) o) parts.add(String.valueOf(x)); return join(parts); }
        if (o instanceof long[]) { for (long x : (long[]) o) parts.add(String.valueOf(x)); return join(parts); }
        if (o instanceof double[]) { for (double x : (double[]) o) parts.add(ser(x)); return join(parts); }
        if (o instanceof boolean[]) { for (boolean x : (boolean[]) o) parts.add(String.valueOf(x)); return join(parts); }
        if (o instanceof char[]) { for (char x : (char[]) o) parts.add(esc(String.valueOf(x))); return join(parts); }
        if (o instanceof Object[]) { for (Object x : (Object[]) o) parts.add(ser(x)); return join(parts); }
        if (o instanceof List) { for (Object x : (List<?>) o) parts.add(ser(x)); return join(parts); }
        if (o instanceof ListNode) {
            ListNode h = (ListNode) o;
            long guard = 0;
            while (h != null && guard++ < 2000000) { parts.add(String.valueOf(h.val)); h = h.next; }
            return join(parts);
        }
        if (o instanceof TreeNode) {
            ArrayDeque<TreeNode> q = new ArrayDeque<>();
            List<String> out = new ArrayList<>();
            q.add((TreeNode) o);
            while (!q.isEmpty()) {
                TreeNode n = q.poll();
                if (n == null) { out.add("null"); continue; }
                out.add(String.valueOf(n.val));
                q.add(n.left);
                q.add(n.right);
            }
            while (!out.isEmpty() && out.get(out.size() - 1).equals("null")) out.remove(out.size() - 1);
            return join(out);
        }
        throw new RuntimeException("Cannot serialize " + o.getClass().getName());
    }
}
