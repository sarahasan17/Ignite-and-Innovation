@Test
void testGetStatusWithInvalidAppFlowTypeId() throws Exception {
    String invalidAppFlowTypeId = "abc"; // Invalid input

    mockMvc.perform(get("/api/advancedSearch/status/{appFlwTypld}", invalidAppFlowTypeId))
            .andExpect(status().isBadRequest()) // Expecting 400 Bad Request
            .andExpect(result -> assertTrue(result.getResolvedException() instanceof IllegalArgumentException))
            .andExpect(result -> assertEquals("Invalid App Flow Type Id", result.getResolvedException().getMessage()));
}
