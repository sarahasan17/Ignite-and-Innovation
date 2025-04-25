  @Test
    void testGetAllADUsers_SuccessfulExecution() throws Exception {
        // Given
        String searchFilter = "(memberOf=CN=groupName,dc=example,dc=com)";
        int pageSize = 100;
        List<LDAPUserInfoDto> expectedUsers = Arrays.asList(new LDAPUserInfoDto(), new LDAPUserInfoDto());

        // Mocking the LdapTemplate behavior
        when(ldapTemplate.search(
            any(), eq(searchFilter), any(SearchControls.class), any(), eq(processor)
        )).thenReturn(expectedUsers);

        // When
        List<LDAPUserInfoDto> result = ldapGroupsServiceImpl.getAllADUsers(searchFilter, pageSize);

        // Then
        assertEquals(2, result.size());
        verify(ldapTemplate, times(1)).search(any(), eq(searchFilter), any(SearchControls.class), any(), eq(processor));
    }


    @Test
    void testGetAllADUsers_ExceptionHandling() throws Exception {
        // Given
        String searchFilter = "(memberOf=CN=groupName,dc=example,dc=com)";
        int pageSize = 100;

        // Mocking the LdapTemplate behavior
        when(ldapTemplate.getContextSource()).thenReturn(mock(SingleContextSource.class));
        
        // Simulate an exception during search
        when(ldapTemplate.getContextSource().getOperations().search(
            any(), eq(searchFilter), any(SearchControls.class), any(), eq(processor)
        )).thenThrow(new RuntimeException("Test Exception"));

        // When
        List<LDAPUserInfoDto> result = ldapGroupsServiceImpl.getAllADUsers(searchFilter, pageSize);

        // Then
        assertNotNull(result);
        assertTrue(result.isEmpty()); // Expecting an empty result since an exception was thrown
        verify(logger, times(1)).error(contains("Exception during Getting AD Users AD-GroupName"), any(Exception.class));
    }

    @Test
    void testDoWhileLoop_EmptyResults() throws Exception {
        // Given
        String searchFilter = "(memberOf=CN=groupName,dc=example,dc=com)";
        int pageSize = 100;
        List<LDAPUserInfoDto> emptyList = Arrays.asList();

        // Mocking the LdapTemplate behavior for empty results
        when(ldapTemplate.getContextSource()).thenReturn(mock(SingleContextSource.class));
        when(ldapTemplate.getContextSource().getOperations().search(
            any(), eq(searchFilter), any(SearchControls.class), any(), eq(processor)
        )).thenReturn(emptyList);

        // When
        List<LDAPUserInfoDto> result = ldapGroupsServiceImpl.getAllADUsers(searchFilter, pageSize);

        // Then
        assertTrue(result.isEmpty());
        verify(ldapTemplate, times(1)).getContextSource();
    }
}
