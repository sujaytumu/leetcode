package com.sujaytumu.leetcode.judge;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import com.sujaytumu.leetcode.judge.CodeExecutor.ExecutionResult;
import com.sujaytumu.leetcode.judge.CodeExecutor.Status;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** Exercises the built-in runner against the real toolchain; skipped on machines without g++ / python3. */
class LocalCodeExecutorTest {

    private static boolean has(String tool) {
        for (String dir : System.getenv().getOrDefault("PATH", "").split(":")) {
            if (!dir.isEmpty() && Files.isExecutable(Path.of(dir, tool))) {
                return true;
            }
        }
        return false;
    }

    private final LocalCodeExecutor executor = new LocalCodeExecutor(2.0, "");

    @Test
    void runsCppAndReadsStdin() {
        assumeTrue(has("g++"));
        ExecutionResult r = executor.execute(Language.CPP,
                "#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b;}", "3 4\n");
        assertEquals(Status.OK, r.status());
        assertEquals("7", r.stdout().trim());
    }

    @Test
    void reportsCompileErrorsAndRuntimeErrors() {
        assumeTrue(has("g++"));
        assertEquals(Status.COMPILE_ERROR, executor.execute(Language.CPP, "int main(){ return x; }", "").status());
        assertEquals(Status.RUNTIME_ERROR, executor.execute(Language.CPP, "int main(){ return 3; }", "").status());
    }

    @Test
    void stopsRunawayPrograms() {
        assumeTrue(has("g++"));
        assertEquals(Status.TIME_LIMIT_EXCEEDED, executor.execute(Language.CPP, "int main(){ while(1){} }", "").status());
    }

    @Test
    void runsPython() {
        assumeTrue(has("python3"));
        ExecutionResult r = executor.execute(Language.PYTHON, "print(sum(map(int, input().split())))", "5 6\n");
        assertEquals(Status.OK, r.status());
        assertEquals("11", r.stdout().trim());
    }

    @Test
    void doesNotLeakServerEnvironment() {
        assumeTrue(has("python3"));
        ExecutionResult r = executor.execute(Language.PYTHON, "import os\nprint(len(os.environ))", "");
        assertTrue(Integer.parseInt(r.stdout().trim()) <= 8, "child should only see a minimal environment");
    }
}
