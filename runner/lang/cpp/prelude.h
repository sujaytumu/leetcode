#pragma once
#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

// Minimal JSON reader/writer used by the generated test driver.
namespace __h {

struct J {
    // 0 null, 1 bool, 2 int, 3 double, 4 string, 5 array, 6 object
    int t = 0;
    bool b = false;
    long long i = 0;
    double d = 0;
    string s;
    vector<J> a;
    vector<string> keys;
    vector<J> vals;
    const J &get(const string &k) const {
        for (size_t x = 0; x < keys.size(); x++)
            if (keys[x] == k) return vals[x];
        throw runtime_error("missing key " + k);
    }
};

struct Parser {
    const string &s;
    size_t p = 0;
    explicit Parser(const string &str) : s(str) {}
    void ws() {
        while (p < s.size() && isspace((unsigned char)s[p])) p++;
    }
    string str() {
        string r;
        p++;
        while (s[p] != '"') {
            if (s[p] == '\\') {
                p++;
                char e = s[p];
                if (e == 'n') r += '\n';
                else if (e == 't') r += '\t';
                else if (e == 'r') r += '\r';
                else if (e == 'u') {
                    unsigned code = stoul(s.substr(p + 1, 4), nullptr, 16);
                    p += 4;
                    if (code < 128) r += (char)code;
                    else if (code < 2048) {
                        r += (char)(192 | (code >> 6));
                        r += (char)(128 | (code & 63));
                    } else {
                        r += (char)(224 | (code >> 12));
                        r += (char)(128 | ((code >> 6) & 63));
                        r += (char)(128 | (code & 63));
                    }
                } else r += e;
                p++;
            } else r += s[p++];
        }
        p++;
        return r;
    }
    J parse() {
        ws();
        J j;
        char c = s[p];
        if (c == '{') {
            j.t = 6;
            p++;
            ws();
            if (s[p] == '}') { p++; return j; }
            while (true) {
                ws();
                string k = str();
                ws();
                p++;  // ':'
                j.keys.push_back(k);
                j.vals.push_back(parse());
                ws();
                if (s[p] == ',') { p++; continue; }
                p++;
                break;
            }
        } else if (c == '[') {
            j.t = 5;
            p++;
            ws();
            if (s[p] == ']') { p++; return j; }
            while (true) {
                j.a.push_back(parse());
                ws();
                if (s[p] == ',') { p++; continue; }
                p++;
                break;
            }
        } else if (c == '"') {
            j.t = 4;
            j.s = str();
        } else if (s.compare(p, 4, "true") == 0) {
            j.t = 1; j.b = true; p += 4;
        } else if (s.compare(p, 5, "false") == 0) {
            j.t = 1; j.b = false; p += 5;
        } else if (s.compare(p, 4, "null") == 0) {
            j.t = 0; p += 4;
        } else {
            size_t st = p;
            bool fl = false;
            while (p < s.size() && (isdigit((unsigned char)s[p]) || s[p] == '-' || s[p] == '+' || s[p] == '.' || s[p] == 'e' || s[p] == 'E')) {
                if (s[p] == '.' || s[p] == 'e' || s[p] == 'E') fl = true;
                p++;
            }
            string num = s.substr(st, p - st);
            if (fl) { j.t = 3; j.d = stod(num); }
            else { j.t = 2; j.i = stoll(num); }
        }
        return j;
    }
};

// ---- JSON -> C++ ----
inline void cv(const J &j, int &x) { x = (int)(j.t == 3 ? (long long)j.d : j.i); }
inline void cv(const J &j, long long &x) { x = j.t == 3 ? (long long)j.d : j.i; }
inline void cv(const J &j, double &x) { x = j.t == 3 ? j.d : (double)j.i; }
inline void cv(const J &j, bool &x) { x = j.b; }
inline void cv(const J &j, string &x) { x = j.s; }
inline void cv(const J &j, char &x) { x = j.s.empty() ? '\0' : j.s[0]; }
inline void cv(const J &j, ListNode *&h) {
    ListNode dummy(0);
    ListNode *cur = &dummy;
    for (auto &e : j.a) {
        cur->next = new ListNode((int)e.i);
        cur = cur->next;
    }
    h = dummy.next;
}
inline void cv(const J &j, TreeNode *&root) {
    root = nullptr;
    if (j.a.empty() || j.a[0].t == 0) return;
    root = new TreeNode((int)j.a[0].i);
    queue<TreeNode *> q;
    q.push(root);
    size_t i = 1;
    while (!q.empty() && i < j.a.size()) {
        TreeNode *n = q.front();
        q.pop();
        if (i < j.a.size() && j.a[i].t != 0) { n->left = new TreeNode((int)j.a[i].i); q.push(n->left); }
        i++;
        if (i < j.a.size() && j.a[i].t != 0) { n->right = new TreeNode((int)j.a[i].i); q.push(n->right); }
        i++;
    }
}
template <class T>
void cv(const J &j, vector<T> &v) {
    v.clear();
    for (auto &e : j.a) {
        T x{};
        cv(e, x);
        v.push_back(x);
    }
}

// ---- C++ -> JSON ----
inline string esc(const string &s) {
    string r = "\"";
    for (unsigned char c : s) {
        if (c == '"') r += "\\\"";
        else if (c == '\\') r += "\\\\";
        else if (c == '\n') r += "\\n";
        else if (c == '\r') r += "\\r";
        else if (c == '\t') r += "\\t";
        else if (c < 32) { char b[8]; snprintf(b, 8, "\\u%04x", c); r += b; }
        else r += (char)c;
    }
    return r + "\"";
}
inline string sr(int x) { return to_string(x); }
inline string sr(long long x) { return to_string(x); }
inline string sr(double x) {
    if (std::isnan(x) || std::isinf(x)) return "null";
    ostringstream o;
    o << setprecision(15) << x;
    return o.str();
}
inline string sr(bool x) { return x ? "true" : "false"; }
inline string sr(char c) { return esc(string(1, c)); }
inline string sr(const string &s) { return esc(s); }
inline string sr(ListNode *h) {
    string r = "[";
    bool first = true;
    long long guard = 0;
    while (h && guard++ < 2000000) {
        if (!first) r += ",";
        first = false;
        r += to_string(h->val);
        h = h->next;
    }
    return r + "]";
}
inline string sr(TreeNode *root) {
    if (!root) return "[]";
    vector<string> out;
    queue<TreeNode *> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode *n = q.front();
        q.pop();
        if (!n) { out.push_back("null"); continue; }
        out.push_back(to_string(n->val));
        q.push(n->left);
        q.push(n->right);
    }
    while (!out.empty() && out.back() == "null") out.pop_back();
    string r = "[";
    for (size_t i = 0; i < out.size(); i++) {
        if (i) r += ",";
        r += out[i];
    }
    return r + "]";
}
template <class T>
string sr(const vector<T> &v) {
    string r = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) r += ",";
        r += sr(v[i]);
    }
    return r + "]";
}

}  // namespace __h
