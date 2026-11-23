package com.sujaytumu.leetcode.playground;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.TestExecutorConfig;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class PlaygroundApiTest {

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private MockHttpServletRequestBuilder run(Map<String, Object> body) throws Exception {
        return post("/api/playground/run").header("X-Client-Id", UUID.randomUUID().toString())
                .contentType(MediaType.APPLICATION_JSON).content(json.writeValueAsString(body));
    }

    @Test
    void runsCodeAndReportsStatus() throws Exception {
        mvc.perform(run(Map.of("language", "python", "code", "print('hi')", "stdin", "")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("OK"))
                .andExpect(jsonPath("$.timeMs").value(10));

        mvc.perform(run(Map.of("language", "java", "code", TestExecutorConfig.COMPILE_ERROR)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("COMPILE_ERROR"))
                .andExpect(jsonPath("$.compileOutput").value("error: ';' expected"));

        mvc.perform(run(Map.of("language", "python", "code", TestExecutorConfig.RUNTIME_ERROR)))
                .andExpect(jsonPath("$.status").value("RUNTIME_ERROR"))
                .andExpect(jsonPath("$.stderr").value("IndexError: list index out of range"));
    }

    @Test
    void rejectsBadRequests() throws Exception {
        mvc.perform(run(Map.of("language", "python", "code", "   "))).andExpect(status().isBadRequest());
        mvc.perform(run(Map.of("language", "cobol", "code", "x"))).andExpect(status().isBadRequest());
        mvc.perform(post("/api/playground/run").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"language\":\"python\",\"code\":\"x\"}"))
                .andExpect(status().isBadRequest());
    }
}
