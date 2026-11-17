package com.sujaytumu.leetcode.export;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.TestExecutorConfig;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class ExportApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private Map<String, String> unzip(byte[] bytes) throws Exception {
        Map<String, String> files = new HashMap<>();
        try (ZipInputStream in = new ZipInputStream(new ByteArrayInputStream(bytes), StandardCharsets.UTF_8)) {
            for (ZipEntry entry = in.getNextEntry(); entry != null; entry = in.getNextEntry()) {
                files.put(entry.getName(), new String(in.readAllBytes(), StandardCharsets.UTF_8));
            }
        }
        return files;
    }

    @Test
    void emptyExportStillContainsAReadme() throws Exception {
        byte[] zip = mvc.perform(get("/api/export/solutions.zip").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsByteArray();
        Map<String, String> files = unzip(zip);
        assertEquals(1, files.size());
        assertTrue(files.get("README.md").contains("No accepted solutions yet"));
    }

    @Test
    void exportsTheLatestAcceptedSolutionPerProblem() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(post("/api/problems/two-sum/submit")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(
                                Map.of("language", "python", "code", TestExecutorConfig.SOLVE_TWO_SUM))))
                .andExpect(status().isOk());

        byte[] zip = mvc.perform(get("/api/export/solutions.zip").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsByteArray();
        Map<String, String> files = unzip(zip);

        String solutionPath = files.keySet().stream().filter(name -> name.endsWith("-two-sum/solution.py")).findFirst().orElseThrow();
        assertTrue(files.get(solutionPath).contains(TestExecutorConfig.SOLVE_TWO_SUM));
        assertTrue(files.containsKey(solutionPath.replace("solution.py", "README.md")));
        assertTrue(files.get("README.md").contains("Two Sum"));
    }
}
