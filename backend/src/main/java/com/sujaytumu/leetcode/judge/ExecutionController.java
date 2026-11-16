package com.sujaytumu.leetcode.judge;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/execution")
public class ExecutionController {

    private final CodeExecutor executor;

    public ExecutionController(CodeExecutor executor) {
        this.executor = executor;
    }

    @GetMapping("/status")
    public CodeExecutor.Health status() {
        return executor.health();
    }
}
