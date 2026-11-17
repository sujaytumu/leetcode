package com.sujaytumu.leetcode.meta;

import static org.hamcrest.Matchers.hasItem;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.sujaytumu.leetcode.TestExecutorConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class MetaApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void exposesTheVocabularyTheUiRendersFrom() throws Exception {
        mvc.perform(get("/api/meta"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.difficulties.length()").value(3))
                .andExpect(jsonPath("$.difficulties[0].key").value("EASY"))
                .andExpect(jsonPath("$.difficulties[0].label").value("Easy"))
                .andExpect(jsonPath("$.statuses[*].key").value(hasItem("ATTEMPTED")))
                .andExpect(jsonPath("$.languages.length()").value(4))
                .andExpect(jsonPath("$.languages[?(@.key=='cpp')].label").value(hasItem("C++")))
                .andExpect(jsonPath("$.languages[?(@.key=='cpp')].editorMode").value(hasItem("cpp")))
                .andExpect(jsonPath("$.defaultLanguage").value("java"))
                .andExpect(jsonPath("$.pageSize").value(20));
    }
}
